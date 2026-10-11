"""Stage 카드로 실제 CLI 인계를 비교하며 원본 결과를 덮어쓰지 않습니다."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

import native
import prepare as P

ROOT = Path(__file__).resolve().parent


def manifest(root: Path) -> dict:
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob("*")) if path.is_file() and "__pycache__" not in path.parts}


async def main() -> None:
    out = ROOT / "runs"
    if out.exists():
        raise FileExistsError("이미 시작한 실험을 덮어쓰지 않습니다.")
    P.H.save(out / "manifest.json", {
        "started_at": datetime.now(timezone.utc).isoformat(), "cases": P.H.CASES, "goals": P.GOALS,
        "conditions": ["stage_card", "stage_card_observation"], "planned_runs": 8,
        "source_hashes": {path.name: native.digest(path.read_text()) for path in (ROOT / "run.py", ROOT / "native.py", ROOT / "prepare.py")},
        "stage_source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=P.REPO, text=True).strip(),
        "stage_setup_hashes": {str(path.relative_to(P.REPO)): native.digest(path.read_text()) for path in (
            P.REPO / "stage/scripts/init_stage.py", P.REPO / "stage/skills/stage-work/register_work.py")},
        "cli_versions": {host: subprocess.check_output([host, "--version"], text=True).strip() for host in ("claude", "codex")},
        "parallelism": 1, "claude_max_reported_cost_usd": 4, "codex_cost_usd": None})
    fixtures = {row["id"]: row for row in json.loads((P.H.PREVIOUS / "fixtures.json").read_text())}
    preflight = []
    for case in P.H.CASES:
        with tempfile.TemporaryDirectory(prefix="stage-followup-preflight-") as directory:
            root = Path(directory)
            P.H.setup(root, case, fixtures[case["id"]]["versions"]["before"]["files"][case["target"]])
            bad = P.check(root, case)
            (root / case["target"]).write_text(fixtures[case["id"]]["versions"]["after"]["files"][case["target"]])
            good = P.check(root, case)
            preflight.append({"case": case["id"], "before": bad, "known_after": good})
            P.H.save(out / "preflight.json", preflight)
            print(json.dumps({"preflight": case["id"], "before": bad["returncode"], "known_after": good["returncode"]}), flush=True)
            if bad["returncode"] != 1 or good["returncode"] != 0:
                raise RuntimeError("공개할 전체 검사의 실패와 성공을 확인하지 못했습니다.")
    for case in P.H.CASES:
        for starter, receiver in (("claude", "codex"), ("codex", "claude")):
            with tempfile.TemporaryDirectory(prefix="stage-followup-") as directory:
                temp = Path(directory)
                source = temp / "source"
                source.mkdir()
                setup = P.setup(source, case, starter, receiver)
                lane = f"{case['id']}--{starter}-to-{receiver}"
                P.H.save(out / lane / "setup.json", setup)
                conditions = ["stage_card", "stage_card_observation"]
                if starter == "codex":
                    conditions.reverse()
                for condition in conditions:
                    cloned = time.perf_counter()
                    root = temp / condition
                    shutil.copytree(source, root)
                    clone_seconds = time.perf_counter() - cloned
                    started = time.perf_counter()
                    prepared = P.add_observation(root, case) if condition.endswith("observation") else {
                        "seconds": 0, "preparation_file_reads": 0, "card": (root / P.CARD).read_text()}
                    before = manifest(root)
                    prompt = native.RULES + "\n작업 카드를 읽고 이 임시 프로젝트의 일을 이어서 끝내세요: " + P.CARD
                    print(json.dumps({"start": lane, "condition": condition, "receiver": receiver}), flush=True)
                    cli = await native.invoke(receiver, root, prompt)
                    P.H.save(out / lane / condition / "cli.json", cli)
                    verification = P.check(root, case)
                    after = manifest(root)
                    changed = sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))
                    outside = [name for name in changed if name != case["target"]]
                    content = (root / case["target"]).read_text()
                    note_preserved = case["id"] != "retrospective_owner_conflict" or P.H.NOTE in content
                    verified = verification["returncode"] == 0 and not outside and note_preserved
                    record = {"id": lane + "--" + condition, "case": case["id"], "receiver": receiver,
                              "condition": condition, "clone_seconds": clone_seconds, "preparation": prepared,
                              "initial_manifest": before, "final_manifest": after, "changed_paths": changed,
                              "outside_target_changes": outside, "note_preserved": note_preserved,
                              "verification": verification, "verified": verified,
                              "declared_complete": (cli.get("answer") or {}).get("complete"),
                              "success": verified and (cli.get("answer") or {}).get("complete") is True,
                              "seconds_including_verification": time.perf_counter() - started,
                              "final_source": content}
                    P.H.save(out / lane / condition / "result.json", record)
                    print(json.dumps({"finished": record["id"], "verified": verified,
                                      "declared_complete": record["declared_complete"], "cli_error": cli["error"]}), flush=True)
                    if cli["error"]:
                        raise RuntimeError("CLI 오류를 보존하고 나머지 호출을 중단했습니다.")


if __name__ == "__main__":
    asyncio.run(main())

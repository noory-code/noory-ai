"""Codex 서버 오류와 독립된 Claude 인계 비교 두 건을 마칩니다."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
import shutil
import tempfile
import time

import native
import prepare as P
import retry as R
import run as N


async def main() -> None:
    manifest_path = R.OUT / "claude-continuation-manifest.json"
    if manifest_path.exists():
        raise FileExistsError("기존 Claude 인계 기록을 덮어쓰지 않습니다.")
    R.save(manifest_path, {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": R.digest(Path(__file__)), "planned_calls": 2,
        "parent_manifest_sha256": R.digest(R.OUT / "manifest.json"),
        "reason": "Codex 호출을 중단하고, 이미 계획한 Claude 수신 두 조건을 독립적으로 수행합니다.",
        "conditions": ["stage_card_observation", "stage_card"],
        "claude_max_reported_cost_usd": 2.0})
    case = next(case for case in P.H.CASES if case["id"] == "retrospective_owner_conflict")
    lane = f"{case['id']}--codex-to-claude"
    with tempfile.TemporaryDirectory(prefix="stage-followup-retry-claude-") as directory:
        temp = Path(directory)
        source = temp / "source"
        source.mkdir()
        R.save(R.OUT / "runs" / lane / "setup.json", P.setup(source, case, "codex", "claude"))
        for condition in ("stage_card_observation", "stage_card"):
            cloned = time.perf_counter()
            root = temp / condition
            shutil.copytree(source, root)
            clone_seconds = time.perf_counter() - cloned
            started = time.perf_counter()
            prepared = P.add_observation(root, case) if condition.endswith("observation") else {
                "seconds": 0, "preparation_file_reads": 0, "card": (root / P.CARD).read_text()}
            before = N.manifest(root)
            prompt = native.RULES + "\n작업 카드를 읽고 이 임시 프로젝트의 일을 이어서 끝내세요: " + P.CARD
            print(f"start: {condition}", flush=True)
            cli = await native.invoke("claude", root, prompt)
            R.save(R.OUT / "runs" / lane / condition / "cli.json", cli)
            verification = P.check(root, case)
            after = N.manifest(root)
            changed = sorted(name for name in before.keys() | after.keys()
                             if before.get(name) != after.get(name))
            outside = [name for name in changed if name != case["target"]]
            content = (root / case["target"]).read_text()
            note_preserved = P.H.NOTE in content
            verified = verification["returncode"] == 0 and not outside and note_preserved
            record = {"id": lane + "--" + condition, "case": case["id"], "receiver": "claude",
                      "condition": condition, "clone_seconds": clone_seconds,
                      "preparation": prepared, "initial_manifest": before, "final_manifest": after,
                      "changed_paths": changed, "outside_target_changes": outside,
                      "note_preserved": note_preserved, "verification": verification,
                      "verified": verified, "declared_complete": (cli.get("answer") or {}).get("complete"),
                      "success": verified and (cli.get("answer") or {}).get("complete") is True,
                      "seconds_including_verification": time.perf_counter() - started,
                      "final_source": content, "retries_failed_attempt": False}
            R.save(R.OUT / "runs" / lane / condition / "result.json", record)
            print(f"finished: {condition}; verified={verified}; error={cli['error']}", flush=True)
            if cli["error"]:
                raise RuntimeError("Claude 실행 오류를 보존하고 추가 호출을 멈춥니다.")


if __name__ == "__main__":
    asyncio.run(main())

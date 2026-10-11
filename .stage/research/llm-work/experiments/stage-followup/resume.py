"""앞선 결과를 보존하며 Codex에서 남은 비교만 이어갑니다."""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

import native
import prepare as P
import retry as R
import retry_continue as C
import run as N


async def handoff() -> None:
    case = next(case for case in P.H.CASES if case["id"] == "retrospective_owner_conflict")
    lane = f"{case['id']}--claude-to-codex"
    with tempfile.TemporaryDirectory(prefix="stage-followup-resume-") as directory:
        temp = Path(directory)
        source = temp / "source"
        source.mkdir()
        setup = P.setup(source, case, "claude", "codex")
        previous = R.read(R.ROOT / "runs" / lane / "setup.json")
        for key in ("seed_sha256", "target_sha256", "card"):
            if setup[key] != previous[key]:
                raise ValueError(f"인계 초기 자료가 달라졌습니다: {key}")
        R.save(R.OUT / "runs" / lane / "setup.json", setup)
        for condition in ("stage_card", "stage_card_observation"):
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
            cli = await native.invoke("codex", root, prompt)
            R.save(R.OUT / "runs" / lane / condition / "cli.json", cli)
            verification = P.check(root, case)
            after = N.manifest(root)
            changed = sorted(name for name in before.keys() | after.keys()
                             if before.get(name) != after.get(name))
            outside = [name for name in changed if name != case["target"]]
            content = (root / case["target"]).read_text()
            note_preserved = P.H.NOTE in content
            verified = verification["returncode"] == 0 and not outside and note_preserved
            record = {"id": lane + "--" + condition, "case": case["id"], "receiver": "codex",
                      "condition": condition, "clone_seconds": clone_seconds,
                      "preparation": prepared, "initial_manifest": before, "final_manifest": after,
                      "changed_paths": changed, "outside_target_changes": outside,
                      "note_preserved": note_preserved, "verification": verification,
                      "verified": verified, "declared_complete": (cli.get("answer") or {}).get("complete"),
                      "success": verified and (cli.get("answer") or {}).get("complete") is True,
                      "seconds_including_verification": time.perf_counter() - started,
                      "final_source": content, "retries_failed_attempt": condition == "stage_card"}
            R.save(R.OUT / "runs" / lane / condition / "result.json", record)
            print(f"finished: {condition}; verified={verified}; error={cli['error']}", flush=True)
            if cli["error"]:
                raise RuntimeError("인계 호출 오류를 보존하고 추가 호출을 멈춥니다.")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="retry-2")
    args = parser.parse_args()
    if Path(args.output).name != args.output:
        raise ValueError("결과 폴더 이름만 입력하세요.")
    R.OUT = R.ROOT / args.output
    if R.OUT.exists():
        raise FileExistsError("이전에 저장한 결과를 덮어쓰지 않습니다.")
    parent = R.read(R.ROOT / "retry-1/manifest.json")
    continuation = R.read(R.ROOT / "retry-1/continuation-manifest.json")
    sources = dict(parent["source_hashes"])
    sources.update({str((R.ROOT / "retry_continue.py").relative_to(P.REPO)):
                    continuation["source_sha256"]})
    for name, value in sources.items():
        if R.digest(P.REPO / name) != value:
            raise ValueError(f"이전 실행기가 달라졌습니다: {name}")
    sources[str(Path(__file__).relative_to(P.REPO))] = R.digest(Path(__file__))
    originals = sorted(path for folder in ("runs", "criteria-runs", "freshness-runs", "retry-1")
                       for path in (R.ROOT / folder).rglob("*.json"))
    manifest = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "reason": "사용자가 잠깐 발생한 장애였다고 설명하고 기존 연구를 계속하도록 요청했습니다.",
        "source_hashes": sources,
        "original_record_hashes": {str(path.relative_to(R.ROOT)): R.digest(path)
                                   for path in originals},
        "cli_versions": {host: subprocess.check_output([host, "--version"], text=True).strip()
                         for host in ("claude", "codex")},
        "stage_source_revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=P.REPO, text=True).strip(),
        "previous_cli_versions": parent["cli_versions"],
        "amended_extraction_prompt": continuation["amended_extraction_prompt"],
        "freshness_manifest": parent["freshness_manifest"],
        "freshness_schedule": parent["freshness_schedule"],
        "planned_calls": {"criteria_extraction": 1, "criteria_decisions": 12,
                          "freshness": 6, "native_handoff": 2},
        "parallelism": 1, "codex_model_requested": "CLI default, unchanged command",
        "claude_calls": 0, "codex_cost_usd": None,
        "limits": ["첫 추출과 달리 출처 단위를 명시한 조건입니다.",
                   "기존 실패를 대체하지 않고 별도 시점의 결과로 기록합니다."]}
    R.save(R.OUT / "manifest.json", manifest)
    status = {"completed_phases": [], "error": None}
    try:
        for phase, task in (
            ("criteria_single_source", lambda: C.clarified_criteria(manifest["amended_extraction_prompt"])),
            ("freshness", lambda: R.freshness(manifest)), ("native_handoff", handoff)):
            status["phase"] = phase
            await task()
            status["completed_phases"].append(phase)
            R.save(R.OUT / "status.json", status)
    except Exception as error:
        status["error"] = str(error)
        raise
    finally:
        status["stopped_at"] = datetime.now(timezone.utc).isoformat()
        R.save(R.OUT / "status.json", status)


if __name__ == "__main__":
    asyncio.run(main())

"""CLI 업데이트를 기록하고 성공한 판단을 보존하며 남은 비교를 실행합니다."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

import continue_pending as P
import criteria as C
import resume
import retry as R

ROOT = Path(__file__).resolve().parent


async def main() -> None:
    R.OUT = ROOT / "after-update"
    if R.OUT.exists():
        raise FileExistsError("업데이트 후의 기존 실행 기록을 덮어쓰지 않습니다.")
    manifest, planned = P.plan()
    completed = {}
    for path in sorted((ROOT / "retry-3/choices").glob("*/*.json")):
        row = R.read(path)
        if not row["cli"]["error"]:
            completed[row["id"]] = (path, row)
    requests = []
    for entry in planned:
        if entry["id"] in completed:
            path, row = completed[entry["id"]]
            if row["cli"]["prompt"] != entry["prompt"]:
                raise ValueError("보존할 판단의 입력이 다릅니다.")
            manifest["retained_successes"].append(str(path.relative_to(ROOT)))
        else:
            requests.append(entry)
    manifest["source_hashes"][str(Path(__file__).relative_to(R.P.REPO))] = R.digest(Path(__file__))
    manifest["previous_record_hashes"].update({str(path.relative_to(ROOT)): R.digest(path)
        for path in sorted((ROOT / "retry-3").rglob("*.json"))})
    manifest.update({"requests": requests, "planned_choice_requests": len(requests),
                     "cli_versions": {host: subprocess.check_output([host, "--version"], text=True).strip()
                                      for host in ("claude", "codex")},
                     "previous_cli_versions": R.read(ROOT / "retry-2/manifest.json")["cli_versions"],
                     "reason": "사용자가 Codex를 업데이트한 뒤 연구를 이어갑니다.",
                     "codex_model_requested": "CLI default, unchanged command"})
    manifest["limits"].append("CLI 버전이 달라 업데이트 전후 시간을 같은 환경의 값으로 비교하지 않습니다.")
    R.save(R.OUT / "manifest.json", manifest)
    status = {"completed_requests": [], "capacity_errors": 0, "error": None}
    try:
        for entry in requests:
            status["request"] = entry["id"]
            for attempt in range(1, 3):
                result = await C.CLI.invoke("codex", entry["prompt"])
                matches = (bool(result["answer"] and C.CLI.matches(result["answer"], entry["expected"]))
                           if entry["kind"] == "criteria" and not result["error"] else None)
                row = {key: value for key, value in entry.items() if key not in {"prompt", "expected"}}
                row.update({"host": "codex", "attempt": attempt, "cli": result, "matches": matches})
                R.save(R.OUT / "choices" / entry["id"] / f"attempt-{attempt}.json", row)
                print(json.dumps({"id": entry["id"], "attempt": attempt,
                                  "matches": matches, "error": result["error"]}), flush=True)
                if not result["error"]:
                    status["completed_requests"].append(entry["id"])
                    break
                capacity = "Selected model is at capacity" in json.dumps(result["events"])
                if capacity:
                    status["capacity_errors"] += 1
                if not capacity or attempt == 2 or status["capacity_errors"] >= 6:
                    raise RuntimeError("정한 재시도 한도에서 응답을 받지 못했습니다.")
                R.save(R.OUT / "status.json", status)
                print("서버 혼잡 뒤 30초를 기다립니다.", flush=True)
                await asyncio.sleep(30)
            R.save(R.OUT / "status.json", status)
            await asyncio.sleep(5)
        status["phase"] = "native_handoff"
        R.save(R.OUT / "status.json", status)
        await resume.handoff()
        status["completed_requests"].extend(["native--stage_card", "native--stage_card_observation"])
    except Exception as error:
        status["error"] = str(error)
        raise
    finally:
        status["stopped_at"] = datetime.now(timezone.utc).isoformat()
        R.save(R.OUT / "status.json", status)


if __name__ == "__main__":
    asyncio.run(main())

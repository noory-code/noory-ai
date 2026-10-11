"""관찰 시점을 혼동했던 공개 입력 한 개를 그대로 재시험합니다."""

from __future__ import annotations

import asyncio
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("choice_cli", ROOT.parent / "ideas-lab/run_models.py")
assert SPEC and SPEC.loader
CLI = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CLI)


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", choices=("both", "claude", "codex"), default="both")
    args = parser.parse_args()
    hosts = ("claude", "codex") if args.host == "both" else (args.host,)
    out = ROOT / "freshness-runs"
    if out.exists():
        raise FileExistsError("기존 재시험을 덮어쓰지 않습니다.")
    source = ROOT.parent / "cross-session/runs/roadmap_repeated_criteria--codex-to-claude/state_packet/call-3.json"
    original = json.loads(source.read_text())
    prefix, payload = original["prompt"].rsplit("\n", 1)
    changed = json.loads(payload)
    previous = changed["handoff"].pop("current_files")
    changed["handoff"]["files_observed_before_receiver_step_1"] = previous
    changed["handoff"]["observation_validity"] = (
        "이 파일은 인계 시점에 읽은 과거 관찰입니다. 이후 history의 성공한 수정 결과와 그 뒤 검사 결과가 더 최신입니다. "
        "인계 파일의 해시가 수정 후 해시와 다른 것 자체는 모순이 아닙니다. 실제 충돌이나 근거 부족이 있으면 확인하세요.")
    prompts = {"original": original["prompt"],
               "time_explicit": prefix + "\n" + json.dumps(changed, ensure_ascii=False)}
    schedule = [(host, condition, repeat) for host in hosts
                for condition in prompts for repeat in range(1, 4)]
    random.Random(2026100517).shuffle(schedule)
    save(out / "manifest.json", {"started_at": datetime.now(timezone.utc).isoformat(),
        "source_record": str(source.relative_to(ROOT.parent)), "source_record_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "prior_cli_sha256": hashlib.sha256((ROOT.parent / "ideas-lab/run_models.py").read_bytes()).hexdigest(),
        "prompts": prompts, "schedule": schedule, "planned_calls": len(schedule),
        "original_both_host_plan": 12, "selected_hosts": hosts,
        "scope": "One selected historical input, three repetitions; extra reading is not scored as an incorrect answer.",
        "claude_max_reported_cost_usd": 1.2})
    for host, condition, repeat in schedule:
        result = await CLI.invoke(host, prompts[condition])
        row = {"host": host, "condition": condition, "repeat": repeat, "cli": result}
        save(out / f"{host}--{condition}--r{repeat}.json", row)
        print(json.dumps({"host": host, "condition": condition, "repeat": repeat,
                          "action": (result["answer"] or {}).get("action"), "error": result["error"]}), flush=True)
        if result["error"]:
            raise RuntimeError("재시험 호출 오류를 보존했습니다.")


if __name__ == "__main__":
    asyncio.run(main())

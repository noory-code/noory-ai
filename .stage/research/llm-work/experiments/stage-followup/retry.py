"""중단된 비교를 같은 실행기로 이어가고 재시도 기록을 따로 남깁니다."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import shutil
import subprocess
import tempfile
import time

import criteria as C
import native
import prepare as P
import run as N

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "retry-1"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: object) -> None:
    C.save(path, value)


def initialize() -> dict:
    if OUT.exists():
        raise FileExistsError("기존 재시도 기록을 덮어쓰지 않습니다.")
    original = read(ROOT / "runs/manifest.json")
    criteria = read(ROOT / "criteria-runs/manifest.json")
    freshness = read(ROOT / "freshness-runs/manifest.json")
    expected = {ROOT / name: value for name, value in original["source_hashes"].items()}
    expected.update({ROOT / "criteria.py": criteria["source_sha256"],
                     ROOT / "freshness.py": freshness["script_sha256"],
                     ROOT.parent / "ideas-lab/run_models.py": criteria["prior_cli_sha256"]})
    expected.update({P.REPO / name: value for name, value in original["stage_setup_hashes"].items()})
    for path, value in expected.items():
        if digest(path) != value:
            raise ValueError(f"원래 실행기의 내용이 달라졌습니다: {path}")
    schedule = [("codex", condition, repeat) for condition in freshness["prompts"]
                for repeat in range(1, 4)]
    random.Random(2026100517).shuffle(schedule)
    originals = sorted(path for folder in ("runs", "criteria-runs", "freshness-runs")
                       for path in (ROOT / folder).rglob("*.json"))
    manifest = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "reason": "사용자가 서버 혼잡으로 중단된 비교를 다시 시도하도록 요청했습니다.",
        "source_hashes": {str(path.relative_to(P.REPO)): digest(path)
                          for path in [*expected, Path(__file__)]},
        "original_record_hashes": {str(path.relative_to(ROOT)): digest(path) for path in originals},
        "cli_versions": {host: subprocess.check_output([host, "--version"], text=True).strip()
                         for host in ("claude", "codex")},
        "previous_cli_versions": original["cli_versions"],
        "stage_source_revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=P.REPO, text=True).strip(),
        "criteria_manifest": criteria,
        "freshness_manifest": freshness,
        "freshness_schedule": schedule,
        "native_plan": [
            {"starter": starter, "receiver": receiver, "condition": condition,
             "retries_failed_attempt": starter == "claude" and condition == "stage_card"}
            for starter, receiver in (("claude", "codex"), ("codex", "claude"))
            for condition in (["stage_card", "stage_card_observation"] if starter == "claude"
                              else ["stage_card_observation", "stage_card"])],
        "planned_calls": {"criteria_extraction": 1, "criteria_decisions": 12,
                          "freshness": 6, "native_handoff": 4},
        "parallelism": 1, "claude_max_reported_cost_usd": 2.0,
        "codex_model_requested": "CLI default, unchanged command",
        "codex_cost_usd": None,
        "limits": ["별도 시점의 재시도이며 원래 실패를 대체하지 않습니다.",
                   "Codex CLI 기본 모델을 명시적으로 고정하지 않았습니다.",
                   "임시 경로와 Stage 카드 생성 시각은 달라질 수 있습니다."]}
    save(OUT / "manifest.json", manifest)
    return manifest


async def criteria() -> None:
    out = OUT / "criteria-runs"
    original = read(ROOT / "criteria-runs/extract--codex.json")
    result = await C.CLI.invoke("codex", original["prompt"])
    save(out / "extract--codex.json", result)
    print(json.dumps({"extraction": "codex", "error": result["error"]}), flush=True)
    if result["error"]:
        raise RuntimeError("재시도 오류를 보존하고 추가 호출을 멈춥니다.")
    rules, errors = [], []
    answer = result["answer"]
    if answer["action"] != "extract_rules" or not answer["targets"]:
        errors.append("기준 추출 응답이 아니거나 기준이 없습니다.")
    for item in answer["targets"]:
        try:
            rule = json.loads(item)
            if set(rule) != {"rule", "project", "status", "source", "quote"}:
                raise ValueError("기준 필드 오류")
            note = next(value for value in C.NOTES if value["id"] == rule["source"])
            if not rule["quote"] or rule["quote"] not in note["text"]:
                raise ValueError("원문에 없는 인용")
            if rule["status"] not in {"confirmed", "unconfirmed"}:
                raise ValueError("상태 오류")
            rules.append(rule)
        except (ValueError, KeyError, StopIteration) as error:
            errors.append(str(error))
    save(out / "extraction-check--codex.json", {"rules": rules, "errors": errors})
    if errors:
        raise RuntimeError("추출 오류를 보존했습니다. 정답으로 고쳐 넣지 않습니다.")
    for index, case in enumerate(C.CASES):
        conditions = ["raw_notes", "extracted_rules"]
        if (index + 1) % 2:
            conditions.reverse()
        for condition in conditions:
            payload = {"policy": C.POLICY, "task": case["task"],
                       "allowed_actions_and_targets": case["actions"],
                       "records": C.NOTES if condition == "raw_notes" else rules}
            result = await C.CLI.invoke(
                "codex", C.CLI.SYSTEM + "\n" + json.dumps(payload, ensure_ascii=False))
            row = {"host": "codex", "case": case["id"], "condition": condition,
                   "cli": result, "matches": bool(result["answer"] and
                                                   C.CLI.matches(result["answer"], case["expected"]))}
            save(out / f"{case['id']}--codex--{condition}.json", row)
            print(json.dumps({key: row[key] for key in ("case", "condition", "matches")}), flush=True)
            if result["error"]:
                raise RuntimeError("기준 적용 오류를 보존하고 추가 호출을 멈춥니다.")


async def freshness(manifest: dict) -> None:
    prompts = manifest["freshness_manifest"]["prompts"]
    for host, condition, repeat in manifest["freshness_schedule"]:
        result = await C.CLI.invoke(host, prompts[condition])
        row = {"host": host, "condition": condition, "repeat": repeat, "cli": result}
        save(OUT / "freshness-runs" / f"{host}--{condition}--r{repeat}.json", row)
        print(json.dumps({"freshness": condition, "repeat": repeat,
                          "action": (result["answer"] or {}).get("action"),
                          "error": result["error"]}), flush=True)
        if result["error"]:
            raise RuntimeError("관찰 시점 비교 오류를 보존하고 멈춥니다.")


async def handoff() -> None:
    case = next(case for case in P.H.CASES if case["id"] == "retrospective_owner_conflict")
    for starter, receiver in (("claude", "codex"), ("codex", "claude")):
        with tempfile.TemporaryDirectory(prefix="stage-followup-retry-") as directory:
            temp = Path(directory)
            source = temp / "source"
            source.mkdir()
            setup = P.setup(source, case, starter, receiver)
            lane = f"{case['id']}--{starter}-to-{receiver}"
            save(OUT / "runs" / lane / "setup.json", setup)
            if starter == "claude":
                previous = read(ROOT / "runs" / lane / "setup.json")
                for key in ("seed_sha256", "target_sha256", "card"):
                    if setup[key] != previous[key]:
                        raise ValueError(f"재시도 초기 자료가 달라졌습니다: {key}")
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
                before = N.manifest(root)
                prompt = native.RULES + "\n작업 카드를 읽고 이 임시 프로젝트의 일을 이어서 끝내세요: " + P.CARD
                print(json.dumps({"start": lane, "condition": condition}), flush=True)
                cli = await native.invoke(receiver, root, prompt)
                save(OUT / "runs" / lane / condition / "cli.json", cli)
                verification = P.check(root, case)
                after = N.manifest(root)
                changed = sorted(name for name in before.keys() | after.keys()
                                 if before.get(name) != after.get(name))
                outside = [name for name in changed if name != case["target"]]
                content = (root / case["target"]).read_text()
                note_preserved = P.H.NOTE in content
                verified = verification["returncode"] == 0 and not outside and note_preserved
                record = {"id": lane + "--" + condition, "case": case["id"], "receiver": receiver,
                          "condition": condition, "clone_seconds": clone_seconds,
                          "preparation": prepared, "initial_manifest": before, "final_manifest": after,
                          "changed_paths": changed, "outside_target_changes": outside,
                          "note_preserved": note_preserved, "verification": verification,
                          "verified": verified, "declared_complete": (cli.get("answer") or {}).get("complete"),
                          "success": verified and (cli.get("answer") or {}).get("complete") is True,
                          "seconds_including_verification": time.perf_counter() - started,
                          "final_source": content,
                          "retries_failed_attempt": starter == "claude" and condition == "stage_card"}
                save(OUT / "runs" / lane / condition / "result.json", record)
                print(json.dumps({"finished": record["id"], "verified": verified,
                                  "complete": record["declared_complete"], "error": cli["error"]}), flush=True)
                if cli["error"]:
                    raise RuntimeError("인계 오류를 보존하고 추가 호출을 멈춥니다.")


async def main() -> None:
    manifest = initialize()
    status = {"completed_phases": [], "error": None}
    try:
        for phase, task in (("criteria", criteria),
                            ("freshness", lambda: freshness(manifest)), ("native_handoff", handoff)):
            status["phase"] = phase
            await task()
            status["completed_phases"].append(phase)
            save(OUT / "status.json", status)
    except Exception as error:
        status["error"] = str(error)
        raise
    finally:
        status["stopped_at"] = datetime.now(timezone.utc).isoformat()
        save(OUT / "status.json", status)


if __name__ == "__main__":
    asyncio.run(main())

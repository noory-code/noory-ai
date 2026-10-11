"""목표와 전체 검사를 공개한 Stage 작업 기록을 임시 복사본에 만듭니다."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import time

import native

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
CROSS = ROOT.parent / "cross-session"
SPEC = importlib.util.spec_from_file_location("previous_harness", CROSS / "harness.py")
assert SPEC and SPEC.loader
H = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(H)
CARD = ".stage/work/current/W-00000001/_story.md"
GOALS = {
    "roadmap_repeated_criteria": [
        "create-milestone의 --completion-criteria를 반복하면 모든 값을 입력 순서대로 '- ' 항목으로 기록합니다.",
        "기존 단일 값과 생략 경로를 유지하고 test_roadmap_v4 모듈의 전체 검사를 통과합니다."],
    "retrospective_owner_conflict": [
        "retrospective_id_for_work_item(item_id)는 stage_root 없이 작업 번호 하나만 받아 대응하는 회고 번호를 반환합니다.",
        "write_driver_retrospective는 R-00000041을 W-00000099가 소유하면 W-00000041의 회고 쓰기를 중단합니다.",
        "충돌 때 빈 회고 ID를 반환하고 오류에 세 번호를 포함하며 R-00000042와 R-00000043을 만들지 않습니다.",
        "회고 예약의 다른 기존 동작을 보존하고 test_drive 모듈의 전체 검사를 통과합니다."],
}


def command(case: dict) -> list[str]:
    return ["python3", "-B", "-m", "unittest", "discover", "-s", "stage/scripts/tests",
            "-p", case["test_file"].split("/")[-1], "-q"]


def check(root: Path, case: dict) -> dict:
    started = time.perf_counter()
    result = subprocess.run(command(case), cwd=root, text=True, capture_output=True, timeout=120)
    return {"command": command(case), "returncode": result.returncode,
            "stdout": result.stdout.replace(str(root), "<experiment>"),
            "stderr": result.stderr.replace(str(root), "<experiment>"),
            "seconds": time.perf_counter() - started}


def section(text: str, name: str, content: str) -> str:
    pattern = rf"(?ms)^## {re.escape(name)}\n.*?(?=^## |\Z)"
    replacement = f"## {name}\n\n{content}\n\n"
    if re.search(pattern, text):
        return re.sub(pattern, lambda _: replacement, text, count=1)
    return text.rstrip() + "\n\n" + replacement


def setup(root: Path, case: dict, starter: str, receiver: str) -> dict:
    started = time.perf_counter()
    seed_path = CROSS / "runs" / f"{case['id']}--{starter}-to-{receiver}" / "seed" / "seed.json"
    seed = json.loads(seed_path.read_text())
    H.setup(root, case, seed["source_after"])
    if case["id"] == "retrospective_owner_conflict":
        path = root / case["target"]
        path.write_text(path.read_text() + H.NOTE, encoding="utf-8")
    stage = REPO / "stage"
    commands = [[sys.executable, str(stage / "scripts/init_stage.py"), "--project-root", str(root), "--language", "ko"],
                [sys.executable, str(stage / "skills/stage-work/register_work.py"), "--project-root", str(root),
                 "--title", "실험용 코드 수정을 이어받아 완료 기준을 충족합니다", "--id", "W-00000001",
                 "--kind", "fix", "--scale", "story", "--scope", case["target"], "--venue", receiver,
                 "--purpose", "다른 AI가 시작한 수정을 이어받아 명시된 동작과 전체 검사를 충족합니다",
                 "--acceptance", " ".join(command(case))]]
    for goal in [*GOALS[case["id"]], "대상 소스 외의 파일과 사람이 추가한 주석을 보존합니다."]:
        commands[-1].extend(["--success-criterion", goal])
    setup_results = []
    for args in commands:
        result = subprocess.run(args, text=True, capture_output=True)
        setup_results.append({"command": args, "returncode": result.returncode,
                              "stdout": result.stdout, "stderr": result.stderr})
        if result.returncode:
            raise RuntimeError(f"Stage fixture setup failed: {result.stderr}")
    card_path = root / CARD
    card = card_path.read_text()
    last = seed["history"][-1]["assistant"]
    card = section(card, "Progress", "이전 AI의 마지막 수정 요청과 공개된 이유입니다. 결과 응답은 기록되지 않았습니다.\n\n"
                   + "```json\n" + json.dumps(last, ensure_ascii=False, indent=2) + "\n```")
    card = section(card, "Verification", "완료를 확인하지 않았습니다. 다음 명령은 모든 완료 조건과 기존 동작을 검사합니다.\n\n"
                   + "```text\n" + " ".join(command(case)) + "\n```\n실패 내용을 직접 확인하고 대상 소스에서 수정할 수 있습니다.")
    card = section(card, "Next action", "현재 대상 파일과 위 완료 기준을 대조하고 남은 수정을 수행한 뒤 전체 검사를 실행합니다.")
    card_path.write_text(card, encoding="utf-8")
    (root / ".stage/operations/verification.md").write_text(
        "# 검증 종류\n\n| Kind | `passed`의 의미 |\n|---|---|\n"
        "| fix | 작업 카드의 전체 검사 명령이 통과하고 보호한 파일과 주석을 보존합니다. |\n",
        encoding="utf-8")
    (root / "AGENTS.md").write_text(native.RULES, encoding="utf-8")
    return {"seconds": time.perf_counter() - started, "seed": str(seed_path.relative_to(ROOT.parent)),
            "seed_sha256": native.digest(seed_path.read_text()), "setup_results": setup_results,
            "card": card, "target_sha256": native.digest((root / case["target"]).read_text())}


def add_observation(root: Path, case: dict) -> dict:
    started = time.perf_counter()
    source = (root / case["target"]).read_text()
    relative = ".stage/research/handoff-observation.json"
    value = {"observed_at": "handoff_before_receiver_action_1",
             "scope": "인계 시점에 한 번 읽은 파일입니다. 이후 수정·검사 결과가 이 관찰보다 최신입니다.",
             "target": case["target"], "sha256": native.digest(source), "content": source}
    H.save(root / relative, value)
    path = root / CARD
    card = path.read_text()
    card += ("\n## Handoff observation\n\n인계 시점의 파일은 " + relative
             + "에 있습니다. 수정이 성공한 뒤에도 이 사본을 현재 파일이라고 해석하지 마세요.\n")
    path.write_text(card, encoding="utf-8")
    return {"seconds": time.perf_counter() - started, "preparation_file_reads": 1,
            "observation": value, "card": card}

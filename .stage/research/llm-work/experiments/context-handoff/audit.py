"""Stage 인계 자료를 복사본에서 읽고 보수적으로 줄일 수 있는 양을 잽니다."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO / "stage" / "hooks"))
from stage_context import session_context  # noqa: E402
from stage_work import item_is_open, load_work_items  # noqa: E402

REMOVED_HEADINGS = {"Current work hierarchy", "Active work", "Review candidates"}
FIELDS = ("Purpose", "Success criteria", "Next action", "Progress", "Verification")


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def sections(text: str, level: int) -> list[tuple[str, str]]:
    matches = list(re.finditer(rf"^{'#' * level} ([^\n]+)\n", text, re.MULTILINE))
    result = [("preamble", text[:matches[0].start()] if matches else text)]
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result.append((match.group(1), text[match.start():end]))
    return result


def body(section: str) -> str:
    return section.partition("\n")[2].strip()


def save(name: str, value: object) -> None:
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if (ROOT / "audit.json").exists() or (ROOT / "snapshot.json").exists():
        raise FileExistsError("기존 결과를 덮어쓰지 않습니다.")
    start = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="stage-context-audit-") as directory:
        project = Path(directory) / "project"
        project.mkdir()
        stage = project / ".stage"
        shutil.copytree(REPO / ".stage", stage,
                        ignore=shutil.ignore_patterns("research", ".runtime", ".obsidian", "__pycache__"))
        sessions = REPO / ".stage" / ".runtime" / "sessions"
        if sessions.exists():
            shutil.copytree(sessions, stage / ".runtime" / "sessions")
        # 실제 지침의 존재 목록도 복원합니다. 개인 설정이나 대화 원문은 읽지 않습니다.
        for parent in [REPO, *(p for p in REPO.iterdir() if p.is_dir() and not p.name.startswith("."))]:
            for name in ("CLAUDE.md", "AGENTS.md", "AGENTS.override.md"):
                source = parent / name
                if source.is_file():
                    dest = project / source.relative_to(REPO)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, dest)

        context = session_context(project)
        context_parts = sections(context, 3)
        kept_context = "".join(text for title, text in context_parts if title not in REMOVED_HEADINGS)
        removed = [(title, text) for title, text in context_parts if title in REMOVED_HEADINGS]
        items = load_work_items(stage)
        by_id = {item.item_id: item for item in items}
        cards = {item.item_id: item.path.read_text(encoding="utf-8") for item in items}
        observations = []
        inputs = {}
        for item in sorted((item for item in items if item_is_open(item)), key=lambda item: item.item_id):
            chain = []
            current = item
            while current:
                if current.item_id in chain:
                    raise ValueError("작업의 부모 관계가 순환합니다.")
                chain.append(current.item_id)
                current = by_id.get(current.parent)
            chain.reverse()
            documents = "\n\n".join(
                f"### Record {key}\nPath: {by_id[key].path.relative_to(project).as_posix()}\n{cards[key]}"
                for key in chain)
            query = f"\n\nContinue work: {item.item_id}\n"
            baseline = context + query + documents
            selected = kept_context + query + documents
            part_map = dict(sections(cards[item.item_id], 2))
            nonempty = {field: bool(body(part_map.get(field, ""))) for field in FIELDS}
            observations.append({
                "work": item.item_id, "path": item.path.relative_to(project).as_posix(),
                "status": item.status, "ancestors_included": chain[:-1],
                "nonempty_sections": nonempty,
                "baseline_characters": len(baseline), "selected_characters": len(selected),
                "removed_characters": len(baseline) - len(selected),
                "reduction_percent": round((1 - len(selected) / len(baseline)) * 100, 3),
                "whole_card_and_ancestors_preserved": all(cards[key] in selected for key in chain),
                "baseline_sha256": digest(baseline), "selected_sha256": digest(selected),
            })
            inputs[item.item_id] = {"baseline": baseline, "selected": selected}

        source_files = {str(p.relative_to(REPO)): digest(p.read_text(encoding="utf-8"))
                        for p in (REPO / "stage" / "hooks").glob("*.py")}
        snapshot = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "context": context, "cards": cards, "inputs": inputs,
            "source_hashes": source_files, "audit_script_sha256": digest(Path(__file__).read_text()),
            "removed_sections": [{"heading": title, "characters": len(text)} for title, text in removed],
            "snapshot_scope": "Copied project Stage records and instruction files; no conversation transcripts",
        }
        save("snapshot.json", snapshot)
        report = {
            "open_work_count": len(observations), "context_characters": len(context),
            "context_characters_without_work_overviews": len(kept_context),
            "context_sha256": digest(context), "work_items": observations,
            "empty_section_counts": {field: sum(not row["nonempty_sections"][field] for row in observations)
                                     for field in FIELDS},
            "measurement_seconds_including_copy": time.perf_counter() - start,
            "limits": [
                "Character counts are not tokenizer counts, latency or money.",
                "Nonempty text does not prove a correct or complete handoff.",
                "Empty named sections may be covered elsewhere; no semantic completeness claim.",
                "The baseline supplies whole target and ancestor cards in addition to hook context.",
                "The selector removes only three overview sections, retains other shared context and whole cards.",
                "Removed sibling state can matter; no behavior-equivalence claim.",
                "No model calls, code edits, task execution, or automatic recovery were tested.",
            ],
        }
        save("audit.json", report)
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

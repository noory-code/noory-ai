"""명시한 의존 관계와 적용 조건만 처리하는 연구용 시제품입니다."""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any


def _local_path(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    if Path(relative).is_absolute() or not candidate.is_relative_to(root.resolve()):
        raise ValueError("자료 경로가 지정한 폴더 밖을 가리킵니다.")
    return candidate


def snapshot(root: Path, paths: list[str]) -> dict[str, str | None]:
    """바이트 해시를 읽습니다. 의미가 같은 편집도 변경으로 셉니다."""
    result: dict[str, str | None] = {}
    for relative in paths:
        path = _local_path(root, relative)
        try:
            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        except FileNotFoundError:
            result[relative] = None
    return result


def plan_review(
    before: dict[str, str | None],
    after: dict[str, str | None],
    dependencies: dict[str, Any],
) -> dict[str, Any]:
    """기록한 의존 관계만 따라갑니다. 숨은 의존 관계를 발견하지 못합니다."""
    changed = {path for path in before.keys() | after.keys() if before.get(path) != after.get(path)}
    affected: set[str] = set()
    uncertain: set[str] = set()
    links: dict[str, list[str]] = {}
    issues: list[dict[str, str]] = []
    for decision, spec in dependencies.items():
        valid = isinstance(spec, dict) and all(
            isinstance(spec.get(key), list)
            and all(isinstance(item, str) and item for item in spec[key])
            for key in ("files", "decisions")
        )
        if not valid:
            uncertain.add(decision)
            links[decision] = []
            issues.append({"id": decision, "reason": "dependency_not_recorded"})
            continue
        links[decision] = spec["decisions"]
        for path in spec["files"]:
            if path not in before or path not in after or before[path] is after[path] is None:
                uncertain.add(decision)
                issues.append({"id": decision, "reason": f"source_not_recorded:{path}"})
            elif path in changed:
                affected.add(decision)
        if any(parent not in dependencies for parent in spec["decisions"]):
            uncertain.add(decision)
            issues.append({"id": decision, "reason": "unknown_decision"})

    visited: set[str] = set()

    def visit(decision: str, stack: list[str]) -> None:
        if decision in stack:
            cycle = stack[stack.index(decision):]
            uncertain.update(cycle)
            issues.append({"id": decision, "reason": "dependency_cycle"})
            return
        if decision in visited or decision not in links:
            return
        for parent in links[decision]:
            visit(parent, stack + [decision])
        visited.add(decision)

    for decision in dependencies:
        visit(decision, [])
    while True:
        previous = (affected.copy(), uncertain.copy())
        for decision, parents in links.items():
            if affected.intersection(parents):
                affected.add(decision)
            if uncertain.intersection(parents):
                uncertain.add(decision)
        if previous == (affected, uncertain):
            break
    return {
        "action": "clarify" if uncertain else "review" if affected else "keep",
        "targets": sorted(affected | uncertain),
        "affected": sorted(affected),
        "uncertain": sorted(uncertain),
        "changed_files": sorted(changed),
        "issues": issues,
    }


def extract_evidence(root: Path, paths: list[str], query: dict[str, Any]) -> dict[str, Any]:
    """구조화한 자료의 조건을 비교합니다. 자유 문장에서 조건을 추론하지 않습니다."""
    selected: list[dict[str, Any]] = []
    issues: list[dict[str, str]] = []
    answers: set[str] = set()
    targets: set[str] = set()
    seen: set[str] = set()
    if not all(isinstance(query.get(key), str) and query[key] for key in ("topic", "version")):
        return {"action": "clarify", "targets": [], "selected": [], "issues": [
            {"id": "query", "reason": "topic_or_version_missing"},
        ]}
    context = query.get("context")
    if not isinstance(context, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in context.items()
    ):
        return {"action": "clarify", "targets": [], "selected": [], "issues": [
            {"id": "query", "reason": "context_not_recorded"},
        ]}
    for relative in paths:
        try:
            record = json.loads(_local_path(root, relative).read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            targets.add(relative)
            issues.append({"id": relative, "reason": type(error).__name__})
            continue
        if not isinstance(record, dict) or not isinstance(record.get("topic"), str):
            targets.add(relative)
            issues.append({"id": relative, "reason": "topic_not_recorded"})
            continue
        if record["topic"] != query["topic"]:
            continue
        version = record.get("version")
        if isinstance(version, str) and version and version != query["version"]:
            continue
        identifier = record.get("id")
        if not isinstance(identifier, str) or not identifier:
            identifier = relative
            issues.append({"id": identifier, "reason": "id_not_recorded"})
        targets.add(identifier)
        selected.append({**record, "path": relative})
        if identifier in seen:
            issues.append({"id": identifier, "reason": "duplicate_id"})
        seen.add(identifier)
        if not isinstance(version, str) or not version:
            issues.append({"id": identifier, "reason": "version_not_recorded"})
        if not isinstance(record.get("source"), str) or not record["source"].strip():
            issues.append({"id": identifier, "reason": "source_not_recorded"})
        answer = record.get("answer")
        if answer not in ("supported", "unsupported"):
            issues.append({"id": identifier, "reason": "answer_not_supported"})
            continue
        exceptions = record.get("exceptions")
        if not isinstance(exceptions, list):
            issues.append({"id": identifier, "reason": "exceptions_not_recorded"})
            continue
        matches: set[str] = set()
        for exception in exceptions:
            if not isinstance(exception, dict) or exception.get("answer") not in (
                "supported", "unsupported",
            ):
                issues.append({"id": identifier, "reason": "invalid_exception"})
                continue
            conditions = exception.get("when")
            if not isinstance(conditions, dict) or not conditions or not all(
                isinstance(key, str) and isinstance(value, str)
                for key, value in conditions.items()
            ):
                issues.append({"id": identifier, "reason": "invalid_exception_condition"})
                continue
            if any(key in context and context[key] != value for key, value in conditions.items()):
                continue
            if any(key not in context for key in conditions):
                issues.append({"id": identifier, "reason": "exception_context_missing"})
                continue
            matches.add(exception["answer"])
        answers.update(matches or {answer})
    if not selected:
        issues.append({"id": "query", "reason": "no_matching_evidence"})
    if len(answers) > 1:
        issues.append({"id": "query", "reason": "conflicting_evidence"})
    return {
        "action": next(iter(answers)) if len(answers) == 1 and not issues else "clarify",
        "targets": sorted(targets),
        "selected": selected,
        "issues": issues,
    }


def build_cases() -> list[dict[str, Any]]:
    """작은 합성 사례 여덟 개를 실행합니다. 실제 프로젝트의 효과를 증명하지는 않습니다."""
    cases: list[dict[str, Any]] = []
    review_task = (
        "자료의 이전·현재 내용과 판단별 의존 관계를 보고 재검토할 대상을 고르세요. "
        "current의 null은 실제로 파일이 삭제되었다는 관찰입니다. "
        "files는 직접 근거이고 decisions는 다른 판단을 근거로 쓴다는 뜻입니다. "
        "변경이나 삭제가 영향을 준 판단과 이를 근거로 쓴 판단을 모두 찾으세요. "
        "의존 관계가 null이거나 알 수 없는 판단·자료가 있으면 연결된 판단까지 보류하세요. "
        "action은 review(알려진 변경을 재검토), keep(변경 없음), "
        "clarify(의존 관계부터 확인) 중 하나입니다. "
        "clarify를 고를 때도 알려진 변경 때문에 재검토할 판단을 targets에 포함하세요. "
        "targets에는 다시 확인할 판단의 ID를 정렬해 담고 keep이면 빈 목록을 주세요. "
        "응답은 {action, targets, reason} JSON 하나로 작성하세요."
    )
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for variant in ("changed", "unchanged", "deleted", "unknown"):
            initial = {"policy.txt": "허용 개수: 3개", "format.txt": "들여쓰기: 2칸"}
            for path, text in initial.items():
                (root / path).write_text(text, encoding="utf-8")
            dependencies: dict[str, Any] = {
                "approve": {"files": ["policy.txt"], "decisions": []},
                "publish": {"files": [], "decisions": ["approve"]},
                "format": {"files": ["format.txt"], "decisions": []},
            }
            before = snapshot(root, list(initial))
            if variant == "changed":
                (root / "policy.txt").write_text("허용 개수: 4개", encoding="utf-8")
            elif variant == "deleted":
                (root / "policy.txt").unlink()
            elif variant == "unknown":
                dependencies = {
                    "audit": None,
                    "publish": {"files": [], "decisions": ["audit"]},
                }
            current = {
                path: (root / path).read_text(encoding="utf-8") if (root / path).exists() else None
                for path in initial
            }
            observation = {"before": initial, "current": current, "dependencies": dependencies}
            computed = plan_review(before, snapshot(root, list(initial)), dependencies)
            expected = {
                "changed": {"action": "review", "targets": ["approve", "publish"]},
                "unchanged": {"action": "keep", "targets": []},
                "deleted": {"action": "review", "targets": ["approve", "publish"]},
                "unknown": {"action": "clarify", "targets": ["audit", "publish"]},
            }[variant]
            cases.append({
                "id": f"I01_{variant}", "idea": "I01", "task": review_task,
                "baseline": observation, "enhanced": {**observation, "computed": computed},
                "expected": expected,
                "scoring_note": (
                    "양쪽에 같은 원본과 의존 관계를 줍니다. 개선 조건에는 코드가 해시와 "
                    "의존 관계로 계산한 답도 제공합니다. 모델 능력 향상으로 해석하면 안 됩니다."
                ),
            })
        evidence_task = (
            "query에 지정한 주제와 버전에서 기능을 지원하는지 판단하세요. "
            "version은 정확히 일치해야 합니다. exceptions의 when이 context와 모두 맞으면 "
            "그 예외의 answer를 적용합니다. 명시된 예외가 기본 answer보다 우선합니다. "
            "출처·버전·예외 목록이 없거나 필요한 조건을 모르거나 자료가 충돌하면 보류하세요. "
            "action은 supported, unsupported, clarify 중 하나입니다. "
            "targets에는 해당 주제·버전의 판단에 쓴 자료 ID를 모두 정렬해 담으세요. "
            "조건이 빠지거나 충돌한 관련 자료도 포함하고 다른 버전의 자료는 제외하세요. "
            "응답은 {action, targets, reason} JSON 하나로 작성하세요."
        )

        def record(identifier: str, **updates: Any) -> dict[str, Any]:
            return {
                "id": identifier, "topic": "export", "version": "2", "answer": "supported",
                "exceptions": [], "source": f"manual/{identifier}", **updates,
            }

        variants = [
            ("version", [record("old", version="1", answer="unsupported"), record("current")],
             {}, {"action": "supported", "targets": ["current"]}),
            ("exception", [record("policy", exceptions=[{
                "when": {"region": "EU"}, "answer": "unsupported",
             }])], {"region": "EU"}, {"action": "unsupported", "targets": ["policy"]}),
            ("conflict", [record("a"), record("b", answer="unsupported")],
             {}, {"action": "clarify", "targets": ["a", "b"]}),
            ("missing_scope", [{
                "id": "partial", "topic": "export", "version": "2", "answer": "supported",
             }], {}, {"action": "clarify", "targets": ["partial"]}),
        ]
        for variant, records, context, expected in variants:
            query = {"topic": "export", "version": "2", "context": context}
            paths = []
            for index, document in enumerate(records):
                path = f"{variant}-{index}.json"
                (root / path).write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
                paths.append(path)
            actual = [json.loads((root / path).read_text(encoding="utf-8")) for path in paths]
            observation = {"query": query, "documents": actual}
            cases.append({
                "id": f"I02_{variant}", "idea": "I02", "task": evidence_task,
                "baseline": observation,
                "enhanced": {**observation, "computed": extract_evidence(root, paths, query)},
                "expected": expected,
                "scoring_note": (
                    "양쪽에 같은 원본 자료를 줍니다. 개선 조건에는 코드가 적용 조건을 비교해 "
                    "계산한 답도 제공합니다. 자유 문서 검색이나 모델 능력 향상을 검증하지 않습니다."
                ),
            })
    return cases

"""관찰한 자료만 다시 시험하고, 정해진 manifest 검사 절차를 실행합니다."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import tempfile
from typing import Any, Callable


MANIFEST_PATHS = (".claude-plugin/plugin.json", ".codex-plugin/plugin.json")
FACTORS = ("input", "tool_response", "file_state")
Observer = Callable[[Path, dict[str, Any], dict[str, Any]], dict[str, Any]]


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _normal_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError("파일 경로 형식이 허용 범위를 벗어났습니다.")
    if value.startswith("/") or any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError("시험 폴더 안의 상대 경로만 사용할 수 있습니다.")
    return value


def _safe_path(root: Path, relative: str) -> Path:
    path = root / _normal_path(relative)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("파일 경로가 시험 폴더를 벗어났습니다.")
    return path


def _file_value(content: str | None) -> dict[str, Any]:
    if content is not None and not isinstance(content, str):
        raise ValueError("파일 내용은 UTF-8 문자열이나 누락을 나타내는 null이어야 합니다.")
    return {
        "exists": content is not None,
        "content": content,
        "sha256": None if content is None else hashlib.sha256(content.encode("utf-8")).hexdigest(),
    }


def _make_record(request: Any, response: Any, files: dict[str, Any]) -> dict[str, Any]:
    record = json.loads(_json({"schema_version": 1, "input": request,
                             "tool_response": response, "files": files}))
    record["hashes"] = {
        "input": _hash(record["input"]),
        "tool_response": _hash(record["tool_response"]),
        "file_state": _hash(record["files"]),
    }
    return record


def record_observation(
    root: Path, request: dict[str, Any], response: dict[str, Any], paths: list[str]
) -> dict[str, Any]:
    """실제로 읽은 UTF-8 파일과 제공받은 자료를 복사해 기록합니다."""
    files = {}
    for relative in sorted(set(paths)):
        path = _safe_path(root, relative)
        files[relative] = _file_value(path.read_bytes().decode("utf-8") if path.exists() else None)
    return _make_record(request, response, files)


def _validate_record(record: dict[str, Any]) -> None:
    if record.get("schema_version") != 1 or not isinstance(record.get("files"), dict):
        raise ValueError("기록 형식을 확인할 수 없습니다.")
    for relative, value in record["files"].items():
        _normal_path(relative)
        if not isinstance(value, dict) or value != _file_value(value.get("content")):
            raise ValueError("파일 내용과 해시가 일치하지 않습니다.")
    expected = _make_record(record.get("input"), record.get("tool_response"), record["files"])
    if record != expected:
        raise ValueError("기록과 해시가 일치하지 않습니다.")


def _observe_copy(record: dict[str, Any], observer: Observer) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="ideas-replay-") as directory:
        root = Path(directory)
        for relative, value in record["files"].items():
            path = _safe_path(root, relative)
            if value["exists"]:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(value["content"].encode("utf-8"))
        request, response = copy.deepcopy(record["input"]), copy.deepcopy(record["tool_response"])
        result = observer(root, request, response)
        actual_paths = {path.relative_to(root).as_posix() for path in root.rglob("*")
                        if path.is_file() or path.is_symlink()}
        paths = sorted(actual_paths | record["files"].keys())
        after = record_observation(root, request, response, paths)
        if after != record:
            raise ValueError("관찰 함수가 시험 자료를 바꿨습니다. 비교 결과를 사용하지 않습니다.")
        return json.loads(_json(result))


def replay_once(
    record: dict[str, Any], changes: dict[str, Any], observer: Observer
) -> dict[str, Any]:
    """한 자료 묶음만 바꾸고 두 복사본에서 같은 읽기 함수를 실행합니다."""
    _validate_record(record)
    if len(changes) != 1 or next(iter(changes)) not in FACTORS:
        raise ValueError("input, tool_response, file_state 중 하나만 바꿔야 합니다.")
    factor = next(iter(changes))
    candidate = copy.deepcopy(record)
    if factor == "file_state":
        if not isinstance(changes[factor], dict):
            raise ValueError("파일 상태는 경로와 내용의 사전이어야 합니다.")
        candidate["files"] = {
            _normal_path(path): _file_value(content) for path, content in changes[factor].items()
        }
    else:
        candidate[factor] = copy.deepcopy(changes[factor])
    candidate = _make_record(candidate["input"], candidate["tool_response"], candidate["files"])
    changed = [name for name in FACTORS if record["hashes"][name] != candidate["hashes"][name]]
    if changed != [factor]:
        raise ValueError("지정한 자료 묶음의 값이 실제로 달라져야 합니다.")
    return {
        "before": _observe_copy(record, observer),
        "after": _observe_copy(candidate, observer),
        "before_hashes": record["hashes"].copy(),
        "after_hashes": candidate["hashes"].copy(),
        "changed_factors": changed,
        "scope": "저장한 입력, 도구 응답, UTF-8 파일만 비교했습니다. 서버 내부 상태는 다루지 않습니다.",
    }


def _fixture_observer(
    root: Path, request: dict[str, Any], response: dict[str, Any]
) -> dict[str, Any]:
    """시험용으로 공개한 규칙을 실행합니다. 모델의 추론을 재현하지 않습니다."""
    if request["kind"] == "search":
        documents = response["documents"]
        found = request["required_document"] in documents
        return {"status": "found" if found else "missing"}
    if request["kind"] == "policy":
        exceptions = request["evidence"].get("exceptions")
        if exceptions is None or request["region"] not in exceptions:
            return {"status": "unknown"}
        return {"status": exceptions[request["region"]]}
    if request["kind"] == "write":
        path = _safe_path(root, request["target"])
        content = path.read_bytes().decode("utf-8") if path.exists() else None
        return {"status": "complete" if content == request["expected_content"] else "incomplete"}
    raise ValueError("정의하지 않은 시험 종류입니다.")


def compare_fixture(record: dict[str, Any], changes: dict[str, Any]) -> dict[str, Any]:
    """알려진 국소 결함을 비교합니다. 서비스의 원인을 추정하지 않습니다."""
    result = replay_once(record, changes, _fixture_observer)
    before, after = result["before"]["status"], result["after"]["status"]
    kind = record["input"]["kind"]
    action, targets = "fallback", []
    if before == after:
        action = "no_difference"
    elif kind == "search" and (before, after) == ("missing", "found"):
        action, targets = "inspect_search", [record["input"]["required_document"]]
    elif kind == "policy" and before == "unknown" and after in ("supported", "unsupported"):
        action, targets = "restore_exception", ["input.evidence.exceptions"]
    elif kind == "write" and (before, after) == ("incomplete", "complete"):
        action, targets = "repair_write", [record["input"]["target"]]
    return {"action": action, "targets": sorted(targets), "comparison": result,
            "reason": "공개한 시험 규칙으로 두 결과를 비교했습니다.",
            "computed_by": "local_python_rule"}


def check_manifest_versions(root: Path) -> dict[str, Any]:
    """두 시험용 manifest를 읽습니다. 일치하지 않는 버전을 임의로 고치지 않습니다."""
    versions, names, errors = {}, {}, {}
    for relative in MANIFEST_PATHS:
        try:
            value = json.loads(_safe_path(root, relative).read_text(encoding="utf-8"))
            if not isinstance(value, dict) or set(value) != {"name", "version"}:
                raise ValueError("이 시험에서는 name과 version만 있는 사전을 받습니다.")
            name = value["name"]
            if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
                raise ValueError("name 형식이 다릅니다.")
            version = value["version"]
            version_pattern = r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
            if not isinstance(version, str) or not re.fullmatch(version_pattern, version):
                raise ValueError("version은 앞자리 0과 접미사가 없는 x.y.z 문자열이어야 합니다.")
            names[relative], versions[relative] = value["name"], version
        except OSError as error:
            errors[relative] = f"파일을 읽지 못했습니다. errno={error.errno}"
        except (UnicodeError, ValueError) as error:
            errors[relative] = str(error)
    if errors:
        action, targets = "fallback", sorted(errors)
    elif len(set(names.values())) != 1:
        action, targets = "fallback", sorted(MANIFEST_PATHS)
        errors = {"names": "서로 다른 플러그인의 버전을 비교하지 않습니다."}
    elif len(set(versions.values())) != 1:
        action, targets = "align_versions", sorted(MANIFEST_PATHS)
    else:
        action, targets = "accept", []
    return {"action": action, "targets": targets, "versions": versions, "errors": errors,
            "reason": "실제 파일을 읽고 공개한 형식과 버전 일치 규칙을 적용했습니다.",
            "computed_by": "local_python_rule"}


REPLAY_TASK = (
    "관찰 가능한 로컬 자료를 비교해 다음 확인 대상을 고르세요. "
    "원본 자료 또는 같은 자료를 처리한 로컬 도구 결과가 제공됩니다. "
    "숨겨진 서버 상태를 추정하지 마세요. "
    "시험 규칙: search는 required_document가 documents에 있으면 found, 없으면 missing입니다. "
    "policy는 evidence.exceptions에 region이 없으면 unknown, 있으면 그 값을 반환합니다. "
    "write는 실제 target 내용이 expected_content와 같으면 complete, 다르면 incomplete입니다. "
    "action은 inspect_search, restore_exception, repair_write, no_difference, fallback 중 하나입니다. "
    "검색 누락이 해소되면 inspect_search, 예외 복원으로 판단할 수 있으면 restore_exception, "
    "파일 내용을 바로잡아 완료되면 repair_write를 고릅니다. 결과가 같으면 no_difference, "
    "정해진 비교를 적용할 수 없으면 fallback입니다. "
    "targets는 검색의 required_document, 예외의 input.evidence.exceptions, 쓰기의 target을 씁니다. "
    "no_difference와 fallback의 targets는 빈 배열입니다. "
    "{action, targets, reason}으로 답하고 targets는 문자열 오름차순으로 정렬하세요."
)

MANIFEST_TASK = (
    "원본 자료 또는 같은 자료를 처리한 로컬 도구 결과로 다음 행동을 고르세요. "
    "파일이 없으면 그 상태도 제공됩니다. "
    "이 시험은 name과 version만 가진 JSON 사전을 받습니다. name은 소문자·숫자로 시작하고 "
    "소문자·숫자·하이픈만 허용합니다. version은 앞자리 0과 접미사가 없는 x.y.z 문자열입니다. "
    "action은 accept, align_versions, fallback 중 하나입니다. 같은 name과 같은 버전이면 accept, "
    "같은 name이고 유효한 버전이 서로 다르면 align_versions입니다. 누락·형식 오류·다른 name이면 "
    "fallback입니다. targets는 accept일 때 빈 배열, align_versions일 때 두 경로입니다. "
    "fallback이면 잘못되거나 누락된 파일 경로를 쓰고, name이 다르면 두 경로를 씁니다. "
    "어느 버전으로 맞출지는 정하지 마세요. {action, targets, reason}으로 답하고 "
    "targets는 문자열 오름차순으로 정렬하세요."
)


def _write_fixture(root: Path, files: dict[str, str | None]) -> None:
    for relative, content in files.items():
        if content is not None:
            path = _safe_path(root, relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content.encode("utf-8"))


def build_cases() -> list[dict[str, Any]]:
    """실제 임시 파일과 위 함수를 사용해 비교할 자료 8개를 만듭니다."""
    policy = {"default": "supported", "exceptions": {"island": "unsupported"}}
    corpus = {"policy.json": _json(policy), "overview.txt": "일반 안내입니다."}
    specifications = [
        ("search_missing", corpus,
         {"kind": "search", "required_document": "policy.json"},
         {"documents": ["overview.txt"]},
         {"tool_response": {"documents": ["overview.txt", "policy.json"]}},
         {"action": "inspect_search", "targets": ["policy.json"]}),
        ("exception_removed", corpus,
         {"kind": "policy", "region": "island", "evidence": {"default": "supported"}},
         {"documents": ["policy.json"]},
         {"input": {"kind": "policy", "region": "island", "evidence": policy}},
         {"action": "restore_exception", "targets": ["input.evidence.exceptions"]}),
        ("partial_write", {"output.txt": "title\n"},
         {"kind": "write", "target": "output.txt", "expected_content": "title\nbody\n"},
         {"success": True}, {"file_state": {"output.txt": "title\nbody\n"}},
         {"action": "repair_write", "targets": ["output.txt"]}),
        ("irrelevant_response_change", {"output.txt": "done\n"},
         {"kind": "write", "target": "output.txt", "expected_content": "done\n"},
         {"success": True}, {"tool_response": {"success": True, "trace_label": "another"}},
         {"action": "no_difference", "targets": []}),
    ]
    cases = []
    for name, files, request, response, changes, expected in specifications:
        with tempfile.TemporaryDirectory(prefix="ideas-fixture-") as directory:
            root = Path(directory)
            _write_fixture(root, files)
            record = record_observation(root, request, response, list(files))
            enhanced = compare_fixture(record, changes)
            if record_observation(root, request, response, list(files)) != record:
                raise AssertionError("원본 시험 자료가 바뀌었습니다.")
            cases.append({
                "id": f"I05_{name}", "idea": "I05", "task": REPLAY_TASK,
                "baseline": {"record": record, "proposed_change": changes},
                "enhanced": enhanced, "expected": expected,
                "scoring_note": "원본과 변경 내용을 기본 조건에 모두 제공합니다. 개선 조건에서는 "
                                "로컬 함수가 비교와 권고를 계산합니다. 모델 능력 향상으로 해석하지 않습니다.",
            })
    good = _json({"name": "sample-plugin", "version": "1.2.3"})
    manifest_specs = [
        ("same_version", good, good, {"action": "accept", "targets": []}),
        ("different_versions", good, _json({"name": "sample-plugin", "version": "1.2.4"}),
         {"action": "align_versions", "targets": sorted(MANIFEST_PATHS)}),
        ("invalid_version_type", _json({"name": "sample-plugin", "version": 123}), good,
         {"action": "fallback", "targets": [MANIFEST_PATHS[0]]}),
        ("missing_manifest", good, None,
         {"action": "fallback", "targets": [MANIFEST_PATHS[1]]}),
    ]
    for name, claude, codex, expected in manifest_specs:
        with tempfile.TemporaryDirectory(prefix="ideas-manifest-") as directory:
            root = Path(directory)
            files = dict(zip(MANIFEST_PATHS, (claude, codex)))
            _write_fixture(root, files)
            record = record_observation(root, {}, {}, list(MANIFEST_PATHS))
            enhanced = check_manifest_versions(root)
            if record_observation(root, {}, {}, list(MANIFEST_PATHS)) != record:
                raise AssertionError("읽기 검사가 manifest를 바꿨습니다.")
            cases.append({
                "id": f"I06_{name}", "idea": "I06", "task": MANIFEST_TASK,
                "baseline": {"manifests": record["files"]}, "enhanced": enhanced,
                "expected": expected,
                "scoring_note": "두 조건에 같은 형식 규칙을 줍니다. 개선 조건에서는 함수가 실제 파일을 "
                                "읽어 action과 targets를 계산합니다. 모델 능력 향상으로 해석하지 않습니다.",
            })
    return cases

"""완료된 리뷰 결과를 재사용할 조건을 확인하는 연구용 캐시입니다."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile
from typing import Any


def _relative_name(name: str) -> None:
    if not isinstance(name, str) or not name or "\\" in name or ":" in name or "\x00" in name:
        raise ValueError("파일 이름은 모호하지 않은 상대 경로여야 합니다.")
    if name.startswith("/") or any(part in ("", ".", "..") for part in name.split("/")):
        raise ValueError("파일 이름이 허용한 상대 경로 형식을 벗어났습니다.")


def fingerprint(files: dict[str, bytes], criteria: str, policy: str, reviewer: str) -> str:
    """제공된 입력만 해시합니다. 누락한 의존 관계나 모델 설정을 발견하지 못합니다."""
    if not isinstance(files, dict):
        raise ValueError("files는 경로와 바이트의 사전이어야 합니다.")
    if not all(isinstance(value, str) for value in (criteria, policy, reviewer)):
        raise ValueError("리뷰 기준·정책·모델 설정은 문자열이어야 합니다.")
    for name, content in files.items():
        _relative_name(name)
        if not isinstance(content, bytes):
            raise ValueError("파일 내용은 바이트여야 합니다.")
    digest = hashlib.sha256()

    def add(value: bytes) -> None:
        digest.update(len(value).to_bytes(8, "big"))
        digest.update(value)

    for value in ("review-reuse-v1", criteria, policy, reviewer, str(len(files))):
        add(value.encode("utf-8"))
    for name in sorted(files):
        add(name.encode("utf-8"))
        add(files[name])
    return digest.hexdigest()


def _cache_path(directory: Path, key: str) -> Path:
    if not isinstance(key, str) or re.fullmatch(r"[a-f0-9]{64}", key) is None:
        raise ValueError("캐시 키는 소문자 16진수 64자여야 합니다.")
    return directory / f"{key}.json"


def _check_json(value: Any, ancestors: set[int]) -> None:
    if value is None or type(value) in (bool, int, str):
        return
    if type(value) is float and math.isfinite(value):
        return
    if type(value) not in (dict, list):
        raise ValueError("결과에는 JSON 값만 저장할 수 있습니다.")
    if id(value) in ancestors:
        raise ValueError("결과에 순환 참조가 있습니다.")
    ancestors.add(id(value))
    try:
        if isinstance(value, dict):
            if not all(isinstance(key, str) for key in value):
                raise ValueError("JSON 객체의 키는 문자열이어야 합니다.")
            children = value.values()
        else:
            children = value
        for child in children:
            _check_json(child, ancestors)
    finally:
        ancestors.remove(id(value))


def _encode(value: dict[str, Any]) -> bytes:
    if not isinstance(value, dict):
        raise ValueError("완료된 결과는 JSON 객체여야 합니다.")
    try:
        _check_json(value, set())
        text = json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
        return text.encode("utf-8")
    except (TypeError, RecursionError, UnicodeError) as error:
        raise ValueError("결과를 완성된 JSON으로 저장할 수 없습니다.") from error


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON 객체에 중복된 필드가 있습니다.")
        result[key] = value
    return result


def lookup(directory: Path, key: str) -> dict[str, Any] | None:
    """손상되거나 읽을 수 없는 캐시는 miss로 처리합니다. 리뷰의 타당성은 검사하지 않습니다."""
    path = _cache_path(directory, key)
    try:
        if path.is_symlink():
            return None
        envelope = json.loads(path.read_bytes(), object_pairs_hook=_unique_object)
        if not isinstance(envelope, dict) or set(envelope) != {
            "version", "key", "result", "checksum",
        }:
            return None
        if type(envelope["version"]) is not int or envelope["version"] != 1:
            return None
        if envelope["key"] != key:
            return None
        encoded = _encode(envelope["result"])
        if envelope["checksum"] != hashlib.sha256(encoded).hexdigest():
            return None
        return envelope["result"]
    except (OSError, ValueError, UnicodeError, RecursionError):
        return None


def store(directory: Path, key: str, result: dict[str, Any]) -> None:
    """검증을 마친 결과만 호출자가 넘겨야 합니다. 임시 파일을 완성한 뒤 교체합니다."""
    target = _cache_path(directory, key)
    encoded = _encode(result)
    envelope = {
        "version": 1,
        "key": key,
        "result": json.loads(encoded),
        "checksum": hashlib.sha256(encoded).hexdigest(),
    }
    payload = _encode(envelope)
    directory.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=directory, prefix=f".{key}.", suffix=".tmp", delete=False,
        ) as output:
            temporary = Path(output.name)
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)

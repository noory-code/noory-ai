"""과거 수정 두 개를 임시 디렉터리에 복원하고 같은 회귀 검사로 확인합니다."""

from __future__ import annotations

import hashlib
import io
import json
import os
import platform
import subprocess
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


OUTPUT = Path(__file__).resolve().parent
REPOSITORY = OUTPUT.parents[4]
CASES = [
    {
        "id": "roadmap_repeated_criteria",
        "title": "마일스톤에 완료 기준 여러 개를 저장합니다",
        "criterion": (
            "정상적인 Stage v4 프로젝트에서 create-theme로 테마를 만든 뒤 "
            "create-milestone에 --completion-criteria를 세 번 전달합니다. "
            "값은 순서대로 Every check passes, Every artifact is published, "
            "Users can install the release입니다. 두 명령은 모두 성공해야 합니다. "
            "생성된 마일스톤 문서의 ## Completion criteria 아래에 세 값이 입력한 "
            "순서대로 각각 '- '로 시작하는 항목으로 남아야 합니다. "
            "이 동작만 검토하고 다른 기능이나 일반적인 코드 품질은 판정하지 마세요."
        ),
        "commit": "a1cd08dac15ddac5ac873d5d73e2db2c9aa48a68",
        "target": "stage/skills/stage-roadmap/manage_roadmap.py",
        "test_file": "stage/scripts/tests/test_roadmap_v4.py",
        "test": (
            "test_roadmap_v4.RoadmapCliTest."
            "test_completion_criteria_is_repeatable_and_preserves_every_value"
        ),
    },
    {
        "id": "retrospective_owner_conflict",
        "title": "다른 작업의 회고 번호와 충돌할 때 처리합니다",
        "criterion": (
            "현재 회고 R-00000041.md의 work_item이 W-00000099인 상태에서 "
            "W-00000041 작업의 회고를 write_driver_retrospective로 쓰려고 합니다. "
            "반환한 회고 ID는 빈 문자열이어야 하고 오류에는 R-00000041, W-00000099, "
            "W-00000041이 모두 나와야 합니다. 새 회고 R-00000042.md와 "
            "R-00000043.md가 생성되면 안 됩니다. 정상적인 Stage v4 경로와 "
            "앞부분 메타데이터를 사용한다고 가정합니다. 이 충돌 처리만 검토하고 "
            "다른 기능이나 일반적인 코드 품질은 판정하지 마세요."
        ),
        "commit": "244a219957377557af4c85c5c81426aee6f12b8a",
        "target": "stage/scripts/driver_lifecycle.py",
        "test_file": "stage/scripts/tests/test_drive.py",
        "test": (
            "test_drive.DriveTest."
            "test_driver_retrospective_refuses_id_owned_by_another_work_item"
        ),
    },
]


def git(*arguments: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(REPOSITORY), *arguments],
        check=True,
        capture_output=True,
    ).stdout


def revision(specification: str) -> str:
    return git("rev-parse", "--verify", specification).decode().strip()


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def source(commit: str, path: str) -> bytes:
    return git("show", f"{commit}:{path}")


def extract_stage(archive: bytes, destination: Path) -> None:
    """일반 파일과 디렉터리만 허용한 상대 경로에 꺼냅니다."""
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as stream:
        for member in stream:
            relative = PurePosixPath(member.name)
            if relative.is_absolute() or ".." in relative.parts or relative.parts[0] != "stage":
                raise ValueError(f"archive path is outside stage: {member.name}")
            if not (member.isdir() or member.isfile()):
                raise ValueError(f"archive contains a special entry: {member.name}")
            path = destination.joinpath(*relative.parts)
            if member.isdir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                handle = stream.extractfile(member)
                if handle is None:
                    raise ValueError(f"archive file has no contents: {member.name}")
                path.write_bytes(handle.read())
                path.chmod(member.mode & 0o777)


def tree_manifest(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): digest(path.read_bytes())
        for path in sorted((root / "stage").rglob("*"))
        if path.is_file()
    }


def manifest_digest(manifest: dict[str, str]) -> str:
    encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    return digest(encoded)


def run_condition(
    case: dict[str, str], archive: bytes, version: str, target_content: bytes
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="review-reuse-") as temporary:
        root = Path(temporary)
        extract_stage(archive, root)
        archive_manifest = tree_manifest(root)
        (root / case["target"]).write_bytes(target_content)
        before_manifest = tree_manifest(root)
        command = [sys.executable, "-B", "-m", "unittest", case["test"], "-v"]
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["PYTHONHASHSEED"] = "0"
        started = time.monotonic()
        result = subprocess.run(
            command,
            cwd=root / "stage/scripts/tests",
            env=environment,
            capture_output=True,
            text=True,
            timeout=120,
        )
        after_manifest = tree_manifest(root)
        changed_paths = sorted(
            path for path in before_manifest.keys() | archive_manifest.keys()
            if before_manifest.get(path) != archive_manifest.get(path)
        )
        return {
            "version": version,
            "command": command,
            "cwd_relative": "stage/scripts/tests",
            "elapsed_seconds": time.monotonic() - started,
            "returncode": result.returncode,
            "stdout": result.stdout.replace(str(root), "<temporary-extraction>"),
            "stderr": result.stderr.replace(str(root), "<temporary-extraction>"),
            "archive_stage_sha256": manifest_digest(archive_manifest),
            "tested_stage_sha256": manifest_digest(before_manifest),
            "after_test_stage_sha256": manifest_digest(after_manifest),
            "file_count": len(before_manifest),
            "changed_from_archive": changed_paths,
            "test_file_sha256": before_manifest[case["test_file"]],
            "target_sha256": before_manifest[case["target"]],
            "source_tree_unchanged_by_test": before_manifest == after_manifest,
        }


def prepare() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    fixtures: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for case in CASES:
        commit = revision(f"{case['commit']}^{{commit}}")
        parent = revision(f"{commit}^")
        before = source(parent, case["target"])
        after = source(commit, case["target"])
        archive = git("archive", "--format=tar", commit, "stage/")
        provenance = {
            "commit": commit,
            "parent": parent,
            "target": case["target"],
            "test": case["test"],
            "test_file": case["test_file"],
            "support_files_revision": commit,
            "before_target_blob": revision(f"{parent}:{case['target']}"),
            "after_target_blob": revision(f"{commit}:{case['target']}"),
        }
        fixtures.append({
            "id": case["id"],
            "title": case["title"],
            "criterion": case["criterion"],
            "versions": {
                "before": {"files": {case["target"]: before.decode("utf-8")}},
                "after": {"files": {case["target"]: after.decode("utf-8")}},
            },
            "provenance": provenance,
        })
        good = run_condition(case, archive, "after", after)
        bad = run_condition(case, archive, "before", before)
        verified = (
            good["returncode"] == 0
            and bad["returncode"] == 1
            and "Ran 1 test" in good["stderr"]
            and "\nOK\n" in good["stderr"]
            and "Ran 1 test" in bad["stderr"]
            and "FAILED (failures=1)" in bad["stderr"]
            and good["test_file_sha256"] == bad["test_file_sha256"]
            and good["changed_from_archive"] == []
            and bad["changed_from_archive"] == [case["target"]]
            and good["source_tree_unchanged_by_test"]
            and bad["source_tree_unchanged_by_test"]
        )
        records.append({
            "id": case["id"],
            **provenance,
            "commit_tree": revision(f"{commit}^{{tree}}"),
            "parent_tree": revision(f"{parent}^{{tree}}"),
            "commit_stage_tree": revision(f"{commit}:stage"),
            "parent_stage_tree": revision(f"{parent}:stage"),
            "archive_sha256": digest(archive),
            "regression_verified": verified,
            "runs": [good, bad],
        })
    report = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": (
            "각 수정 커밋의 stage 전체 트리와 그 커밋의 고정된 검사 한 개를 사용했습니다. "
            "수정 전 조건에서는 대상 파일 하나만 부모 버전으로 바꿨습니다. "
            "원래 커밋 당시 실행 로그가 아니라 새로 복원한 실험입니다."
        ),
        "python": sys.version,
        "platform": platform.platform(),
        "git_version": git("--version").decode().strip(),
        "repository_head": revision("HEAD"),
        "prepare_sha256": digest(Path(__file__).read_bytes()),
        "case_count": len(records),
        "run_count": sum(len(record["runs"]) for record in records),
        "all_regressions_verified": all(record["regression_verified"] for record in records),
        "cases": records,
    }
    return fixtures, report


def main() -> int:
    fixtures, report = prepare()
    for name, value in (("fixtures.json", fixtures), ("regression-results.json", report)):
        (OUTPUT / name).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps({
        "cases": report["case_count"],
        "runs": report["run_count"],
        "all_regressions_verified": report["all_regressions_verified"],
    }, ensure_ascii=False))
    return 0 if report["all_regressions_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

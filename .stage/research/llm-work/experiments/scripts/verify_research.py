"""연구 문서의 링크와 기록 파일을 읽기 전용으로 검사합니다."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
import re
from urllib.parse import unquote


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    errors: list[str] = []
    links = 0
    markdown = list(root.rglob("*.md"))
    for path in markdown:
        content = path.read_text(encoding="utf-8")
        if len(re.findall(r"^```", content, re.MULTILINE)) % 2:
            errors.append(f"닫히지 않은 코드 블록: {path}")
        for link in re.findall(r"\]\(([^)]+)\)", content):
            if re.match(r"[a-z]+://", link):
                continue
            relative, _, anchor = unquote(link).partition("#")
            target = (path.parent / relative).resolve() if relative else path
            links += 1
            if not target.exists():
                errors.append(f"없는 링크: {path}: {link}")
            elif anchor and target.suffix == ".md":
                target_text = target.read_text(encoding="utf-8")
                if f'id="{anchor}"' not in target_text:
                    errors.append(f"명시한 앵커 없음: {path}: {link}")
    json_files = [path for path in root.rglob("*.json") if ".obsidian" not in path.parts]
    for path in json_files:
        json.loads(path.read_text(encoding="utf-8"))
    scripts = list(root.rglob("*.py"))
    for path in scripts:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    for path in [*markdown, *scripts, *json_files]:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.rstrip() != line:
                errors.append(f"줄 끝 공백: {path}:{number}")
            if re.search(r"[\u3040-\u30ff]", line):
                errors.append(f"일본어 문자 확인 필요: {path}:{number}")
    experiments = root / "llm-work" / "experiments"
    for suite in ("followup", "repaired"):
        folder = experiments / "runs" / f"2026-10-05-{suite}"
        manifest_path = folder / "manifest.json"
        if not manifest_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text())
        for filename, expected in manifest["source_hashes"].items():
            actual = hashlib.sha256((experiments / filename).read_bytes()).hexdigest()
            if actual != expected:
                errors.append(f"실행 전 파일 해시와 다름: {filename}")
        expected_ids = {f'{s["case"]}--{s["condition"]}--{s["repeat"]}'
                        for s in manifest["schedule"]}
        actual_ids = {path.stem for path in folder.glob("*--*.json")}
        if expected_ids != actual_ids:
            errors.append(f"실행 기록 수집 미완료: {suite}: {len(actual_ids)}/{len(expected_ids)}")
        for path in folder.glob("*--*.json"):
            record = json.loads(path.read_text(encoding="utf-8"))
            expected = hashlib.sha256(
                (record["system_prompt"] + "\n" + record["prompt"]).encode()).hexdigest()
            if record["input_sha256"] != expected:
                errors.append(f"실행 입력 해시 불일치: {path}")
    print(json.dumps({"markdown": len(markdown), "internal_links": links,
                      "json": len(json_files), "python": len(scripts),
                      "errors": errors}, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

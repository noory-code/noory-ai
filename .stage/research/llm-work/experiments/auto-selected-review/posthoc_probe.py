"""실험 뒤 원본을 읽어 추가 모델 호출 없이 알 수 있었던 사실을 확인합니다."""

import json
from pathlib import Path
import re
import time

from common import BASE, ROOT, digest, function_index, save
from run import cases


def explicit_names(text: str, names: list[str]) -> list[str]:
    # 한국어 조사가 식별자 바로 뒤에 붙어도 코드 이름을 찾습니다.
    return [name for name in names if re.search(
        r"(?<![A-Za-z0-9_])" + re.escape(name) + r"(?![A-Za-z0-9_])", text)]


def main() -> None:
    rows = []
    for case in cases():
        started = time.perf_counter()
        for name, source in case["files"].items():
            names = [row["name"] for row in function_index(source)]
            mentioned = explicit_names(case["criterion"], names)
            smaller = [name for name in names
                       if len(BASE.select_source(source, name)["source"]) < len(source)]
            rows.append({"case": case["id"], "file": name, "source_sha256": digest(source.encode()),
                         "top_level_functions": len(names), "explicit_names_in_criterion": mentioned,
                         "entries_producing_smaller_source": smaller,
                         "all_entries_keep_full_source": bool(names) and not smaller,
                         "seconds": time.perf_counter() - started})
    save(ROOT / "posthoc-probe.json", {"after_model_experiment": True, "rows": rows,
        "source_sha256": digest(Path(__file__).read_bytes()),
        "limits": ["모델 비교가 끝난 뒤 추가로 확인했습니다. 세 번째 비교 조건의 결과가 아닙니다.",
                   "기준에 함수 이름이 나온다는 사실만으로 일반적인 검토 시작점을 확정할 수는 없습니다.",
                   "모든 시작점의 소스를 비교한 시간이며 실제 운영에 연결한 선택기의 시간은 아닙니다."]})
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

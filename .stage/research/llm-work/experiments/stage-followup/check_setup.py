"""모델을 호출하기 전에 임시 Stage 카드의 생성과 구조를 확인합니다."""

from pathlib import Path
import subprocess
import sys
import tempfile

import prepare as P


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="stage-followup-setup-") as directory:
        root = Path(directory)
        setup = P.setup(root, P.H.CASES[0], "claude", "codex")
        audit = subprocess.run([sys.executable, str(P.REPO / "stage/scripts/audit_stage.py"),
                                "--project-root", str(root)], text=True, capture_output=True)
        P.H.save(P.ROOT / "preparation-check.json", {"setup": setup, "audit": {
            "returncode": audit.returncode, "stdout": audit.stdout, "stderr": audit.stderr}})
        print(audit.stdout)
        print(audit.stderr)
        if audit.returncode:
            raise SystemExit(audit.returncode)


if __name__ == "__main__":
    main()

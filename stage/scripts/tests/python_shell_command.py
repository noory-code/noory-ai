"""Build fixture commands without passing Python syntax through the shell."""
import base64
import os
import shlex
import subprocess
import sys


def python_command(code: str) -> str:
    encoded = base64.b64encode(code.encode("utf-8")).decode("ascii")
    args = [sys.executable, "-c", f"import base64;exec(base64.b64decode('{encoded}'))"]
    return subprocess.list2cmdline(args) if os.name == "nt" else shlex.join(args)

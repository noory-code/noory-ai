"""Give every git command a test starts one throwaway global configuration.

Starting a process is the dominant cost of the scripts suite on Windows, and git
adds processes the tests never asked for: each commit spawns
`git maintenance run --auto`, a developer's signing setup spawns a signer per
commit, and fixtures spend two `git config` calls per repository on an identity.
The configuration written here turns automatic maintenance and signing off and
supplies that identity once, so a fixture repository needs no setup calls. It
also keeps a developer's own global settings (hooks paths, signing, aliases) out
of the tests. Repository-level settings a test writes still take precedence.

`GIT_CONFIG_GLOBAL` needs Git 2.32 or newer. The system configuration stays in
effect on purpose: Git for Windows sets `core.autocrlf` there, and the tests run
against the line-ending behavior a Windows user gets.
"""

from __future__ import annotations

import atexit
import os
import shutil
import tempfile
from pathlib import Path

TEST_GIT_USER_NAME = "Stage Test"
TEST_GIT_USER_EMAIL = "stage-test@example.com"

_ACTIVE_ROOT: Path | None = None


def render_git_config(template_dir: Path) -> str:
    # Git reads backslashes in a quoted value as escapes, so a Windows path is
    # written with forward slashes, which Git accepts on every platform.
    template = template_dir.as_posix().replace('"', '\\"')
    return (
        "[user]\n"
        f"\tname = {TEST_GIT_USER_NAME}\n"
        f"\temail = {TEST_GIT_USER_EMAIL}\n"
        "[maintenance]\n"
        "\tauto = false\n"
        "[gc]\n"
        "\tauto = 0\n"
        "[commit]\n"
        "\tgpgsign = false\n"
        "[tag]\n"
        "\tgpgsign = false\n"
        "[init]\n"
        f'\ttemplateDir = "{template}"\n'
    )


def isolate_git_config() -> Path:
    """Point this process and its children at the test configuration; return its path.

    Idempotent: every test module may call it, and the first call wins for the
    whole run because the environment is process-wide.
    """

    global _ACTIVE_ROOT
    if _ACTIVE_ROOT is not None:
        return _ACTIVE_ROOT / "gitconfig"
    root = Path(tempfile.mkdtemp(prefix="stage-test-git-"))
    atexit.register(shutil.rmtree, str(root), True)
    # `git init` copies its template into every new repository. Git's default
    # template is a dozen sample hooks no test runs; keep the layout tests write
    # into (an empty hooks directory and info/exclude) without the samples.
    template_dir = root / "template"
    (template_dir / "hooks").mkdir(parents=True)
    (template_dir / "info").mkdir(parents=True)
    (template_dir / "info" / "exclude").write_text("", encoding="utf-8")
    config_path = root / "gitconfig"
    config_path.write_text(render_git_config(template_dir), encoding="utf-8")
    os.environ["GIT_CONFIG_GLOBAL"] = str(config_path)
    _ACTIVE_ROOT = root
    return config_path

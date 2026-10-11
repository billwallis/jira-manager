import pathlib
import subprocess
import sys
from typing import Sequence

BIN = pathlib.Path(sys.executable).parent
EXE = str(BIN / "jira-manager")


def _run(args: Sequence[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        (EXE, *args),
        capture_output=True,
        **kwargs,
    )


def test__cli__can_print_version():
    proc = _run(("--version",))
    assert proc.returncode == 0
    assert proc.stdout == b"jira-manager 0.0.0\n"


def test__cli__no_args_prints_help():
    proc = _run([])
    help_ = _run(("--help",))
    assert proc.returncode == 0
    assert proc.stdout == help_.stdout


def test__cli__cmd_project_is_not_implemented():
    proc = _run(("project", "foo"), check=False)
    assert proc.returncode == 1
    assert proc.stdout == b"error: not implemented\n"

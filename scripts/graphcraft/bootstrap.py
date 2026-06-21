"""Ensure GraphStack + Graphify are available for graphcraft init."""

from __future__ import annotations

import subprocess
import sys

PIP_SPEC = "MertCapkin_GraphStack[graphify]>=4.7,<5"
PIP_SPEC_GIT = (
    "MertCapkin_GraphStack[graphify] @ git+https://github.com/MertCapkin/GraphStack.git"
)


def _echo(msg: str) -> None:
    print(msg, flush=True)


def find_python() -> list[str]:
    return [sys.executable]


def graphstack_available() -> bool:
    try:
        import graphstack  # noqa: F401
        return True
    except ImportError:
        pass
    proc = subprocess.run(
        [*find_python(), "-m", "graphstack", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode == 0


def pip_install(*specs: str, quiet: bool = True) -> int:
    if not specs:
        return 0
    cmd = [*find_python(), "-m", "pip", "install", "--upgrade"]
    if quiet:
        cmd.append("--quiet")
    cmd.extend(specs)
    _echo(f"  pip install {' '.join(specs)}")
    return subprocess.run(cmd, check=False).returncode


def ensure_graphstack(*, install: bool = True) -> bool:
    if graphstack_available():
        return True
    if not install:
        return False
    _echo("")
    _echo("Installing GraphStack (MertCapkin_GraphStack[graphify])...")
    rc = pip_install(PIP_SPEC)
    if rc != 0:
        _echo("PyPI install failed — trying GitHub...")
        rc = pip_install(PIP_SPEC_GIT)
    return rc == 0 and graphstack_available()


def run_graphstack_init(target: str, *, non_interactive: bool, install_deps: bool) -> int:
    cmd = [*find_python(), "-m", "graphstack", "init", target]
    if non_interactive:
        cmd.append("-y")
    if install_deps:
        cmd.append("--install-deps")
    return subprocess.run(cmd, check=False).returncode

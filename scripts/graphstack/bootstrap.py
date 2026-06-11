"""Dependency bootstrap helpers for one-shot ``graphstack init``."""

from __future__ import annotations

import subprocess

from .platform_utils import echo, find_python, graphify_available

# PyPI distribution name (``graphstack`` was taken). CLI command remains ``graphstack``.
PIP_SPEC = "MertCapkin_GraphStack[graphify]"
PIP_SPEC_GIT = (
    "MertCapkin_GraphStack[graphify] @ git+https://github.com/MertCapkin/GraphStack.git"
)


def pip_install(*specs: str, quiet: bool = True) -> int:
    """Install packages with the same Python running graphstack."""
    if not specs:
        return 0
    cmd = [*find_python(), "-m", "pip", "install", "--upgrade"]
    if quiet:
        cmd.append("--quiet")
    cmd.extend(specs)
    echo(f"  pip install {' '.join(specs)}")
    return subprocess.run(cmd, check=False).returncode


def ensure_graphify(*, install: bool = True) -> bool:
    if graphify_available():
        return True
    if not install:
        return False
    echo("")
    echo("Installing Graphify (graphifyy)...")
    rc = pip_install("graphifyy>=0.7,<0.9")
    return rc == 0 and graphify_available()


def ensure_graphstack_from_git() -> int:
    """Fallback when PyPI package is not published yet."""
    echo("Trying GitHub install (PyPI fallback)...")
    return pip_install(PIP_SPEC_GIT)


def run_graphify_cursor_install() -> int:
    if not graphify_available():
        return 1
    cmd = [*find_python(), "-m", "graphify", "cursor", "install"]
    proc = subprocess.run(cmd, check=False)
    return proc.returncode

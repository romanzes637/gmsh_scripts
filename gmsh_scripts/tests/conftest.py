import sys
import subprocess
from pathlib import Path

import pytest


@pytest.fixture()
def run(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    python = sys.executable
    p = Path(request.param)
    args = [python, '-m', 'gmsh_scripts', str(p)]
    result = subprocess.run(args)
    return result.returncode


@pytest.fixture()
def plot(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    python = sys.executable
    p = Path(request.param)
    args = [python, '-m', 'gmsh_scripts', str(p), '--plot']
    result = subprocess.run(args)
    return result.returncode

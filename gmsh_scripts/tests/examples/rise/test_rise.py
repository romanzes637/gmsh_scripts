import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("plot", ["cube.yml"], indirect=True)
def test_plot_cube(plot):
    assert plot == 0


@pytest.mark.parametrize("run", ["cube.yml"], indirect=True)
def test_cube(run):
    assert run == 0


def test_generate_random_cube():
    result = subprocess.run([sys.executable, 'random_cube.py'])
    assert result.returncode == 0


@pytest.mark.parametrize("run", ["random_cube.yml"], indirect=True)
def test_random_cube(run):
    assert run == 0

import pytest

@pytest.mark.parametrize("run", ["cube.json"], indirect=True)
def test_cube(run):
    assert run == 0

import pytest


@pytest.mark.parametrize("run", ["tetrahedron.json"], indirect=True)
def test_tetrahedron(run):
    assert run == 0


@pytest.mark.parametrize("run", ["cube.json"], indirect=True)
def test_cube(run):
    assert run == 0


@pytest.mark.parametrize("run", ["pyramid.json"], indirect=True)
def test_pyramid(run):
    assert run == 0


@pytest.mark.parametrize("run", ["octahedron.json"], indirect=True)
def test_octahedron(run):
    assert run == 0


@pytest.mark.parametrize("run", ["dodecahedron.json"], indirect=True)
def test_dodecahedron(run):
    assert run == 0


@pytest.mark.parametrize("run", ["icosahedron.json"], indirect=True)
def test_icosahedron(run):
    assert run == 0


@pytest.mark.parametrize("run", ["multi.json"], indirect=True)
def test_multi(run):
    assert run == 0

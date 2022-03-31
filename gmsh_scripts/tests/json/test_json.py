import pytest


@pytest.mark.parametrize("plot", ["container.json"], indirect=True)
def test_plot(plot):
    assert plot == 0


@pytest.mark.parametrize("run", ["container.json"], indirect=True)
def test_run(run):
    assert run == 0



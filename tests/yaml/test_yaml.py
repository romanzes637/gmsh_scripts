import pytest


@pytest.mark.parametrize("plot", ["container.yml"], indirect=True)
def test_plot_action(plot):
    assert plot == 0


@pytest.mark.parametrize("run", ["container.yml"], indirect=True)
def test_action(run):
    assert run == 0




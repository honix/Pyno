"""This contains e.g. fixtures that supply reusable elements."""

import pytest

import pyno.runner


@pytest.fixture
def window():
    """Supply a window, as that will probably be useful quite often."""
    return pyno.runner.create_window()

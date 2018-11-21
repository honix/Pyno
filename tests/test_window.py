"""Tests for pyno.window"""
import pyglet

from pyno import runner


def test_app_run():
    pyglet.clock.schedule_once(lambda x: pyglet.app.exit(), 0.1)
    runner.run()


def test_get_window(window):
    # Check some meaningful things
    assert window.caption == 'Pyno'
    assert window.active_nodes == []



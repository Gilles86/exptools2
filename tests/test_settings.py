"""Tests that do not need a window (no display required)."""
import os.path as op
from types import SimpleNamespace

import yaml

import exptools2
from exptools2.core.session import _merge_settings
from exptools2.core.trial import _get_quit_key

DEFAULTS = op.join(op.dirname(exptools2.__file__), "data", "default_settings.yml")


def load_defaults():
    with open(DEFAULTS, encoding="utf8") as f:
        return yaml.safe_load(f)


def test_default_settings_are_packaged():
    settings = load_defaults()
    for section in ("preferences", "window", "monitor", "mouse", "keyboard", "eyetracker", "mri"):
        assert section in settings
    assert settings["keyboard"]["quit_key"] == "q"
    assert settings["mouse"]["setup"] is True


def test_merge_settings_is_recursive():
    default = load_defaults()
    _merge_settings(default, {"window": {"size": [800, 600]}, "custom": {"a": 1}})
    assert default["window"]["size"] == [800, 600]
    assert default["window"]["fullscr"] is True  # untouched sibling key survives
    assert default["custom"] == {"a": 1}


def test_quit_key_default_and_override():
    assert _get_quit_key(SimpleNamespace(settings={})) == "q"
    assert _get_quit_key(SimpleNamespace()) == "q"
    assert _get_quit_key(SimpleNamespace(settings={"keyboard": {"quit_key": "escape"}})) == "escape"
    assert _get_quit_key(SimpleNamespace(settings={"keyboard": {"quit_key": None}})) is None

"""End-to-end smoke test: opens a small PsychoPy window, runs a few trials,
and checks the output files.

It needs a display, so it only runs when EXPTOOLS2_DISPLAY_TESTS=1, e.g.

    EXPTOOLS2_DISPLAY_TESTS=1 pytest tests/test_smoke.py
"""
import os

import pandas as pd
import pytest
import yaml

pytestmark = pytest.mark.skipif(
    os.environ.get("EXPTOOLS2_DISPLAY_TESTS") != "1",
    reason="needs a display; set EXPTOOLS2_DISPLAY_TESTS=1",
)


def _settings(tmp_path, **extra):
    settings = {
        "window": {"size": [400, 300], "fullscr": False, "units": "pix"},
        "monitor": {"name": "exptools2_test", "width": 30, "distance": 60},
        "mri": {"simulate": False},
    }
    settings.update(extra)
    path = tmp_path / "settings.yml"
    path.write_text(yaml.safe_dump(settings))
    return str(path)


def _run(tmp_path, settings_file, fake_keys=None):
    from psychopy import event
    from psychopy.visual import TextStim

    from exptools2.core import Session, Trial

    class SmokeTrial(Trial):
        def __init__(self, session, trial_nr, **kwargs):
            super().__init__(session, trial_nr, phase_durations=(0.1, 0.1),
                             phase_names=("stim", "iti"),
                             parameters={"condition": trial_nr % 2}, **kwargs)
            self.txt = TextStim(session.win, text=str(trial_nr))

        def draw(self):
            if self.phase == 0:
                self.txt.draw()

    session = Session("sub-test", output_dir=str(tmp_path / "logs"),
                      settings_file=settings_file)
    if fake_keys is not None:
        calls = iter(fake_keys)
        orig = event.getKeys
        event.getKeys = lambda *a, **k: next(calls, [])
    # Build trials *before* start_experiment(): the session timer starts
    # there, so time spent creating stimuli afterwards eats into phase 0.
    trials = [SmokeTrial(session, trial_nr, verbose=False) for trial_nr in range(3)]
    try:
        session.start_experiment()
        for trial in trials:
            trial.run()
        session.close()
    finally:
        if fake_keys is not None:
            event.getKeys = orig
    return session


def test_session_writes_outputs(tmp_path):
    override = tmp_path / "override.yml"
    override.write_text(yaml.safe_dump({"window": {"color": [-1, -1, -1]}, "custom": {"x": 1}}))
    session = _run(tmp_path, [_settings(tmp_path), str(override)])
    assert session.settings["custom"] == {"x": 1}
    assert session.settings["window"]["color"] == [-1, -1, -1]
    assert session.settings["window"]["size"] == [400, 300]  # from the first file
    out = tmp_path / "logs"
    events = pd.read_csv(out / "sub-test_events.tsv", sep="\t")
    # real key presses (the window grabs focus) are logged as responses
    events = events[events["event_type"] != "response"]
    assert len(events) == 6  # 3 trials x 2 phases
    assert list(events["event_type"]) == ["stim", "iti"] * 3
    assert set(events["condition"]) == {0, 1}
    # first phase is ~1 frame shorter (start-flip compensation)
    assert events["duration"].between(0.07, 0.15).all()
    assert events["onset"].iloc[-1] == pytest.approx(0.5, abs=0.05)  # non-slip
    assert (out / "sub-test_expsettings.yml").exists()
    assert (out / "sub-test_frames.pdf").exists()
    assert session.mouse is not None  # default: mouse is set up


def test_quit_key_can_be_disabled(tmp_path):
    # 'q' arrives during the first trial; with quit_key: null it is logged
    # as a normal response instead of ending the experiment.
    settings = _settings(tmp_path, keyboard={"quit_key": None}, mouse={"setup": False})
    session = _run(tmp_path, settings, fake_keys=[[("q", 0.05)]])
    events = pd.read_csv(tmp_path / "logs" / "sub-test_events.tsv", sep="\t")
    assert (events["response"] == "q").sum() == 1
    assert (events["event_type"] != "response").sum() == 6
    assert session.mouse is None


def test_default_quit_key_closes_and_quits(tmp_path):
    # Default behaviour (unchanged): 'q' inside a trial writes the (partial)
    # events file via session.close() and then exits through core.quit().
    with pytest.raises(SystemExit):
        _run(tmp_path, _settings(tmp_path), fake_keys=[[], [("q", 0.05)]])
    events = pd.read_csv(tmp_path / "logs" / "sub-test_events.tsv", sep="\t")
    assert len(events) >= 1

# Session

```python
from exptools2.core import Session

session = Session(output_str, output_dir=None, settings_file=None)
```

| Argument | Meaning |
|---|---|
| `output_str` | Prefix of every output file, e.g. `'sub-01_ses-1_task-risk_run-1'`. Use BIDS entities so the files can go straight into a BIDS dataset. |
| `output_dir` | Where output goes. Default: `./logs` (relative to the *current working directory*, not the script). Created if needed. |
| `settings_file` | A YAML file, or a list of YAML files merged in order, on top of exptools2's defaults. See [Settings](settings.md). |

The constructor, in order:

1. loads and merges the settings, writes them to `<output_str>_expsettings.yml`, and
   applies the `preferences` section to `psychopy.prefs`;
2. creates a PsychoPy `Monitor` from `monitor:` (with `window.size` as pixel size) and
   saves it;
3. opens the `Window` from `window:` and measures the frame rate;
4. computes `width_deg` and `pix_per_deg` (see [Display](display.md));
5. creates the mouse from `mouse:`;
6. opens a PsychoPy log file `<output_str>_log.txt` (level EXP);
7. creates `default_fix` (a small white circle, 0.075 units radius) and, if
   `mri.simulate` is true, a simulated scanner.

## Attributes you will use

| Attribute | |
|---|---|
| `win` | the PsychoPy `Window` |
| `settings` | the merged settings `dict`; add your own sections to the YAML and read them here |
| `clock` | session clock; 0 at `start_experiment()`. All onsets in the log use it. |
| `timer` | phase timer used by `Trial.run()`; do not reset it yourself |
| `actual_framerate` | measured refresh rate (Hz); falls back to `1 / win.monitorFramePeriod` |
| `width_deg`, `pix_per_deg` | screen width in degrees of visual angle and pixels per degree |
| `mouse` | a `psychopy.event.Mouse`, or `None` with `mouse: {setup: False}` |
| `default_fix` | a fixation dot you can `draw()` |
| `mri_trigger` | the key the scanner sends (`mri.sync`, default `t`) |
| `global_log` | the log as a pandas DataFrame (written to disk in `close()`) |
| `output_dir`, `output_str` | as given |

## Methods

`start_experiment(wait_n_triggers=None, show_fix_during_dummies=True)`
: Resets `clock` and `timer` and starts recording frame intervals. With
  `wait_n_triggers=n` it then shows `default_fix` and blocks until `n` scanner
  triggers (`mri.sync` key) have arrived, and resets the phase timer again; the session
  clock keeps the time of the first call. See [MRI](mri.md).

`display_text(text, keys=None, duration=None, **kwargs)`
: Draws a `TextStim` and waits for one of `keys` *or* for `duration` seconds. Nothing
  is logged. Fine before `start_experiment()`; inside the experiment use an
  instruction [trial](trials.md#instruction-screens) instead, so the screen is logged.

`close()`
: Flips once more to time-stamp the end, computes durations, writes
  `<output_str>_events.tsv` and `<output_str>_frames.pdf`, stops the MRI simulator and
  closes the window. Safe to call twice. **Always call it** (also in a `finally:`),
  because nothing is written before. See [Logging](logging.md).

`quit()`
: `close()` (if needed) and `psychopy.core.quit()`, which exits Python.

## A Session subclass

The usual pattern: the subclass builds stimuli once, creates all trials up front, and
runs them.

```python
from exptools2.core import Session

class TaskSession(Session):
    def __init__(self, output_str, settings_file, n_trials=20, **kwargs):
        super().__init__(output_str, settings_file=settings_file, **kwargs)
        self.n_trials = n_trials
        self.stimulus = MyStimulus(self.win, **self.settings['stimulus'])  # build once

    def create_trials(self):
        self.trials = [MyTrial(self, i, ...) for i in range(self.n_trials)]

    def run(self):
        self.create_trials()        # before start_experiment(): see Trials > timing
        self.start_experiment()
        try:
            for trial in self.trials:
                trial.run()
        finally:
            self.close()
```

If you use `load_next_during_phase` (see [Trials](trials.md#loading-the-next-trial-during-a-phase)),
the session must have a `create_trial(trial_nr)` method instead.

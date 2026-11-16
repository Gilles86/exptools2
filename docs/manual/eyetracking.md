# Eye tracking (EyeLink)

`PylinkEyetrackerSession` is a `Session` that also connects to an SR Research EyeLink
through `pylink`, calibrates it with PsychoPy graphics, records, and fetches the EDF
file at the end.

```python
from exptools2.core import PylinkEyetrackerSession

class TaskSession(PylinkEyetrackerSession):
    def __init__(self, output_str, output_dir, settings_file, eyetracker_on=True):
        super().__init__(output_str, output_dir=output_dir,
                         settings_file=settings_file, eyetracker_on=eyetracker_on)
        ...

    def run(self):
        if self.eyetracker_on:
            self.calibrate_eyetracker()       # EyeLink setup screen: C, V, Enter, Esc
        self.start_recording_eyetracker()
        self.start_experiment()
        try:
            for trial in self.trials:
                trial.run()
        finally:
            self.close()                      # stops recording, fetches the EDF
```

Unlike `Session`, `output_dir` and `settings_file` are required arguments here.

## Install

`pip install sr-research-pylink` (or the `eyetracker` extra), or install the wheel that
comes with the EyeLink Developers Kit. Without pylink you can still import exptools2 and
use `eyetracker_on=False` (you get a warning at import). `eyetracker_on=True` without
pylink raises an `ImportError`.

## What it does

- **Connect** to `eyetracker.address` (default `100.1.1.1`, the usual EyeLink host IP),
  open an EDF file named `HH_MM_SS.edf` on the host (EyeLink file names are limited to
  8 characters + extension), and send every `eyetracker.options` entry as a
  `key = value` command (sampling rate, calibration type, active eye, file and link
  filters, ...).
- **`calibrate_eyetracker()`** opens the EyeLink setup screen on the stimulus window
  (camera image, calibration, validation). Calibration target size: `eyetracker.dot_size`
  (deg). Does nothing when the eye tracker is off.
- **`start_recording_eyetracker()` / `stop_recording_eyetracker()`**: start before the
  task (and before `start_experiment()`), stop is done by `close()`.
- **Messages.** With `eyetracker_on=True`, every phase onset sends
  `start_type-stim_trial-<trial_nr>_phase-<phase>` and every key press sends
  `start_type-<response|pulse>_trial-<n>_phase-<p>_key-<key>_time-<t>` to the EDF.
  The EyeLink status line shows `trial <n>`. These MSG lines are how you cut the gaze
  data into trials and phases later. Add your own with
  `self.session.tracker.sendMessage('...')`.
- **`close()`** writes the events file, then stops recording, and copies the EDF from the
  host to `<output_dir>/<output_str>.edf`. Copying a long recording takes several
  seconds; do not kill the program.

## Settings

```yaml
eyetracker:
  address: '100.1.1.1'
  dot_size: 0.1          # deg
  options:
    active_eye: left     # or right
    binocular_enabled: NO
    sample_rate: 1000    # 500 in many fMRI setups
    calibration_type: HV9  # HV5 for a small screen in the scanner
    pupil_size_diameter: YES
    file_event_filter: 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
    ...
```

Options are merged with the defaults like everything else, so you only list what
differs. To run the same task without the tracker (laptop, behavioural lab), pass
`eyetracker_on=False` from a command-line flag rather than changing classes.

## Analysing the data

Convert the EDF with SR Research's `edf2asc`, find the `MSG` lines above for trial and
phase onsets, and convert gaze from pixels to degrees with the screen geometry stored
in that run's `_expsettings.yml` (`window.size`, `monitor.width`, `monitor.distance`),
not with assumed values.

# Logging and output files

All files go to `output_dir` (default `./logs`) and start with `output_str`:

| File | Written | Content |
|---|---|---|
| `_expsettings.yml` | in the constructor | merged settings |
| `_log.txt` | continuously | PsychoPy log (level EXP): warnings, dropped frames, framerate |
| `_events.tsv` | **in `close()` only** | the event log |
| `_frames.pdf` | in `close()` | frame intervals with the expected interval (red) and twice it (dashed) |
| `.edf` | in `close()`, eye-tracker sessions | EyeLink data, see [Eye tracking](eyetracking.md) |

## events.tsv

One row per **phase onset** and one per **key press** (including scanner pulses),
in the order they happened, indexed by `trial_nr`:

| Column | Meaning |
|---|---|
| `trial_nr` | trial number |
| `onset` | seconds on the session clock (0 = `start_experiment()`) |
| `event_type` | phase name for phase rows; `response` for key presses; `pulse` for the `mri.sync` key |
| `phase` | phase index (for responses: the phase during which the key was pressed) |
| `response` | the key name (response and pulse rows) |
| `nr_frames` | phase rows: number of frames the phase lasted |
| `duration` | phase rows: time until the next phase onset (the last phase: until `close()`) |
| `onset_abs` | `onset` plus the clock time at `start_experiment()` |
| *your parameters* | every entry of `trial.parameters`, see below |

Lists and arrays in `parameters` are spread over columns `name_   0`, `name_   1`, ...
(the index is formatted with `%4i`, so the column names contain spaces).

Onsets are logged on the screen flip (`win.callOnFlip`), so a phase onset is the time
the first frame of that phase was shown.

### Parameters are copied at the time a row is written { #parameters }

`trial.parameters` is copied into a row at the moment that row is written: at the phase
onset (for phase rows) or at the key press (for response rows). Changing a parameter
later does not change rows already written. So if you store the choice in
`self.parameters['choice']` during the choice phase, it appears in the response row
that ended the phase and in the rows of later phases, but not in the row of the choice
phase itself. To read results per trial, take the last row of each trial, or add a
short phase after the response phase (e.g. feedback) whose onset row then carries the
response.

## When the file is written

`events.tsv` exists only after `session.close()`. If Python crashes before that, the
run's events are lost (the `_log.txt` and the `.edf` are not enough to rebuild them).
Protect yourself:

- call `close()` in a `finally:` block;
- keep runs short (one run per process, see [Running in the UZH Econ labs](econ-labs.md));
- for long behavioural sessions, also write your own per-trial backup (e.g. append
  `self.session.global_log` rows to a CSV at the end of each trial).

The `q` key closes the session (writing a partial `events.tsv`) and exits; see
[Keyboard](responses.md#the-quit-key).

## Checking a new task

1. Run a few trials with a windowed settings file.
2. Open the first `_events.tsv`: one row per phase, the responses where you expect
   them, parameters in the right rows, durations close to the planned ones.
3. Look at `_frames.pdf` on the real machine: intervals above the dashed line are
   dropped frames.

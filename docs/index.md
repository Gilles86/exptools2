# exptools2

exptools2 is a thin framework on top of [PsychoPy](https://www.psychopy.org/) for
psychophysics and fMRI experiments. It takes care of the parts every experiment needs
and that are easy to get subtly wrong:

- **Non-slip timing.** A trial is a list of *phases* with durations; phase onsets are
  timed against one session clock and logged on the actual screen flip.
- **Logging.** Every phase onset, key press and MRI pulse ends up as a row in a
  BIDS-style `*_events.tsv`, together with the trial's parameters.
- **Settings.** One YAML file per setup (laptop, behavioural lab, scanner) controls
  window, monitor geometry, MRI and eye-tracker options; the merged settings are saved
  next to the data.
- **MRI triggers** (wait for dummy scans, log pulses) and **EyeLink eye tracking**
  (`PylinkEyetrackerSession`: calibration, recording, EDF transfer).

You still write the stimuli and the trial logic in plain PsychoPy. exptools2 only owns
the window, the clocks, the trial loop and the log.

This is the version the Ruff group uses: the fork
[Gilles86/exptools2](https://github.com/Gilles86/exptools2) of
[VU-Cog-Sci/exptools2](https://github.com/VU-Cog-Sci/exptools2). It is a drop-in
replacement for both; see [Changes in this fork](changes.md).

## Install

exptools2 does **not** install PsychoPy for you (PsychoPy is big and often installed
by conda or a standalone installer). Put both in your project. With
[uv](https://docs.astral.sh/uv/):

```toml
# pyproject.toml of your experiment
[project]
name = "mytask"
version = "0.1.0"
requires-python = "==3.10.*"
dependencies = ["exptools2", "psychopy>=2026.1"]

[tool.uv]
package = false

[tool.uv.sources]
exptools2 = { git = "https://github.com/Gilles86/exptools2", rev = "<commit>" }
```

Then `uv sync` and `uv run python task.py`. Pin `rev` to a commit so every participant
runs the same code; commit `uv.lock`.

Other ways:

```bash
uv pip install "exptools2 @ git+https://github.com/Gilles86/exptools2@<commit>"
pip install "exptools2[psychopy] @ git+https://github.com/Gilles86/exptools2@<commit>"   # also installs PsychoPy
pip install -e path/to/exptools2                                                         # a git submodule
```

Extras: `psychopy` (PsychoPy itself), `eyetracker` (SR Research `pylink`), `docs`, `test`.
PsychoPy 2023.2 to 2026.2 are known to work; Python 3.10 is the safest choice for
PsychoPy.

## A minimal experiment

Five trials: a fixation dot, a number, then up to two seconds to press `f` or `j`.

```python
--8<-- "examples/minimal.py"
```

Run it with `python minimal.py` (full screen, exptools2's default settings) or
`python minimal.py settings.yml` with your own [settings](manual/settings.md). Press
`q` to abort. Afterwards `logs/` contains:

| File | Content |
|---|---|
| `sub-01_task-numbers_run-1_events.tsv` | one row per phase onset and per key press, with `number` in every row |
| `sub-01_task-numbers_run-1_expsettings.yml` | the settings actually used |
| `sub-01_task-numbers_run-1_log.txt` | PsychoPy's log (warnings, dropped frames) |
| `sub-01_task-numbers_run-1_frames.pdf` | frame intervals, to spot dropped frames |

Next: the [manual](manual/index.md), and the [known traps](traps.md) before you run
real participants.

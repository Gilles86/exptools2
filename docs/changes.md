# Changes in this fork

[Gilles86/exptools2](https://github.com/Gilles86/exptools2) started as a fork of
[VU-Cog-Sci/exptools2](https://github.com/VU-Cog-Sci/exptools2) (Tomas Knapen, Lukas
Snoek and contributors) and contains everything in its `master` branch. It is meant
as a drop-in replacement for both: experiments written for either should run
unchanged.

## 0.2.0 (consolidated)

- `settings_file` can be a list of YAML files, merged in order (per-setup overrides).
- `keyboard.quit_key` setting (default `q`; `null` disables).
- `mouse.setup` works: `session.mouse` is a `Mouse` by default, `None` with
  `setup: False` (it used to crash with `setup: True` and be `None` otherwise).
- A warning when a phase is named `response`, `trigger` or `pulse`.
- `eyetracker_on=True` without pylink raises a clear `ImportError`;
  `calibrate_eyetracker()` is a no-op with the eye tracker off.
- Packaging: `pyproject.toml`; light dependencies; PsychoPy as the `psychopy` extra.
- Tests (`tests/`), this documentation.

## Earlier fork-only changes (2022–2024)

- `mouse.setup` option (see above).
- Frame rate falls back to the nominal monitor rate if it cannot be measured.
- `Clock.add` (deprecated in PsychoPy) replaced by `Clock.addTime`.
- Removed the hard `requirements.txt`/`install_requires` (install PsychoPy yourself).

# Known traps

Things that have cost people data or days. Each links to the manual section with
details. Items marked **fixed** behave better since the consolidated fork (0.2.0); the
others are how exptools2 works and are unlikely to change, because existing
experiments rely on them.

### events.tsv is written only in `close()`

A crash, a killed process or a closed terminal before `session.close()` loses the
whole run's event log. Use `try: ... finally: session.close()`, keep runs short (one
run per process) and consider a per-trial backup of your own.
→ [Logging](manual/logging.md#when-the-file-is-written)

### Parameters are copied when a row is written

`trial.parameters` is copied into the log at each phase onset and key press. A value
you set later in the trial (the choice, the reward) is not in the rows written before.
Read per-trial results from the last row of each trial, or from a phase that starts
after the response.
→ [Logging](manual/logging.md#parameters)

### `q` quits from inside every trial

It closes the session (a *partial* `events.tsv` is written) and exits Python. A
participant typing a `q`, or a launcher that only checks whether `events.tsv` exists,
turns this into silent data loss. **Fixed:** configurable with
`keyboard: {quit_key: ...}`; `null` disables it. The default is still `q`.
→ [Keyboard](manual/responses.md#the-quit-key)

### Reserved phase names { #reserved-phase-names }

`close()` treats rows whose `event_type` is `response`, `trigger` or `pulse` as key
presses. A *phase* with one of these names gets no `duration`, the phase before it
absorbs its duration, and `nr_frames` shift. Name phases e.g. `choice` or
`wait_trigger`. Exptools2 now logs a warning when you do this; the output itself is
unchanged.

### `window.size` vs display scaling

With display scaling (Windows 125 %, macOS "looks like"), `window.size` must be the
resolution the OS reports, not the panel's physical resolution, or every size in
degrees is off. Keep one settings file per setup and record the measured width and
distance.
→ [Display](manual/display.md)

### Work done after `start_experiment()` shortens the first phase

The timer starts in `start_experiment()`. Building trials or stimuli after that call is
taken out of the first phase (0.5 s became 0.04 s in a test). Create all trials before
`start_experiment()`.
→ [Trials](manual/trials.md#timing-what-to-do-before-start_experiment)

### `stop_phase()` resets the timer

After a self-paced phase, timing restarts from the moment `stop_phase()` was called.
That is what you want for instructions and responses, but it means the run is no
longer locked to the scanner clock. Re-sync to a trigger if needed.
→ [MRI](manual/mri.md)

### `draw()` runs before `get_events()`

State reset in `get_events()` is seen one frame late. Reset per-trial state at the
start of the phase in `draw()`.
→ [Trials](manual/trials.md#the-frame-loop)

### Keys pressed before the start

Keys in PsychoPy's buffer before `start_experiment()` are logged in the first frame
with negative onsets. Call `psychopy.event.clearEvents()` before starting.

### The scanner sync key must be a string

`mri.sync: 5` in YAML is an integer and never equals the key name `'5'`: write
`sync: '5'`.
→ [MRI](manual/mri.md)

### Settings changed after construction are not saved

`_expsettings.yml` is written inside `Session.__init__`. Values you put into
`session.settings` later are not in it.
→ [Settings](manual/settings.md)

### `preferences.general.audioLib` has no effect

The defaults set `audioLib` under `general`, but current PsychoPy reads
`prefs.hardware['audioLib']`, and `exptools2.core` imports `psychopy.sound` before the
settings are read anyway. To choose an audio backend, set
`psychopy.prefs.hardware['audioLib'] = [...]` in your script **before** importing
exptools2 (or psychopy.sound).

### `session.mouse` setting crashed (fixed)

In the fork before 0.2.0, `mouse: {setup: True}` raised `TypeError` and without it
`session.mouse` was `None`. **Fixed:** `session.mouse` is a `Mouse` by default (as in
upstream exptools2), `setup: False` gives `None`.

### Eye tracker without pylink (fixed)

`eyetracker_on=True` without pylink installed used to fail later with an
`AttributeError` on `None`. **Fixed:** it now raises an `ImportError` that says what
to install.

### `argparse --help` and PsychoPy

Importing PsychoPy can swallow command-line arguments such as `--help`. Parse your
arguments before importing exptools2 or psychopy.

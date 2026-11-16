# Trials, phases and timing

```python
from exptools2.core import Trial

Trial(session, trial_nr, phase_durations, phase_names=None, parameters=None,
      timing='seconds', load_next_during_phase=None, verbose=True,
      draw_each_frame=True)
```

| Argument | Meaning |
|---|---|
| `trial_nr` | goes into the `trial_nr` column of the log |
| `phase_durations` | one duration per phase, in seconds (or frames, see below); `np.inf` = until `stop_phase()` |
| `phase_names` | names written to `event_type` in the log (default: all `'stim'`). **Do not use `response`, `trigger` or `pulse`** (see [traps](../traps.md#reserved-phase-names)). |
| `parameters` | dict copied into every log row of this trial (condition, stimulus values, ...) |
| `timing` | `'seconds'` (default) or `'frames'` |
| `load_next_during_phase` | index of the phase during which `session.create_trial(trial_nr + 1)` is called |
| `verbose` | print phase onsets to the console |
| `draw_each_frame` | if False, `run()` does not flip; your `draw()` must call `self.session.win.flip()` itself |

You implement `draw()`; `self.phase` tells you which phase is running.

## The frame loop

`trial.run()` does, for each phase:

```text
win.callOnFlip(log_phase_info)            # the onset is logged on the next flip
timer.addTime(-duration)                  # timer counts up from -duration to 0
while timer.getTime() < 0 and not stopped:
    self.draw()
    win.flip()                            # first flip of the phase -> onset logged
    self.get_events()
```

Consequences:

- **`draw()` runs before `get_events()`** in each frame. State you reset in
  `get_events()` is seen by `draw()` one frame late; reset per-phase state at the start
  of the phase in `draw()` instead (e.g. `if self.phase == 2 and self.response is None: ...`).
- **Non-slip timing.** The timer is not reset between phases: every phase ends at the
  sum of all durations so far, measured from `start_experiment()`. A frame that is late
  in one phase is taken out of the next one, so the run does not drift. The actual
  onsets are in the log; compare them with the planned ones.
- A phase ends at the first flip *after* its time is up, so durations are rounded up to
  whole frames (at 60 Hz, 0.5 s is 30 frames; 0.51 s becomes 31 frames = 0.517 s).
  Choose durations that are multiples of the frame duration.
- `stop_phase()` ends the current phase after the current frame, **and resets the
  timer**: from then on timing restarts from that moment (needed for self-paced
  phases). `stop_trial()` ends the whole trial.
- The first phase of the first trial is shortened by 1.1 frames to make up for the
  flip done by `start_experiment()`.

## Timing: what to do before `start_experiment()`

The session timer starts in `start_experiment()`. Everything that happens between that
call and the first flip of the first trial (creating `TextStim`s, loading images,
building the trial list) is subtracted from the first phase. In a test, creating 5
trials after `start_experiment()` cut a 0.5 s first phase to 0.04 s. **Create all trials
first**, then call `start_experiment()`.

Likewise, building stimuli inside `draw()` is slow (a new `TextStim` per frame drops
frames). Build them in `__init__` and only change attributes (`.text`, `.pos`,
`.opacity`) in `draw()`.

## Seconds or frames

With `timing='frames'` all durations must be integers and count flips. This is exact
only if no frames are dropped; on a lab PC with a reliable display and `waitBlanking`,
it is the most precise way to show brief stimuli. `load_next_during_phase` only works
with `timing='seconds'`.

## Self-paced phases and instruction screens { #instruction-screens }

A phase of `np.inf` lasts until you call `stop_phase()`:

```python
class InstructionTrial(Trial):
    def __init__(self, session, trial_nr, text, keys=('space',), **kwargs):
        super().__init__(session, trial_nr, phase_durations=[np.inf],
                         phase_names=['instruction'], **kwargs)
        self.text = TextStim(session.win, text=text, wrapWidth=20)
        self.keys = keys

    def draw(self):
        self.text.draw()

    def get_events(self):
        events = super().get_events()
        if any(key in self.keys for key, t in events):
            self.stop_phase()
```

Instruction trials are logged like any other trial, so you can see later how long
participants read.

## Responses that end a phase

Override `get_events()`, call `super().get_events()` (that logs the keys), and act on
the returned `[(key, time), ...]` list. Example: a choice phase that ends on `f`/`j`
and stores the choice:

```python
def get_events(self):
    events = super().get_events()
    if self.phase == 2:
        for key, t in events:
            if key in ('f', 'j'):
                self.parameters['choice'] = key
                self.parameters['choice_time'] = t   # session clock, like 'onset'
                self.stop_phase()
```

The reaction time is `choice_time` minus the onset of the choice phase, both in the
log. (`self.start_trial` holds the onset of phase 0 of the running trial.)

Parameters set this way show up in log rows that are written **later** (the next phase
onset), not in the row of the phase in which they were set. See
[Logging](logging.md#parameters).

## Loading the next trial during a phase

If creating a trial takes long (large images), you can let exptools2 build trial
`n + 1` during a phase of trial `n`: pass `load_next_during_phase=k` and give your
session a method `create_trial(trial_nr)` that creates and stores that trial. A warning
is logged if loading takes longer than the phase.

## Drawing only when needed

With `draw_each_frame=False`, `run()` does not flip; your `draw()` decides when to call
`self.session.win.flip()`. Phase onsets are still logged at the next flip. Use this
for static screens where redrawing every frame is wasteful; for most tasks the default
is simpler.

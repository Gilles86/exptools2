# MRI triggers and scanner sync

Most scanners send a key press (Siemens at many sites: `5`; default here: `t`) at the
start of every volume. exptools2 uses it in two places.

## Settings

```yaml
mri:
  sync: '5'        # quote it: an unquoted 5 is an integer and never matches a key
  simulate: False  # True: psychopy's SyncGenerator sends fake triggers (testing)
  TR: 2.0          # used only by the simulator
  volumes: 10      # simulator
  skip: 0          # simulator: volumes without trigger at the start
  sound: False     # simulator: play scanner noise
```

## Waiting for the scanner

```python
session.start_experiment(wait_n_triggers=4)
```

resets the session clock, shows `default_fix`, and blocks until 4 `sync` keys have
arrived; then it resets the phase timer, so the first trial starts at the last
trigger. The session clock keeps counting from the call, so trial onsets in the log
are relative to the moment you called `start_experiment()`, not to the first trigger.
While it waits, nothing is logged and `q` does not work.

If you need the trigger onsets in the log (recommended for fMRI analyses that align to
the first volume), wait in a trial instead. The group's pattern is a trial with one
`np.inf` phase per expected trigger:

```python
class WaitForScannerTrial(Trial):
    def __init__(self, session, trial_nr, n_triggers=1, **kwargs):
        super().__init__(session, trial_nr,
                         phase_durations=[np.inf] * n_triggers,
                         phase_names=[f'trigger_{i + 1}' for i in range(n_triggers)],
                         **kwargs)
        self.last_trigger = -np.inf

    def draw(self):
        self.session.default_fix.draw()

    def get_events(self):
        events = super().get_events()
        for key, t in events:
            if key == self.session.mri_trigger and t - self.last_trigger > 0.5:
                self.last_trigger = t
                self.stop_phase()
        return events
```

Call `session.start_experiment()` (without `wait_n_triggers`), run this trial, then the
task trials. The phase onsets `trigger_1`, `trigger_2`, ... are logged, and the
`pulse` rows hold every trigger. The 0.5 s guard ignores a trigger that is reported
twice. Note that `stop_phase()` resets the timer, so the task's timing starts at the
last trigger.

## Pulses during the run

Every `sync` key that arrives while a trial runs is logged with
`event_type = 'pulse'`; it does not count as a response and does not change
`trial.last_resp`. Pulses let you check the TR and re-align onsets to the actual
volumes afterwards.

If the scanner's key collides with a response key on the button box, change the
response mapping, not the sync key.

## Testing without a scanner

Set `mri.simulate: True` to let PsychoPy's `SyncGenerator` press the sync key every
`TR` seconds once `start_experiment()` is called, or simply press the key yourself.

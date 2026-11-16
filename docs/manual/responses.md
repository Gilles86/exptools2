# Keyboard, mouse and responses

## Keys

`Trial.get_events()` reads all key presses since the last frame with
`psychopy.event.getKeys(timeStamped=session.clock)`, logs each of them (see
[Logging](logging.md)) and returns them as a list of `(key, time)` tuples. It also sets
`trial.last_resp` and `trial.last_resp_onset` (the scanner sync key excluded).

Override it to react to keys, and always call `super().get_events()` so the keys are
logged:

```python
def get_events(self):
    events = super().get_events()
    for key, t in events:
        if key in self.session.settings['keys']['choice']:
            ...
    return events
```

Notes:

- Key names are PsychoPy's (`'space'`, `'return'`, `'left'`, `'1'`, ...). Button boxes in
  scanners usually send number keys; put the mapping in the settings file per setup.
- `psychopy.event` keys are timed at the frame they are read, i.e. with up to one frame
  of delay. For millisecond-accurate reaction times use `psychopy.hardware.keyboard`
  (Psychtoolbox backend) in your own `get_events()`; you then have to log the keys
  yourself.
- Keys pressed **before** `start_experiment()` stay in PsychoPy's buffer and are logged in
  the first frame of the first trial with negative onsets. Call
  `psychopy.event.clearEvents()` right before `start_experiment()` if that matters.
- `getKeys()` empties the buffer: if you call `event.getKeys()` yourself somewhere else,
  those keys never reach the log.

## The quit key { #the-quit-key }

Pressing `q` inside any trial calls `session.close()` (which writes a partial
`events.tsv`) and then `session.quit()`, which exits Python. That is useful while
testing. In a real session it means that a participant who presses `q` ends the run,
and a launcher that checks whether `events.tsv` exists will think the run finished.

Change or disable it in the settings:

```yaml
keyboard:
  quit_key: escape   # or null to disable
```

Disable it in tasks where participants type text. (Before the consolidated fork the
key was hard-wired to `q`. Because `super().get_events()` reads the keys itself, the
only workaround there was not to call it and log the keys yourself.)

## Mouse

`session.mouse` is a `psychopy.event.Mouse` created from the `mouse:` settings
(default `visible: False`: the cursor is hidden, which is what you want in almost every experiment; set `visible: True` only for tasks that use the mouse). With `mouse: {setup: False}` it is `None` (the cursor
settings are still applied). Many tasks create their own instead:
`self.mouse = event.Mouse(visible=False)` in the Session subclass.

For a mouse-driven slider:

- remember the mouse position at the start of the response phase and move the marker
  only when the mouse moves, so the marker does not jump to where the mouse was left
  in the previous trial;
- reset the per-trial response state in `draw()` at the start of the phase, not in
  `get_events()` (one frame late);
- confirm with a click (`mouse.getPressed()[0]`) and ignore clicks in the first few
  hundred ms of the phase, so a click that ended the previous phase does not count.

Mouse clicks are not logged automatically. Store them in `parameters` (then they appear
in later rows), or add a log row yourself.

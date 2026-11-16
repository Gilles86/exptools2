# Settings

Settings are YAML. exptools2 starts from its own
[`default_settings.yml`](https://github.com/Gilles86/exptools2/blob/master/exptools2/data/default_settings.yml)
and merges your file(s) on top, recursively: a key you set replaces the default, keys you
leave out keep the default, and new sections (your task parameters) are simply added.
The result is `session.settings` and is saved as `<output_str>_expsettings.yml` next to
the data. Keep that file: it is the only record of screen size, distance and so on for
that run.

## The defaults

```yaml
preferences:          # applied to psychopy.prefs.<section>[<key>]
  general:
    audioLib: sounddevice   # has no effect in current PsychoPy, see Known traps
    units: deg              # default units of all stimuli

window:               # passed to psychopy.visual.Window(**window)
  size: [1440, 900]
  pos: [0, 0]
  color: [0, 0, 0]
  fullscr: True
  waitBlanking: True

monitor:              # passed to psychopy.monitors.Monitor(**monitor)
  name: default
  width: 50           # cm, visible width of the screen
  distance: 80        # cm, eye to screen
  gamma: 1

mouse:
  visible: False      # passed to psychopy.event.Mouse
  setup: True         # False: session.mouse is None (cursor still hidden)

keyboard:
  quit_key: q         # aborts the run from inside any trial; null disables

eyetracker:           # see Eye tracking
  address: '100.1.1.1'
  dot_size: 0.1       # deg, calibration target
  options: {...}      # sent to the EyeLink as "<key> = <value>" commands

mri:                  # see MRI
  simulate: False
  TR: 2.0
  volumes: 10
  sync: t             # key sent by the scanner trigger
  skip: 0
  sound: False
```

Everything under `window:` goes straight into `psychopy.visual.Window`, so you can add
any `Window` argument there (`screen: 1`, `winType: pyglet`, `useRetina: False`,
`checkTiming: False`, ...). The same holds for `monitor:` and `Monitor`.

## Your own parameters

Put task parameters in the same file, in your own sections, and read them from
`session.settings`:

```yaml
durations:
  fixation: 0.5
  stimulus: 0.6
  iti: [1.0, 1.5, 2.0]
stimulus:
  aperture_radius: 2.5   # deg
```

```python
d = self.settings['durations']
```

They are then saved with the data too.

## One file per setup

The screen, viewing distance, sync key and full-screen flag differ between your laptop,
the behavioural lab and the scanner; the task parameters do not. Keep a
`default.yml` with the task parameters and a windowed laptop setup, plus one small
override file per setup, and pass both. `settings_file` accepts a list that is merged in
order:

```python
Session(output_str, settings_file=['settings/default.yml', f'settings/{args.setup}.yml'])
```

```yaml
# settings/scanner.yml: only what differs
window:
  size: [1920, 1080]
  fullscr: True
  screen: 1
monitor:
  name: scanner_projector
  width: 69.8
  distance: 220
mri:
  sync: '5'
```

!!! note "Older versions"
    Before the consolidated fork, `settings_file` took one path only; projects merged
    their files themselves with `exptools2.core.session._merge_settings` and passed the
    result as a temporary file. That still works.

`_expsettings.yml` is written in the constructor. Values you add to `session.settings`
afterwards (`self.settings['subject'] = subject`, a command-line option) are available to
your code but are **not** in that file. Put what you need for the analysis in
`output_str` (subject, session, run) or in the trial `parameters`, which go into the log.

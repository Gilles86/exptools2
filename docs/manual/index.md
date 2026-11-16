# Manual

An exptools2 experiment has two kinds of objects:

- one **[Session](session.md)** per run: it reads the [settings](settings.md), opens the
  window, owns the clocks and collects the [log](logging.md). You subclass it to hold
  your stimuli and the list of trials.
- many **[Trials](trials.md)**: each trial is a sequence of timed *phases*. You subclass
  `Trial` and implement `draw()` (what is on screen in the current phase) and,
  optionally, `get_events()` (what to do with key presses).

```text
Session.__init__   settings -> monitor -> window -> mouse -> log file
   your code       build stimuli and trials           (before the clock starts!)
start_experiment() reset clocks [wait for n scanner triggers]
trial.run()        for each phase: draw() -> flip -> get_events() until time is up
   ...
close()            write events.tsv and frames.pdf, close the window
quit()             close() + core.quit()
```

The usual project layout:

```text
experiment/
├── pyproject.toml          # exptools2 + psychopy, pinned (see Home)
├── settings/
│   ├── default.yml         # task parameters + laptop window
│   ├── lab.yml             # overrides for the behavioural lab
│   └── scanner.yml         # overrides for the scanner (sync key, screen, distance)
├── session.py              # Session subclass: stimuli, create_trials(), run()
├── trial.py                # Trial subclasses
└── task.py                 # argparse -> Session(...) -> run()
```

Pages:

- [Session](session.md): constructor, attributes, `start_experiment`, `close`, `quit`.
- [Trials, phases and timing](trials.md): the frame loop, `stop_phase`, seconds vs frames, loading during a phase.
- [Settings](settings.md): YAML, the defaults, per-setup overrides.
- [Logging and output files](logging.md): what is in `events.tsv` and when it is written.
- [Keyboard, mouse and responses](responses.md).
- [MRI triggers and scanner sync](mri.md).
- [Eye tracking](eyetracking.md) with `PylinkEyetrackerSession`.
- [Display, degrees and scaling](display.md).
- [Running in the UZH Econ labs](econ-labs.md).

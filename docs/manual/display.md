# Display, degrees and scaling

By default all stimuli are in **degrees of visual angle** (`preferences.general.units:
deg`). PsychoPy converts degrees to pixels with three numbers from the settings:

| Setting | Meaning |
|---|---|
| `window.size` | resolution of the window in pixels |
| `monitor.width` | width of the visible screen area in cm |
| `monitor.distance` | eye-to-screen distance in cm |

Measure width and distance on each setup (the visible image, not the bezel; in the
scanner, the projection screen as seen through the mirror, and the distance from the
eyes via the mirror). Write the numbers into the setup's settings file with a comment on
how and when they were measured.

exptools2 also computes, for your own conversions:

```python
session.width_deg   = 2 * degrees(arctan(monitor.width / monitor.distance))
session.pix_per_deg = win.size[0] / session.width_deg
```

`width_deg` uses the full width (not twice the half-width angle); PsychoPy's own
conversion uses a small-angle approximation. The two agree closely for normal screens
and drift apart for very wide fields of view.

## Window size must match what the OS reports

`window.size` must be the resolution the operating system *reports* for that screen,
which with display scaling is not the physical resolution:

- **Windows** at 125 % scaling: a 2560 x 1440 screen reports 2048 x 1152.
- **macOS** "looks like 1440 x 900" on a Retina display: use 1440 x 900. PsychoPy
  renders at the physical resolution itself (`useRetina`, on by default) and may then
  report `win.size` at the physical resolution, which also doubles
  `session.pix_per_deg`. Print `session.win.size` once on a new machine and compare.

If `window.size` is wrong, the full-screen window is stretched or cropped, and every
size in degrees is off by the scaling factor. Check on each machine: Display settings →
resolution *and* scale. Then check a stimulus with a ruler once.

## Refresh rate

`session.actual_framerate` is measured when the window opens (falls back to the nominal
rate if the measurement fails) and is logged to `_log.txt`. Phase durations are rounded
up to whole frames, so design durations as multiples of the frame duration of the
setup you run on (e.g. 100 Hz lab screens: multiples of 10 ms). The `_frames.pdf` plot
shows whether frames were dropped.

## Several screens

`window.screen` selects the screen (0 = primary). In the scanner the projector is
usually the second screen; mirror or extend the displays as the site requires, and set
`fullscr: True`.

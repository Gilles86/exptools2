# Running in the UZH Econ labs

Practical notes for running exptools2 tasks on the behavioural-lab and scanner PCs of
the Department of Economics. Lab rules, bookings and the current PC setup are on the
lab's own pages; ask the lab staff for access. This page only covers what matters for
the code.

**Make the experiment self-contained.** The lab clients do not have PsychoPy, and
whatever Python is installed there may change. Ship a relocatable Python with your
experiment (e.g. `uv python install 3.10 --install-dir lab_python`, then install your
locked requirements into it). A `.venv` created elsewhere is *not* relocatable, so do
not copy one.

**Pin exptools2 to a commit without needing git.** Export your lock file
(`uv export --frozen --no-hashes`) and rewrite the git dependency to an archive URL:

```text
exptools2 @ https://github.com/Gilles86/exptools2/archive/<commit>.zip
```

**Never write logs into the mirrored experiment folder.** Experiment folders on the
clients are mirrored from a server, and mirroring deletes everything in the destination
that is not in the source. Point `output_dir` at a folder outside it (one the clients
can write to), and copy data off after every session.

**Check the display.** The client screens run at a high resolution and refresh rate;
with Windows display scaling the window size in your settings must be the *scaled*
resolution (see [Display](display.md)). Measure the viewing distance and put both into a
`lab.yml` override.

**One run per process.** Start each part (instructions, training, each run) as its own
Python process from a small launcher script. Every part then gets a fresh window and its
own events file, and a crash only costs one run.

**Disable or move the quit key** for sessions where participants type
(`keyboard: {quit_key: null}`), and make sure the launcher does not treat a run that
was aborted with `q` as complete.

**Test on a real client** at least two weeks before the first session: resolution,
refresh rate (`_frames.pdf`), fonts, key names, and where the output files end up.

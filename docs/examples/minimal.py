"""Minimal exptools2 experiment: fixation, a number, and a key response."""
import sys
import numpy as np
from psychopy.visual import TextStim
from exptools2.core import Session, Trial


class NumberTrial(Trial):
    def __init__(self, session, trial_nr, number):
        super().__init__(session, trial_nr,
                         phase_durations=[0.5, 1.0, 2.0],      # seconds
                         phase_names=['fixation', 'stimulus', 'choice'],
                         parameters={'number': number})          # logged in every row
        self.text = TextStim(session.win, text=str(number), height=1)  # 1 deg

    def draw(self):
        if self.phase == 1:
            self.text.draw()
        else:
            self.session.default_fix.draw()

    def get_events(self):
        events = super().get_events()                # logs every key press
        if self.phase == 2 and any(key in ('f', 'j') for key, t in events):
            self.stop_phase()                        # response ends the phase


settings = sys.argv[1] if len(sys.argv) > 1 else None
session = Session('sub-01_task-numbers_run-1', output_dir='logs', settings_file=settings)
trials = [NumberTrial(session, i, n) for i, n in enumerate(np.random.randint(1, 10, 5))]
session.start_experiment()
for trial in trials:
    trial.run()
session.close()   # writes logs/sub-01_task-numbers_run-1_events.tsv

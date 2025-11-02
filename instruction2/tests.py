from otree.api import Bot, Submission

# Import pages from __init__.py
from . import (
    Part2Intro,
    Decisions,
    ExamplesWaitPage,
    ComprehensionCheck,
    WaitToStart
)


class PlayerBot(Bot):
    def play_round(self):
        treatment = self.participant.treatment

        # Yield display pages (pages where user clicks "Next")
        yield Part2Intro
        yield Decisions

        # ExamplesWaitPage might not have a submit button - skip HTML check
        yield Submission(ExamplesWaitPage, {}, check_html=False)

        # Part 2 comprehension check answers
        answers = {}

        if treatment == 'BI':
            answers = {
                'q5_bi': 1,
                'q6_bi': 3,
                'q7_bi': 1,
            }
        elif treatment == 'BT':
            answers = {
                'q5_bt': 5,
                'q6_bt': 2,
            }

        # Yield ComprehensionCheck with answers (form page)
        yield ComprehensionCheck, answers

        # Don't yield WaitToStart (WaitPage - automatic)

        print(f"Bot {self.participant.code} completed Part 2 instructions ({treatment})")
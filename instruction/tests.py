from otree.api import Bot, Submission

# Import pages from __init__.py
from . import (
    Consent,
    Welcome,
    Part1Intro,
    Decisions,
    Examples,
    ExamplesWaitPage,
    ComprehensionCheck,
    WaitToStart
)


class PlayerBot(Bot):
    def play_round(self):
        treatment = self.participant.treatment

        # Yield display pages
        yield Consent
        yield Welcome
        yield Part1Intro
        yield Decisions
        yield Examples

        # ExamplesWaitPage might not have a submit button
        yield Submission(ExamplesWaitPage, {}, check_html=False)

        # Part 1 comprehension check - ONLY q1-q4 (same for all treatments)
        answers = {
            'q1': 1,  # True
            'q2': 2,  # The number of people who choose Box B
            'q3': 4,  # 15 ECU
            'q4': 2,  # Box A with YELLOW
        }

        # NO treatment-specific questions in Part 1!
        # Those are only in Part 2 (instruction2 app)

        # Yield ComprehensionCheck with answers
        yield ComprehensionCheck, answers

        # Don't yield WaitToStart (WaitPage - automatic)

        print(f"Bot {self.participant.code} completed Part 1 instructions ({treatment})")
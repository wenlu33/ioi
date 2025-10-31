from otree.api import Bot, expect
import random

# FIX: Import all your page classes directly from the __init__.py module
from . import (
    FormingGroupsWait,
    GenerateBallWaitPage,
    BallDrawPage,
    Choice,
    ResultsWaitPage,
    ResultsPage
)


class PlayerBot(Bot):
    """
    Bot for the congestion game.
    Randomly chooses Box A or Box B.
    """

    def play_round(self):

        # 1. Handle the FormingGroupsWait page (only for rounds > 1)
        #if self.player.round_number > 1:
            # yield FormingGroupsWait  # No 'pages.' prefix

        # 2. Pass through the ball draw pages
        # yield GenerateBallWaitPage  # No 'pages.' prefix
        yield BallDrawPage  # No 'pages.' prefix

        # 3. Make and submit the choice
        choice = random.choice(['A', 'B'])
        yield Choice, {'choice': choice}  # No 'pages.' prefix

        # 4. Pass through the ResultsWaitPage
        # yield ResultsWaitPage  # No 'pages.' prefix

        # 5. Pass through the ResultsPage (this sets the payoff)
        yield ResultsPage  # No 'pages.' prefix

        # --- Verification ---
        # 6. NOW check the payoff


        if choice == 'A':
            if self.group.box_a_color == 'YELLOW':
                expect(self.player.payoff, 30)
            else:
                expect(self.player.payoff, 10)
        else:
            expect(self.player.payoff, self.group.box_b_earnings)

        print(f"Bot {self.participant.code} Round {self.player.round_number}: "
              f"Chose {choice}, Payoff={self.player.payoff}")
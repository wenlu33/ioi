from otree.api import Bot, expect, Submission
import random

# Import page classes from __init__.py
from . import (
    FormingGroupsWait,
    GenerateBallWaitPage,
    BallDrawPage,
    RecommendationWaitPage,
    RecommendationPage,
    Choice,
    ResultsWaitPage,
    ResultsPage,
    FinalPayment
)


class PlayerBot(Bot):
    """
    Bot for Part 2: With treatments BI (information) or BT (incentive)
    - BI: Sometimes follows recommendation, sometimes doesn't
    - BT: No recommendation, just different payoffs
    """

    def play_round(self):
        treatment = self.participant.treatment

        # 1. Don't yield FormingGroupsWait (WaitPage - automatic)
        # 2. Don't yield GenerateBallWaitPage (WaitPage - automatic)

        # 3. Yield BallDrawPage (display page)
        yield BallDrawPage

        # 4. Don't yield RecommendationWaitPage (WaitPage - automatic, only for BI)

        # 5. Yield RecommendationPage if BI treatment (display page)
        if treatment == 'BI':
            yield RecommendationPage

        # 6. Decide choice
        if treatment == 'BI' and hasattr(self.player, 'recommendation') and self.player.recommendation:
            # Sometimes follow recommendation (70%), sometimes don't (30%)
            if random.random() < 0.7:
                choice = self.player.recommendation
            else:
                choice = 'B' if self.player.recommendation == 'A' else 'A'
        else:
            # BT treatment or no recommendation: choose randomly
            choice = random.choice(['A', 'B'])

        # 7. Yield Choice page with form data
        yield Choice, {'choice': choice}

        # 8. Don't yield ResultsWaitPage (WaitPage - automatic)

        # 9. Yield ResultsPage (display page)
        yield ResultsPage

        # 10. Verify payoff
        if choice == 'A':
            if self.group.box_a_color == 'YELLOW':
                expect(self.player.payoff, 30)
            else:
                expect(self.player.payoff, 10)
        else:
            expect(self.player.payoff, self.group.box_b_earnings)

        recommendation_text = getattr(self.player, 'recommendation', 'N/A')
        print(f"Bot {self.participant.code} Round {self.player.round_number} ({treatment}): "
              f"Recommendation={recommendation_text}, "
              f"Chose {choice}, Payoff={self.player.payoff}")

        # 11. Last round: Yield FinalPayment page (display page, no submit button)
        if self.player.round_number == 10:  # Change to 10 if using 10 rounds
            yield Submission(FinalPayment, {}, check_html=False)
            print(f"Bot {self.participant.code} FINAL PAYMENT: ${self.participant.payoff:.2f}")
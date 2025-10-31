from otree.api import Bot, expect
import random


class PlayerBot(Bot):
    """
    Bot for Part 2: With treatments BI (information) or BT (incentive)
    - BI: Sometimes follows recommendation, sometimes doesn't
    - BT: No recommendation, just different payoffs
    """

    def play_round(self):
        treatment = self.participant.treatment

        # BI treatment: Sometimes follow recommendation (70%), sometimes don't (30%)
        if treatment == 'BI' and hasattr(self.player, 'recommendation') and self.player.recommendation:
            if random.random() < 0.7:
                choice = self.player.recommendation
            else:
                choice = 'B' if self.player.recommendation == 'A' else 'A'
        else:
            # BT treatment or no recommendation: choose randomly
            choice = random.choice(['A', 'B'])

        # Make choice
        yield 'Choice', {'choice': choice}

        # Verify payoff
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

        # Last round: View final payment
        if self.player.round_number == self.player._Constants.NUM_ROUNDS:
            print(f"Bot {self.participant.code} FINAL PAYMENT: ${self.participant.payoff:.2f}")

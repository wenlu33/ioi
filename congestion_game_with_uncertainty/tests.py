from otree.api import Bot, expect
import random


class PlayerBot(Bot):
    """
    Bot for Part 1: Baseline game (3 rounds)
    Randomly chooses Box A or Box B
    """

    def play_round(self):
        # Make choice (randomly choose A or B)
        choice = random.choice(['A', 'B'])
        yield 'Choice', {'choice': choice}

        # Verify payoff was set correctly
        if choice == 'A':
            if self.group.box_a_color == 'YELLOW':
                expect(self.player.payoff, 30)
            else:
                expect(self.player.payoff, 10)
        else:
            # Box B payoff depends on congestion
            expect(self.player.payoff, self.group.box_b_earnings)

        print(f"Bot {self.participant.code} Round {self.player.round_number}: "
              f"Chose {choice}, Payoff={self.player.payoff}")

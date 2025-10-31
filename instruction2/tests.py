from otree.api import Bot


class PlayerBot(Bot):
    def play_round(self):
        # Instruction pages have no forms, oTree auto-advances bots through them
        pass

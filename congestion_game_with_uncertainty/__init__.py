from otree.api import *
import random

doc = """
Game with Guess → Choose → Group Result
"""

class C(BaseConstants):
    NAME_IN_URL = 'congestion_game_with_uncertainty'
    PLAYERS_PER_GROUP = 5
    NUM_ROUNDS = 5

class Subsession(BaseSubsession):
    def creating_session(subsession):
        pass
        # We don't set box_a_color here — moved to after_all_players_arrive!

class Group(BaseGroup):
    box_a_color = models.StringField()  # YELLOW or BLUE
    box_b_size = models.StringField()   # Small or Large
    box_b_earnings = models.FloatField()

class Player(BasePlayer):
    first_guess = models.IntegerField(label="Your guess about Yellow ball", min=0, max=100)
    choice = models.StringField(
        choices=[['A', 'Choose Box A'], ['B', 'Choose Box B']],
        widget=widgets.RadioSelect
    )

# ----------------- Pages -----------------
class BallDrawPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return True  # Always show Ball Draw page before guess

    @staticmethod
    def vars_for_template(player: Player):
        return dict()

class GuessPage1(Page):
    form_model = 'player'
    form_fields = ['first_guess']

class Choice(Page):
    form_model = 'player'
    form_fields = ['choice']

class ResultsWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        # 🎯 Randomly decide color of ball in Box A
        group.box_a_color = random.choice(['YELLOW', 'BLUE'])

        # 🎯 Set Box B size and earnings based on number of people choosing Box B
        set_group_results(group)

class ResultsPage(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        # Calculate payoff
        if player.choice == 'A':
            if group.box_a_color == 'YELLOW':
                earning = 3
            else:
                earning = 1
        else:
            earning = group.box_b_earnings

        players = group.get_players()
        num_box_b = sum(1 for p in players if p.choice == 'B')

        return dict(
            round_number=player.round_number,
            first_guess=player.first_guess,
            choice=player.choice,
            box_a_color=group.box_a_color,
            box_b_size=group.box_b_size,
            num_box_b=num_box_b,
            round_earnings=earning
        )

# ----------------- Functions -----------------

def set_group_results(group: Group):
    players = group.get_players()

    # Count how many chose Box B
    num_box_b = sum(1 for p in players if p.choice == 'B')

    # Determine box size
    if num_box_b > 2:
        group.box_b_size = 'Small'
    else:
        group.box_b_size = 'Large'

    # Set Box B earnings based on table
    payoff_table = {0: 3, 1: 2.5, 2: 2, 3: 1.5, 4: 1, 5: 0.5}
    group.box_b_earnings = payoff_table.get(num_box_b, 0)

# ----------------- Page Sequence -----------------

page_sequence = [BallDrawPage, GuessPage1, Choice, ResultsWaitPage, ResultsPage]
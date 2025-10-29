from otree.api import *
import random

doc = """
Game with Choose → Group Result
"""


class C(BaseConstants):
    NAME_IN_URL = 'congestion_game_with_uncertainty'
    PLAYERS_PER_GROUP = 5
    NUM_ROUNDS = 3


class Subsession(BaseSubsession):
    pass


# def creating_session(subsession):
#     # Set treatment in round 1
#     if subsession.round_number == 1:
#         for player in subsession.get_players():
#             treatment = subsession.session.config.get('treatment', 'BB')
#             player.participant.treatment = treatment
#
#     # Shuffle groups each round (except round 1)
#     if subsession.round_number > 1:
#         subsession.group_randomly()
#
#     # 🎯 Draw ball color BEFORE players see anything
#     for group in subsession.get_groups():
#         group.box_a_color = random.choice(['YELLOW', 'BLUE'])
#         # Removed: group.num_chose_box_b = 0  (not needed, initial=0 handles it)

def creating_session(subsession):
    # Don't set treatment here - it's already set in instruction app

    # Shuffle groups each round (except round 1)
    if subsession.round_number > 1:
        subsession.group_randomly()

    # Draw ball color BEFORE players see anything
    for group in subsession.get_groups():
        group.box_a_color = random.choice(['YELLOW', 'BLUE'])

class Group(BaseGroup):
    box_a_color = models.StringField()  # YELLOW or BLUE
    box_b_size = models.StringField()  # Small or Large
    box_b_earnings = models.FloatField(initial=0)  # ✅ Added initial value
    num_chose_box_b = models.IntegerField(initial=0)


class Player(BasePlayer):
    choice = models.StringField(
        choices=[['A', 'Choose Box A'], ['B', 'Choose Box B']],
        widget=widgets.RadioSelect
    )


# ----------------- Pages -----------------

class FormingGroupsWait(WaitPage):
    title_text = "Forming Groups"
    body_text = "Please wait while we form new groups for this round..."

    @staticmethod
    def is_displayed(player):
        return player.round_number > 1  # Show for rounds 2-10 (not round 1)

class BallDrawPage(Page):
    """Shows animation of ball being drawn (already drawn, just not revealed)"""

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            box_a_color=player.group.box_a_color  # Available if you want to show animation
        )


class Choice(Page):
    form_model = 'player'
    form_fields = ['choice']


class ResultsWaitPage(WaitPage):
    """Wait for all players, then calculate results"""

    @staticmethod
    def after_all_players_arrive(group: Group):
        # Ball color already set in creating_session
        # Just calculate Box B results
        set_group_results(group)


class ResultsPage(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        # Calculate earning
        if player.choice == 'A':
            if group.box_a_color == 'YELLOW':
                earning = 30
            else:
                earning = 10
        else:
            earning = group.box_b_earnings

        return dict(
            round_number=player.round_number,
            choice=player.choice,
            box_a_color=group.box_a_color,
            box_b_size=group.box_b_size,
            num_box_b=group.num_chose_box_b,
            round_earnings=earning
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # # ✅ SET THE PAYOFF (important!)
        # group = player.group
        #
        # if player.choice == 'A':
        #     if group.box_a_color == 'YELLOW':
        #         player.payoff = 30
        #     else:
        #         player.payoff = 10
        # else:
        #     player.payoff = group.box_b_earnings

        # Store Part 1 data for later payment calculation
        key = f'part1_round_{player.round_number}'
        player.participant.vars[key] = {
            'choice': player.choice,
            'box_a_color': player.group.box_a_color,
            'num_chose_b': player.group.num_chose_box_b,
            'box_b_earnings': player.group.box_b_earnings
        }


# ----------------- Functions -----------------

def set_group_results(group: Group):
    players = group.get_players()
    num_box_b = sum(1 for p in players if p.choice == 'B')
    group.num_chose_box_b = num_box_b

    if num_box_b > 2:
        group.box_b_size = 'Small'
    else:
        group.box_b_size = 'Large'

    # Check this table!
    payoff_table = {1: 25, 2: 20, 3: 15, 4: 10, 5: 5}
    group.box_b_earnings = payoff_table.get(num_box_b, 0)

    # ✅ Add debug here:
    print(f"DEBUG set_group_results: num_box_b={num_box_b}, box_b_earnings={group.box_b_earnings}")

# ----------------- Page Sequence -----------------

page_sequence = [FormingGroupsWait, BallDrawPage, Choice, ResultsWaitPage, ResultsPage]
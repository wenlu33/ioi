from otree.api import *
import random

doc = """
Game with Guess → Choose → Group Result (Part 2 for BI and BT Treatments)
"""


class C(BaseConstants):
    NAME_IN_URL = 'congestion_game_with_uncertainty2'
    PLAYERS_PER_GROUP = 5
    NUM_ROUNDS = 10  # 10 rounds total for each treatment


class Subsession(BaseSubsession):
    def creating_session(subsession):
        for group in subsession.get_groups():
            # Assign a random color for Box A (YELLOW or BLUE)
            group.box_a_color = random.choice(['YELLOW', 'BLUE'])

            # Make sure treatment is assigned (done in instruction app)
            for player in subsession.get_players():
                player.participant.treatment = player.participant.vars.get('treatment',
                                                                           'BB')  # Default to 'BB' if treatment not set


class Group(BaseGroup):
    box_a_color = models.StringField()  # YELLOW or BLUE
    box_b_size = models.StringField()  # Small or Large
    box_b_earnings = models.FloatField()


class Player(BasePlayer):
    first_guess = models.IntegerField(label="Your guess about Yellow ball", min=0, max=100)
    choice = models.StringField(
        choices=[['A', 'Choose Box A'], ['B', 'Choose Box B']],
        widget=widgets.RadioSelect
    )
    round_payoff = models.FloatField()  # Renamed 'payoff' to 'round_payoff'
    second_guess = models.IntegerField(min=0, max=100, blank=True)  # For BI treatment only


# ----------------- Pages -----------------
class BallDrawPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return True  # Always show Ball Draw page before guess

    @staticmethod
    def vars_for_template(player: Player):
        return dict()  # Just returns an empty dict

    def before_next_page(player, timeout_happened):
        # Assign box_a_color here during BallDrawPage
        player.group.box_a_color = random.choice(['YELLOW', 'BLUE'])  # Assign color for Box A


class GuessPage1(Page):
    form_model = 'player'
    form_fields = ['first_guess']


class Choice(Page):
    form_model = 'player'
    form_fields = ['choice']


# -------------- For BI and BT treatment pages ----------------
# This page only appears for BI treatment to show the Clue Ball.
class ClueBallPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 'BI'  # Only for BI treatment

    @staticmethod
    def vars_for_template(player: Player):
        # Construct the image URL based on the Clue Ball color
        clue_ball_image_url = f"congestion_game_with_uncertainty/images/{player.participant.clue_ball_color}_ball.png"

        # Return the variables to the template
        return {
            "clue_ball_color": player.participant.clue_ball_color,  # Pass the Clue Ball color
            "clue_ball_image_url": clue_ball_image_url,  # Pass the dynamically constructed URL
        }


class ClueBallDrawPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 'BI'  # Only for BI treatment

    @staticmethod
    def vars_for_template(player: Player):
        # Determine the color of Box A
        box_a_color = player.group.box_a_color

        # Now determine the Clue Ball color based on Box A color
        if box_a_color == 'YELLOW':
            # If Box A is Yellow, the Clue Ball is Yellow and comes from Clue Box X
            player.participant.clue_ball_color = 'yellow'  # Always yellow in this case
        else:
            # If Box A is Blue, the Clue Ball can either be Blue or Yellow (from Clue Box Y)
            # 1/3 chance for Yellow and 2/3 chance for Blue
            player.participant.clue_ball_color = random.choices(
                ['yellow', 'blue'],
                weights=[1, 2],  # Weighting 1 for yellow and 2 for blue
                k=1  # Generate a single random choice
            )[0]

        return {
            "box_a_color": box_a_color,
            "clue_ball_color": player.participant.clue_ball_color,
        }

    def before_next_page(player, timeout_happened):
        # The logic for choosing the Clue Ball color has already been executed in vars_for_template
        pass

# This page handles the second guess for BI treatment after the Clue Ball is shown
class SecondGuessPage(Page):
    form_model = 'player'
    form_fields = ['second_guess']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 'BI'  # Only for BI treatment

    @staticmethod
    def vars_for_template(player: Player):
        return {
            "box_a_color": player.group.box_a_color  # Show the color of Box A
        }

    def before_next_page(player, timeout_happened):
        # Store the second guess value
        player.second_guess = player.second_guess  # Ensure second_guess is saved


class ResultsWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        num_box_b = sum(1 for p in players if p.choice == 'B')

        # Assign box_b_size based on the number of players choosing Box B
        if num_box_b <= 2:
            group.box_b_size = 'Small'
        else:
            group.box_b_size = 'Large'

        # For BT treatment, modify payoff structure for Box B in Part 2
        treatment = players[0].participant.treatment  # All players in the group have the same treatment
        if treatment == 'BT':  # For BT treatment
            modified_payoff_table = {0: 2.5, 1: 2, 2: 1.5, 3: 1, 4: 0.5, 5: 0}
            group.box_b_earnings = modified_payoff_table.get(num_box_b, 0)
        else:
            # Standard payoff structure for Box B for BI and BB treatments
            payoff_table = {0: 3, 1: 2.5, 2: 2, 3: 1.5, 4: 1, 5: 0.5}
            group.box_b_earnings = payoff_table.get(num_box_b, 0)

        # Assign payoff to players based on choice
        for p in players:
            if p.choice == 'A':
                if group.box_a_color == 'YELLOW':
                    p.round_payoff = 3  # Renamed from 'payoff' to 'round_payoff'
                else:
                    p.round_payoff = 1  # Renamed from 'payoff' to 'round_payoff'
            else:
                p.round_payoff = group.box_b_earnings  # Renamed from 'payoff' to 'round_payoff'

class ResultsPage(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        players = group.get_players()
        num_box_b = sum(1 for p in players if p.choice == 'B')

        return dict(
            round_number=player.round_number,
            first_guess=player.first_guess,
            choice=player.choice,
            box_a_color=group.box_a_color,
            box_b_size=group.box_b_size,
            num_box_b=num_box_b,
            round_earnings=player.round_payoff,  # Renamed from 'payoff' to 'round_payoff'
            second_guess=player.second_guess  # Pass the second_guess value to ResultsPage
        )
# ----------------- Page Sequence -----------------
page_sequence = [BallDrawPage, GuessPage1,ClueBallDrawPage, ClueBallPage, SecondGuessPage, Choice, ResultsWaitPage, ResultsPage]
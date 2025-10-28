from otree.api import *
import random

doc = """
Part 2: With Recommendation Ball System
"""


class C(BaseConstants):
    NAME_IN_URL = 'congestion_game_with_uncertainty2'
    PLAYERS_PER_GROUP = 5
    NUM_ROUNDS = 10


class Subsession(BaseSubsession):
    pass


def creating_session(subsession):
    # Shuffle groups each round (except round 1)
    if subsession.round_number > 1:
        subsession.group_randomly()

    # ✅ Removed: group.num_chose_box_b = 0 (initial=0 in model handles this)


class Group(BaseGroup):
    box_a_color = models.StringField()  # YELLOW or BLUE
    box_b_size = models.StringField()  # Small or Large
    box_b_earnings = models.FloatField(initial=0)  # ✅ Added initial value
    num_chose_box_b = models.IntegerField(initial=0)


class Player(BasePlayer):
    recommendation = models.StringField()  # A or B
    choice = models.StringField(
        choices=[['A', 'Choose Box A'], ['B', 'Choose Box B']],
        widget=widgets.RadioSelect
    )


# ----------------- Pages -----------------

# class InstructionsWaitPage(WaitPage):
#     """Experimenter control: Wait after reading Part 2 instructions"""
#     title_text = "Please wait"
#     body_text = "You have finished reading the Part 2 instructions. Please wait for the experimenter to begin Part 2."
#
#     @staticmethod
#     def is_displayed(player: Player):
#         return player.round_number == 1


class FormingGroupsWait(WaitPage):
    title_text = "Forming Groups"
    body_text = "Please wait while we form new groups for this round..."

    @staticmethod
    def is_displayed(player):
        return player.round_number > 1  # Show for rounds 2-10 (not round 1)

class BallDrawPage(Page):
    """Shows animation of ball being drawn"""

    @staticmethod
    def vars_for_template(player: Player):
        return dict()


class RecommendationWaitPage(WaitPage):
    """
    CRITICAL: Generate ball color AND recommendations for ALL players together
    This ensures proper distribution (5 A's if YELLOW, or 3 A's + 2 B's if BLUE)
    """
    title_text = "Drawing Recommendation Balls..."
    body_text = "Please wait while the computer prepares your recommendation ball."

    @staticmethod
    def after_all_players_arrive(group: Group):
        # 🎯 First: Randomly determine Box A color (BEFORE recommendations)
        group.box_a_color = random.choice(['YELLOW', 'BLUE'])

        # Then: Generate recommendations based on color
        if group.box_a_color == 'YELLOW':
            # All 5 recommendation balls are "A"
            for player in group.get_players():
                player.recommendation = 'A'
        else:
            # BLUE: 3 balls labeled "A", 2 balls labeled "B"
            recommendations = ['A', 'A', 'A', 'B', 'B']
            random.shuffle(recommendations)  # Randomly distribute

            players = group.get_players()
            for i, player in enumerate(players):
                player.recommendation = recommendations[i]


class RecommendationPage(Page):
    """Shows the player their recommendation ball"""

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            recommendation=player.recommendation,
            round_number=player.round_number
        )


class Choice(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            recommendation=player.recommendation,
            round_number=player.round_number
        )


class ResultsWaitPage(WaitPage):
    """Wait for all players to make their choice, then calculate results"""

    @staticmethod
    def after_all_players_arrive(group: Group):
        # Box A color already set in RecommendationWaitPage
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
            recommendation=player.recommendation,
            choice=player.choice,
            box_a_color=group.box_a_color,
            box_b_size=group.box_b_size,
            num_box_b=group.num_chose_box_b,
            round_earnings=earning
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        key = f'part2_round_{player.round_number}'
        player.participant.vars[key] = {
            'choice': player.choice,
            'box_a_color': player.group.box_a_color,
            'num_chose_b': player.group.num_chose_box_b,
            'box_b_earnings': player.group.box_b_earnings
        }


class FinalPayment(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        import random

        # Get exchange rate from settings
        exchange_rate = player.session.config.get('exchange_rate', 0.5)

        # Total rounds: 10 from Part 1 + 10 from Part 2 = 20 rounds
        total_rounds = 20  # ✅ Changed from 6 to 20
        payment_round = random.randint(1, total_rounds)

        # Determine which part and get the player data
        if payment_round <= 10:  # ✅ Changed from 3 to 10
            # Payment from Part 1 (rounds 1-10)
            part = 1
            round_in_part = payment_round

            # Retrieve stored Part 1 data
            part1_data_key = f'part1_round_{round_in_part}'

            if part1_data_key in player.participant.vars:
                part1_data = player.participant.vars[part1_data_key]
                choice = part1_data['choice']
                box_a_color = part1_data['box_a_color']
                num_chose_b = part1_data['num_chose_b']
                box_b_earnings = part1_data['box_b_earnings']
                recommendation = None
            else:
                # Fallback if Part 1 data not found
                payment_round_player = player.in_round(1)
                choice = payment_round_player.choice
                box_a_color = payment_round_player.group.box_a_color
                num_chose_b = payment_round_player.group.num_chose_box_b
                box_b_earnings = payment_round_player.group.box_b_earnings
                recommendation = None
                part = 2
                round_in_part = 1
        else:
            # Payment from Part 2 (rounds 11-20)
            part = 2
            round_in_part = payment_round - 10  # ✅ Changed from 3 to 10
            payment_round_player = player.in_round(round_in_part)

            choice = payment_round_player.choice
            box_a_color = payment_round_player.group.box_a_color
            num_chose_b = payment_round_player.group.num_chose_box_b
            box_b_earnings = payment_round_player.group.box_b_earnings
            recommendation = payment_round_player.recommendation

        # Calculate earnings IN ECU
        if choice == 'A':
            if box_a_color == 'YELLOW':
                round_earnings_ecu = 30
            else:
                round_earnings_ecu = 10
        else:
            round_earnings_ecu = box_b_earnings

        # Convert ECU to dollars
        round_earnings_dollars = round_earnings_ecu * exchange_rate

        # # Calculate total payment (game + $3 survey)
        # participation_fee = 3
        # total_payment = round_earnings_dollars + participation_fee
        #
        # # ✅ Store TOTAL payment - ONLY TIME WE SET THIS
        # player.participant.payoff = total_payment

        # ❌ REMOVE THESE:
        # participation_fee = 3
        # total_payment = round_earnings_dollars + participation_fee
        # player.participant.payoff = total_payment

        # ✅ REPLACE WITH:
        player.participant.payoff = round_earnings_dollars
        # Return data to display (removed participation_fee and total_payment)
        return dict(
            payment_round=payment_round,
            part=part,
            round_in_part=round_in_part,
            round_earnings_ecu=round_earnings_ecu,
            round_earnings_dollars=round_earnings_dollars,
            exchange_rate=exchange_rate,
            box_a_color=box_a_color,
            choice=choice,
            num_chose_b=num_chose_b,
            recommendation=recommendation
        )
# class FinalPayment(Page):
#     @staticmethod
#     def is_displayed(player: Player):
#         return player.round_number == C.NUM_ROUNDS
#
#     @staticmethod
#     def vars_for_template(player: Player):
#         import random
#
#         # Get exchange rate from settings
#         exchange_rate = player.session.config.get('exchange_rate', 0.5)
#
#         # Total rounds: 10 from Part 1 + 10 from Part 2 = 20 rounds
#         total_rounds = 6
#         payment_round = random.randint(1, total_rounds)
#
#         # Determine which part and get the player data
#         if payment_round <= 3:
#             part = 1
#             round_in_part = payment_round
#             part1_data_key = f'part1_round_{round_in_part}'
#
#             if part1_data_key in player.participant.vars:
#                 part1_data = player.participant.vars[part1_data_key]
#
#                 choice = part1_data['choice']
#                 box_a_color = part1_data['box_a_color']
#                 num_chose_b = part1_data['num_chose_b']
#                 box_b_earnings = part1_data['box_b_earnings']
#                 recommendation = None
#             else:
#                 payment_round_player = player.in_round(1)
#                 choice = payment_round_player.choice
#                 box_a_color = payment_round_player.group.box_a_color
#                 num_chose_b = payment_round_player.group.num_chose_box_b
#                 box_b_earnings = payment_round_player.group.box_b_earnings
#                 recommendation = payment_round_player.recommendation
#                 part = 2
#                 round_in_part = 1
#         else:
#             part = 2
#             round_in_part = payment_round - 3
#             payment_round_player = player.in_round(round_in_part)
#             choice = payment_round_player.choice
#             box_a_color = payment_round_player.group.box_a_color
#             num_chose_b = payment_round_player.group.num_chose_box_b
#             box_b_earnings = payment_round_player.group.box_b_earnings
#             recommendation = payment_round_player.recommendation
#
#         # Calculate earnings IN ECU
#         if choice == 'A':
#             if box_a_color == 'YELLOW':
#                 round_earnings_ecu = 30
#             else:
#                 round_earnings_ecu = 10
#         else:
#
#             round_earnings_ecu = box_b_earnings
#
#         # Convert ECU to dollars
#         round_earnings_dollars = round_earnings_ecu * exchange_rate
#
#         # ✅ Store game earnings in participant.payoff (survey will add participation fee)
#         player.participant.payoff = round_earnings_dollars
#
#         return dict(
#             payment_round=payment_round,
#             part=part,
#             round_in_part=round_in_part,
#             round_earnings_ecu=round_earnings_ecu,
#             round_earnings_dollars=round_earnings_dollars,
#             exchange_rate=exchange_rate,
#             box_a_color=box_a_color,
#             choice=choice,
#             num_chose_b=num_chose_b,
#             recommendation=recommendation
#         )

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

page_sequence = [
    # InstructionsWaitPage,  # Round 1 only - experimenter control
FormingGroupsWait,
    BallDrawPage,  # Show ball being drawn
    RecommendationWaitPage,  # Generate ball color + recommendations
    RecommendationPage,  # Show YOUR recommendation ball
    Choice,  # Choose Box A or Box B
    ResultsWaitPage,  # Wait for all players
    ResultsPage,  # Show results
    FinalPayment  # Final payment (last round only)
]
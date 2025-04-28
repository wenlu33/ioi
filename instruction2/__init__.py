from otree.api import *
import random
import pagetime
doc = """
Instruction Page 2 for BI and BT treatments
"""


class C(BaseConstants):
    NAME_IN_URL = 'instruction2'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Fields for BI treatment
    q5_bi = models.IntegerField(
        choices=[
            [1, 'The ball in Box A is BLUE'],
            [2, 'The ball in Box A is YELLOW'],
            [3, 'The Clue Ball came from Clue Box X'],
            [4, 'Everyone in your group saw a blue Clue Ball']
        ],
        widget=widgets.RadioSelect,
        blank=True
    )

    q6_bi = models.IntegerField(
        choices=[
            [1, 'It selects one randomly each round'],
            [2, 'It’s based on your group number'],
            [3, 'It depends on the color of the ball in Box A'],
            [4, 'It’s different for each participant']
        ],
        widget=widgets.RadioSelect,
        blank=True
    )

    q7_bi = models.IntegerField(
        choices=[[1, 'True'], [2, 'False']],
        widget=widgets.RadioSelect,
        blank=True
    )

    # Fields for BT treatment
    q5_bt = models.IntegerField(
        choices=[
            [1, '3.0 ECU'],
            [2, '2.5 ECU'],
            [3, '2 ECU'],
            [4, '1.5 ECU'],
            [5, '1 ECU']
        ],
        widget=widgets.RadioSelect,
        blank=True
    )

    q6_bt = models.IntegerField(
        choices=[
            [1, 'The number of people in your group changes'],
            [2, 'The earning from Box B is lower than in Part 1 when the same number of people choose it'],
            [3, 'Box B now gives a fixed earning regardless of how many people choose it'],
            [4, 'The earning from Box B is higher when more people choose it']
        ],
        widget=widgets.RadioSelect,
        blank=True
    )
    time_consent = models.IntegerField()
    time_comprehension = models.IntegerField()
    time_decisions = models.IntegerField()
    time_examples = models.IntegerField()
    time_welcome = models.IntegerField()
    time_examples_wait = models.IntegerField()

# Pages

@pagetime.track
class Decisions(Page):

    @staticmethod
    def is_displayed(player: Player):
        # Only show for BI and BT treatments
        return player.participant.treatment in ['BI', 'BT']

    @staticmethod
    def vars_for_template(player: Player):
        treatment = player.participant.treatment
        exchange_rate = player.subsession.session.config['exchange_rate']
        return dict(treatment=treatment, exchange_rate=exchange_rate)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_decisions = pagetime.last(player.participant)


@pagetime.track
class Examples(Page):

    @staticmethod
    def is_displayed(player: Player):
        # Only show for BI and BT treatments
        return player.participant.treatment in ['BI', 'BT']

    @staticmethod
    def vars_for_template(player: Player):
        treatment = player.participant.treatment
        exchange_rate = player.subsession.session.config['exchange_rate']
        return dict(treatment=treatment, exchange_rate=exchange_rate)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_examples = pagetime.last(player.participant)


@pagetime.track
class ExamplesWaitPage(Page):

    @staticmethod
    def is_displayed(player: Player):
        # Only show for BI and BT treatments
        return player.participant.treatment in ['BI', 'BT']

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_examples_wait = pagetime.last(player.participant)

class ComprehensionCheck(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        # If treatment is 'BI' or 'BT', show the relevant fields for comprehension check
        treatment = getattr(player.participant, 'treatment', 'BB')  # Default to 'BB' if not set
        fields = []

        if treatment == 'BI':
            fields += ['q5_bi', 'q6_bi', 'q7_bi']
        elif treatment == 'BT':
            fields += ['q5_bt', 'q6_bt']

        return fields

    @staticmethod
    def vars_for_template(player):
        return dict(treatment=getattr(player.participant, 'treatment', 'BB'))

    @staticmethod
    def error_message(player: Player, values):
        solutions = {}

        treatment = player.participant.treatment
        if treatment == 'BI':
            solutions.update(
                q5_bi=1,
                q6_bi=3,
                q7_bi=1,
            )
        elif treatment == 'BT':
            solutions.update(
                q5_bt=5,
                q6_bt=2,
            )

        error_messages = {}

        for field_name in solutions:
            if values.get(field_name) != solutions[field_name]:
                error_messages[field_name] = 'The answer is incorrect. Please try again.'

        return error_messages

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_comprehension = pagetime.last(player.participant)


# Sequence of pages
page_sequence = [Decisions, Examples, ExamplesWaitPage, ComprehensionCheck]
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
            [3, 'Everyone in your group received the same Recommendation Ball'],
            [4, 'You know what Recommendation Ball others received'],
        ],
        widget=widgets.RadioSelect,
        blank=True
    )

    q6_bi = models.IntegerField(
        choices=[
            [1, 'It randomly selects the number of A and B labels each round'],
            [2, 'It depends on how many people chose Box B in the previous round'],
            [3, 'It depends on the unknown color of the ball in Box A'],
            [4, 'Each participant selects their own Recommendation Ball from a pile']
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
            [1, '30 ECU'],
            [2, '25 ECU'],
            [3, '20 ECU'],
            [4, '15 ECU'],
            [5, '10 ECU']
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
class Part2Intro(Page):
    @staticmethod
    def is_displayed(player):
        return True

@pagetime.track
class Decisions(Page):
    # ❌ REMOVE THIS ENTIRE METHOD:
    # @staticmethod
    # def is_displayed(player: Player):
    #     return player.participant.treatment in ['BI', 'BT']

    @staticmethod
    def vars_for_template(player: Player):
        treatment = player.participant.treatment
        exchange_rate = player.subsession.session.config['exchange_rate']
        return dict(treatment=treatment, exchange_rate=exchange_rate)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_decisions = pagetime.last(player.participant)



@pagetime.track
class ExamplesWaitPage(Page):
    # ❌ REMOVE THIS ENTIRE METHOD:
    # @staticmethod
    # def is_displayed(player: Player):
    #     return player.participant.treatment in ['BI', 'BT']

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_examples_wait = pagetime.last(player.participant)


class ComprehensionCheck(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        treatment = getattr(player.participant, 'treatment', 'BB')
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


class WaitToStart(WaitPage):
    title_text = "Please wait"
    body_text = "Please wait for all participants to complete the comprehension check. Part 2 will begin shortly."

    @staticmethod
    def is_displayed(player):
        return True  # Always show

page_sequence = [Part2Intro, Decisions, ExamplesWaitPage, ComprehensionCheck, WaitToStart]
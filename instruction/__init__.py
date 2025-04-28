from otree.api import *
import time
import pagetime

doc = """
Consent and Welcome pages with treatment assignment (BB, BI, BT).
"""
def creating_session(subsession):
    import itertools
    print("CREATING_SESSION IS RUNNING")  # 🔥 Add this
    treatments = itertools.cycle(subsession.session.config['treatments'])
    for player in subsession.get_players():
        player.participant.treatment = next(treatments)

class C(BaseConstants):
    NAME_IN_URL = 'instruction'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Shared for all treatments
    q1 = models.IntegerField(
        choices=[[1, 'True'], [2, 'False']],
        widget=widgets.RadioSelect
    )
    q2 = models.IntegerField(
        choices=[
            [1, 'A random draw'],
            [2, 'The number of people who choose Box B'],
            [3, 'The color of the ball in Box A'],
            [4, 'The number of people who choose Box A']
        ],
        widget=widgets.RadioSelect
    )
    q3 = models.IntegerField(
        choices=[
            [1, '3.0 ECU'],
            [2, '2.5 ECU'],
            [3, '2 ECU'],
            [4, '1.5 ECU'],
            [5, '1 ECU']
        ],
        widget=widgets.RadioSelect
    )
    q4 = models.IntegerField(
        choices=[
            [1, 'Box A with BLUE'],
            [2, 'Box A with YELLOW'],
            [3, 'Box B with only me choosing'],
            [4, 'Box B with everyone choosing']
        ],
        widget=widgets.RadioSelect
    )

    # Only for BI treatment
    q5_bi = models.IntegerField(
        choices=[
            [1, 'The ball in Box A is BLUE'],
            [2, 'The ball in Box A is YELLOW'],
            [3, 'The Clue Ball was chosen randomly'],
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

    # Only for BT treatment
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


# PAGES
@pagetime.track
class Consent(Page):
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_consent = pagetime.last(player.participant)


@pagetime.track
class Welcome(Page):

    @staticmethod
    def vars_for_template(player: Player):
        treatment = player.participant.treatment
        exchange_rate = player.subsession.session.config['exchange_rate']
        inverse_exchange_rate = round(1/exchange_rate)
        return dict(treatment=treatment, exchange_rate=exchange_rate, inverse_exchange_rate=inverse_exchange_rate)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_welcome = pagetime.last(player.participant)

@pagetime.track
class Decisions(Page):

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
    def vars_for_template(player: Player):
        treatment = player.participant.treatment
        exchange_rate = player.subsession.session.config['exchange_rate']
        return dict(treatment=treatment, exchange_rate=exchange_rate)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_examples = pagetime.last(player.participant)


class ComprehensionCheck(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        treatment = player.participant.treatment
        form_fields = ['q1', 'q2', 'q3', 'q4']
        treatment = getattr(player.participant, 'treatment', 'BB')  # ← Default fallback
        if treatment == 'BI':
            form_fields += ['q5_bi', 'q6_bi', 'q7_bi']
        elif treatment == 'BT':
            form_fields += ['q5_bt', 'q6_bt']
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        treatment = player.participant.treatment
        exchange_rate = player.subsession.session.config['exchange_rate']
        return dict(treatment=treatment, exchange_rate=exchange_rate)

    @staticmethod
    def error_message(player: Player, values):
        solutions = dict(
            q1=1,  # True
            q2=2,  # The number of people who choose Box B
            q3=4,  # 1.5 ECU (in Part 1)
            q4=2,  # Box A with YELLOW
        )

        error_messages = {}

        for field_name in solutions:
            if field_name in values and values[field_name] != solutions[field_name]:
                error_messages[field_name] = 'The above answer is incorrect - please try again.'

        return error_messages

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_comprehension = pagetime.last(player.participant)


@pagetime.track
class ExamplesWaitPage(Page):

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_examples_wait = pagetime.last(player.participant)


@pagetime.track
class Results(Page):

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.time_results = int(time.time())
page_sequence = [Consent, Welcome, Decisions, Examples, ExamplesWaitPage, ComprehensionCheck]
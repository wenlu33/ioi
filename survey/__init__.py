from otree.api import *
import time
import pagetime

doc = """
Post-task survey and end screen.
"""


class C(BaseConstants):
    NAME_IN_URL = 'survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Demographics
    age = models.IntegerField(label='1. How old are you?', min=13, max=125)

    gender = models.StringField(
        choices=[
            ['Male', 'Male'],
            ['Female', 'Female'],
            ['Other', 'Other'],
            ['I prefer not to say.', 'I prefer not to say.'],
        ],
        label='2. What is your gender?',
        widget=widgets.RadioSelect,
    )

    race = models.IntegerField(
        label="3. Which race or ethnicity best describes you?",
        choices=[
            [1, 'White or Caucasian'],
            [2, 'Black or African-American'],
            [3, 'Hispanic or Latino'],
            [4, 'Asian'],
            [5, 'Native American'],
            [6, 'Mixed Race or Multi-Racial'],
            [7, 'Other'],
        ],
        widget=widgets.RadioSelect,
    )

    study_year = models.IntegerField(
        label="4. What year are you?",
        choices=[
            [1, '1st-year undergraduate'],
            [2, '2nd-year undergraduate'],
            [3, '3rd-year undergraduate'],
            [4, '4th-year undergraduate'],
            [5, 'Graduate'],
            [0, 'Other'],
        ],
        widget=widgets.RadioSelect,
    )

    study_field = models.StringField(
        choices=[
            ['Arts and Humanities', 'Arts and Humanities'],
            ['Business', 'Business'],
            ['Economics', 'Economics'],
            ['Engineering', 'Engineering'],
            ['Finance', 'Finance'],
            ['Mathematics', 'Mathematics'],
            ['Medicine', 'Medicine'],
            ['Natural Science', 'Natural Science'],
            ['Psychology', 'Psychology'],
            ['Social Studies', 'Social Studies'],
            ['Other', 'Other'],
        ],
        label='5. What is your field of study?',
        widget=widgets.RadioSelect,
    )

    gpa_avg = models.FloatField(
        label="6. What is your average GPA?",
        choices=[
            [0.5, 'Less than 1'],
            [1.5, 'Between 1 and 2'],
            [2.25, 'Between 2 and 2.5'],
            [2.75, 'Between 2.5 and 3'],
            [3.25, 'Between 3 and 3.5'],
            [3.75, 'More than 3.5'],
        ],
        widget=widgets.RadioSelect,
    )

    experience = models.IntegerField(
        label="7. Please indicate how many decision-making experiments you have participated in (including this experiment).",
        choices=[
            [1, 'This is the first time.'],
            [2, '2 - 4'],
            [3, '5 - 7'],
            [4, '8 or more'],
            [0, 'I prefer not to say.']
        ],
        widget=widgets.RadioSelect,
    )

    time_survey = models.IntegerField()
    time_survey_instructions = models.IntegerField()


# PAGES
@pagetime.track
class SurveyInstructions(Page):

    @staticmethod
    def vars_for_template(player):
        participation_fee = player.session.config.get('participation_fee', 3)
        return dict(participation_fee=format(participation_fee, '.2f'))

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_instructions = pagetime.last(player.participant)


@pagetime.track
class Survey(Page):
    form_model = 'player'
    form_fields = [
        'age',
        'gender',
        'race',
        'study_year',
        'study_field',
        'gpa_avg',
        'experience',
    ]

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey = pagetime.last(player.participant)


# class EndScreen(Page):
#
#     @staticmethod
#     def vars_for_template(player):
#         # Game earnings (already stored in participant.payoff from FinalPayment)
#         game_earnings = player.participant.payoff
#
#         # Participation fee for completing survey
#         participation_fee = player.session.config.get('participation_fee', 3)
#
#         # Total earnings
#         total_earnings = game_earnings + participation_fee
#
#         return dict(
#             payoff=format(game_earnings, '.2f'),
#             participation_fee=format(participation_fee, '.2f'),
#             total_earnings=format(total_earnings, '.2f'),
#         )
class EndScreen(Page):
    @staticmethod
    def vars_for_template(player):
        # Game earnings from FinalPayment
        game_earnings = player.participant.payoff

        # Participation fee from settings
        participation_fee = float(player.session.config.get('participation_fee', 3))

        # Total
        total_earnings = game_earnings + participation_fee

        # ✅ Debug print to see actual values
        print(f"DEBUG EndScreen: game={game_earnings}, fee={participation_fee}, total={total_earnings}")

        return dict(
            payoff=format(float(game_earnings), '.2f'),
            participation_fee=format(float(participation_fee), '.2f'),
            total_earnings=format(float(total_earnings), '.2f'),
        )
page_sequence = [SurveyInstructions, Survey, EndScreen]
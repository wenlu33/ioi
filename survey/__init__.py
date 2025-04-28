from otree.api import *
import time
import pagetime
import math

doc = """
This app shows the post-task survey and end screen.

Page sequence:

<ul>
    <li>Survey Instructions</li>
    <li>Survey Page</li>
    <li>End Screen</li>
</ul>

"""


class C(BaseConstants):
    NAME_IN_URL = 'survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    StandardChoices = [
        [1, 'Disagree strongly'],
        [2, 'Disagree moderately'],
        [3, 'Disagree a little'],
        [4, 'Neither agree nor disagree'],
        [5, 'Agree a little'],
        [6, 'Agree moderately'],
        [7, 'Agree strongly'],
    ]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass

class Player(BasePlayer):
    start_time = models.FloatField()
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
        label="3. Which race or ethnicity best describes you? ",
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

    # academics
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
        label='5) What is your field of study',
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
        participation_fee= format(player.session.config['participation_fee'], '.2f')
        return dict(participation_fee=participation_fee)

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
        player.participant.finished = True
        player.participant.end_time = time.time()
        player.participant.total_time = int(player.participant.end_time - player.participant.start_time)


class EndScreen(Page):

    @staticmethod
    def vars_for_template(player):
        payoff = player.participant.payoff

        participation_fee = player.session.config['participation_fee']
        total_earnings = participation_fee + payoff

        return dict(
            payoff=format(payoff, '.2f'),
            participation_fee=format(participation_fee, '.2f'),
            total_earnings=format(total_earnings, '.2f'),
        )


page_sequence = [SurveyInstructions, Survey, EndScreen]

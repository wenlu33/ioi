from os import environ
import os

# Define BASE_DIR (root directory of your project)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the _static directory to STATICFILES_DIRS
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "_static"),  # This tells Django where to look for static files in your project
]

# Other settings...

SESSION_CONFIGS = [
    # dict(
    #     name='IOI_BB',
    #     display_name='IOI - Treatment BB',
    #     app_sequence=['instruction', 'congestion_game_with_uncertainty', 'instruction2', 'congestion_game_with_uncertainty2', 'survey'],
    #     treatment='BB',
    # ),
    dict(
        name='IOI_BI',
        display_name='IOI - Treatment BI',
        app_sequence=['instruction', 'congestion_game_with_uncertainty', 'instruction2', 'congestion_game_with_uncertainty2', 'survey'],
        treatment='BI',
        use_browser_bots=False,
    ),
    dict(
        name='IOI_BT',
        display_name='IOI - Treatment BT',
        app_sequence=['instruction', 'congestion_game_with_uncertainty', 'instruction2', 'congestion_game_with_uncertainty2', 'survey'],
        treatment='BT',
        use_browser_bots=False,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    num_demo_participants=5,
    exchange_rate=0.5,  # ← Changed to 0.5 (1 ECU = $0.50)
    real_world_currency_per_point=1,
    participation_fee=3.00,
    doc=""
)

PARTICIPANT_FIELDS = [

    'treatment',  # Stores the treatment assigned to the participant (BB, BI, BT).
    'random_number',  # This could represent the random number drawn for decision-making or exogenous variables.
    'clue_box_used',  # If you're assigning a clue box based on Box A's color and storing that info.
    'start_time',  # The time the participant starts the experiment.
    'end_time',  # The time the participant finishes the experiment.
    'total_time',  # The total time the participant took to complete the experiment.
    'finished',  # Boolean value (True/False) to track if the participant has finished.
    'round_number',  # To track the round number the participant is in.
    'guess',  # The guess made by the participant about the ball color.
    'choice',  # The choice the participant made (Box A or Box B).
    'second_guess',  # The second guess, if applicable (used for BI treatment).
    'box_a_color',  # The color of Box A, determined during the experiment.
    'box_b_size',  # Size of Box B, based on the choices made.
    'box_b_earnings',  # Earnings from Box B, based on the number of people choosing it.
    'clue_ball_color',  # The color of the clue ball, which could be used in the logic.
]
SESSION_FIELDS = []


ROOMS = [
    dict(
        name='SDER',
        display_name='SDER',
        participant_label_file='_rooms/SDER.txt',
    ),
]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False  # ✅ Change to False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '8365198495083'

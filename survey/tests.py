from otree.api import Bot, Submission
import random

# Import pages from __init__.py
from . import (
    SurveyInstructions,
    Survey,
    EndScreen
)


class PlayerBot(Bot):
    """
    Bot for survey - fills out all required demographic fields
    """

    def play_round(self):
        # Yield SurveyInstructions page (display page)
        yield SurveyInstructions

        # Fill out survey with random demographic data
        survey_data = {
            'age': random.randint(18, 30),
            'gender': random.choice(['Male', 'Female', 'Other', 'I prefer not to say.']),
            'race': random.randint(1, 7),
            'study_year': random.randint(0, 5),
            'study_field': random.choice([
                'Arts and Humanities',
                'Business',
                'Economics',
                'Engineering',
                'Finance',
                'Mathematics',
                'Medicine',
                'Natural Science',
                'Psychology',
                'Social Studies',
                'Other'
            ]),
            'gpa_avg': random.choice([0.5, 1.5, 2.25, 2.75, 3.25, 3.75]),
            'experience': random.randint(0, 4),
        }

        # Yield Survey page with form data
        yield Survey, survey_data

        # Yield EndScreen (final page - no submit button, just displays payment)
        yield Submission(EndScreen, {}, check_html=False)

        print(f"Bot {self.participant.code} completed survey and finished experiment!")
        print(f"Final total payment: ${self.participant.payoff:.2f}")
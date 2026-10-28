"""Exercise the repository's real logic without importing the oTree server.

Functions are extracted from the source AST so the checks use the implementation
in the application, with small stand-ins for oTree player and group records.
These checks do not replace full oTree bot sessions.
"""
from __future__ import annotations

import ast
import contextlib
import io
import itertools
from pathlib import Path
import random
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load_logic(relative_path, *names):
    parsed = ast.parse((ROOT / relative_path).read_text())
    nodes = []
    for node in parsed.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
            if isinstance(node, ast.ClassDef):
                node.bases = []
                node.keywords = []
            nodes.append(node)
    future = ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0)
    module = ast.fix_missing_locations(ast.Module(body=[future, *nodes], type_ignores=[]))
    namespace = {'random': random, 'C': SimpleNamespace(NUM_ROUNDS=10)}
    exec(compile(module, str(ROOT / relative_path), 'exec'), namespace)
    return namespace


BASE = load_logic('congestion_game_with_uncertainty/__init__.py', 'set_group_results')
TREATMENT = load_logic(
    'congestion_game_with_uncertainty2/__init__.py',
    'set_group_results', 'RecommendationWaitPage', 'FinalPayment',
)


def group_for(choices, treatment='BI', color='BLUE'):
    players = [SimpleNamespace(choice=c, recommendation='',
               participant=SimpleNamespace(treatment=treatment)) for c in choices]
    return SimpleNamespace(box_a_color=color, get_players=lambda: players)


def payment_player(saved_round=None, baseline_choice='A', color='YELLOW',
                   treatment_choice='B', treatment_payoff=15):
    records = {}
    if saved_round is not None:
        records['random_number'] = saved_round
    for n in range(1, 11):
        records[f'part1_round_{n}'] = dict(
            choice=baseline_choice, box_a_color=color,
            num_chose_b=3, box_b_earnings=15,
        )
    treatment_round = SimpleNamespace(
        choice=treatment_choice, recommendation='B',
        group=SimpleNamespace(box_a_color=color, num_chose_box_b=3,
                              box_b_earnings=treatment_payoff),
    )
    return SimpleNamespace(
        participant=SimpleNamespace(vars=records, payoff=None),
        session=SimpleNamespace(config={'exchange_rate': .5}),
        in_round=lambda n: treatment_round,
    )


class PayoffChecks(unittest.TestCase):
    def test_all_binary_choice_profiles_baseline(self):
        for choices in itertools.product('AB', repeat=5):
            group = group_for(choices)
            with contextlib.redirect_stdout(io.StringIO()):
                BASE['set_group_results'](group)
            n = choices.count('B')
            self.assertEqual(group.num_chose_box_b, n)
            self.assertEqual(group.box_b_earnings, 30-5*n if n else 0)

    def test_all_binary_choice_profiles_both_treatments(self):
        for treatment, choices in itertools.product(['BI','BT'], itertools.product('AB', repeat=5)):
            group = group_for(choices, treatment)
            with contextlib.redirect_stdout(io.StringIO()):
                TREATMENT['set_group_results'](group)
            n = choices.count('B')
            deduction = 5 if treatment == 'BT' else 0
            self.assertEqual(group.num_chose_box_b, n)
            self.assertEqual(group.box_b_earnings, 30-5*n-deduction if n else 0)

    def test_blue_recommendations_have_two_entries(self):
        for _ in range(30):
            group = group_for('AAAAA')
            TREATMENT['RecommendationWaitPage'].after_all_players_arrive(group)
            self.assertEqual(sorted(p.recommendation for p in group.get_players()), ['A','A','A','B','B'])

    def test_yellow_recommendations_all_alternative(self):
        group = group_for('AAAAA', color='YELLOW')
        TREATMENT['RecommendationWaitPage'].after_all_players_arrive(group)
        self.assertEqual([p.recommendation for p in group.get_players()], ['A']*5)

    def test_refresh_preserves_first_payment_draw(self):
        player = payment_player()
        with patch.object(random, 'randint', return_value=7) as draw:
            first = TREATMENT['FinalPayment'].vars_for_template(player)
            second = TREATMENT['FinalPayment'].vars_for_template(player)
        self.assertEqual(draw.call_count, 1)
        self.assertEqual(first, second)
        self.assertEqual(player.participant.vars['random_number'], 7)

    def test_saved_round_does_not_draw_again(self):
        player = payment_player(saved_round=11)
        with patch.object(random, 'randint', side_effect=AssertionError('Must not redraw')):
            result = TREATMENT['FinalPayment'].vars_for_template(player)
        self.assertEqual(result['part'], 2)
        self.assertEqual(result['round_in_part'], 1)

    def test_baseline_alternative_earnings(self):
        for color, expected in [('YELLOW',15),('BLUE',5)]:
            player = payment_player(saved_round=10, color=color)
            result = TREATMENT['FinalPayment'].vars_for_template(player)
            self.assertEqual(result['round_earnings_dollars'], expected)
            self.assertEqual(player.participant.payoff, expected)

    def test_baseline_shared_option_earnings(self):
        player = payment_player(saved_round=2, baseline_choice='B')
        result = TREATMENT['FinalPayment'].vars_for_template(player)
        self.assertEqual(result['round_earnings_dollars'], 7.5)

    def test_treatment_shared_option_uses_charged_payoff(self):
        player = payment_player(saved_round=20, treatment_payoff=10)
        result = TREATMENT['FinalPayment'].vars_for_template(player)
        self.assertEqual(result['round_in_part'], 10)
        self.assertEqual(result['round_earnings_dollars'], 5)

    def test_treatment_alternative_uses_state_payoff(self):
        player = payment_player(saved_round=12, treatment_choice='A', color='BLUE')
        result = TREATMENT['FinalPayment'].vars_for_template(player)
        self.assertEqual(result['round_earnings_dollars'], 5)

    def test_missing_baseline_record_is_not_silently_substituted(self):
        player = payment_player(saved_round=3)
        del player.participant.vars['part1_round_3']
        with self.assertRaisesRegex(RuntimeError, 'Missing baseline record'):
            TREATMENT['FinalPayment'].vars_for_template(player)

    def test_invalid_saved_payment_round(self):
        for value in [0,21,'7',7.5,True]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                TREATMENT['FinalPayment'].vars_for_template(payment_player(saved_round=value))


if __name__ == '__main__':
    unittest.main()

# Pricing and recommendations in a congestion experiment

Python and oTree software for Wen Lu's research on how financial incentives and private recommendations affect decisions about a shared resource.

**Research question:** Can recommendations improve coordination, and how do their effects compare with a fixed charge?

In the experiment, five participants choose between an alternative with an uncertain payoff and a shared option whose payoff decreases as more people choose it. Participants complete ten baseline rounds, followed by ten rounds with either a charge or private recommendations. The associated study involved 170 participants across six sessions and produced 3,400 repeated decisions.

[Research and contact](https://www.wenlu.site) · [Wen Lu on GitHub](https://github.com/wenlu33)

## What to look at first

| Component | What it does |
| --- | --- |
| [`congestion_game_with_uncertainty/`](congestion_game_with_uncertainty/) | Baseline choices, group formation, feedback, and payoff calculations |
| [`congestion_game_with_uncertainty2/`](congestion_game_with_uncertainty2/) | Treatment-specific charges and recommendations, decisions, feedback, and payment display |
| [`instruction/`](instruction/) and [`instruction2/`](instruction2/) | Participant instructions, examples, and comprehension checks |
| [`survey/`](survey/) | Post-task survey and final earnings display |
| [`settings.py`](settings.py) | The `IOI_BI` information session and `IOI_BT` charge session |

The `BI` condition sends recommendations that depend on the alternative option's hidden state. In the low-payoff state, two randomly chosen participants receive a recommendation to use the shared option and three receive the alternative recommendation. In the high-payoff state, everyone receives the alternative recommendation. The `BT` condition instead deducts five experimental points from each shared-option choice.

## Run a local demonstration

The project specifies Python 3.11 and oTree 5.11.4. For a local SQLite demonstration:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install otree==5.11.4
otree devserver
```

Open the local address shown by oTree and create an `IOI_BI` or `IOI_BT` session with five participants. Each participant needs a separate participant URL. Groups are reshuffled after the first round within each ten-round stage.

The existing `requirements.txt` also includes the PostgreSQL driver used for deployment. It is not required for the local SQLite demonstration above. Deployment settings and live recruitment should be managed separately from a local demonstration.

## Research and interpretation

This repository contains the experiment implementation. The manuscript's empirical analysis and participant-level research data are maintained separately.

The study compares how choices and total surplus change under the two policies. Information makes choices more responsive to the hidden state; the fixed charge reduces shared-option use in both states. Both generate positive estimated changes in allocative surplus when charge revenue is included. Participant earnings are a separate outcome because the collected charges were not rebated in the experiment.

The within-information recommendation assignment identifies the effect of recommendation content in the low-payoff state. The between-policy comparison uses six sessions, three per policy. These are distinct comparisons.

## Software checks

The original oTree bots are in each application's `tests.py`. The additional checks in `tests/test_game_logic.py` exercise the payoff tables, recommendation allocation, and payment-round stability without starting oTree:

```bash
python -m unittest discover -s tests -v
```

Those checks cover isolated logic. A full oTree session remains the appropriate check for page flow, forms, and group synchronization.

## Author

Wen Lu, Economics PhD candidate, Georgia State University. For the paper, related research, and contact information, see [wenlu.site](https://www.wenlu.site).

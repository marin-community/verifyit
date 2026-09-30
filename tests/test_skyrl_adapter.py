# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

import pytest

from verifyit.adapters.skyrl import grade_aime_candidate, grade_gsm8k_final_line
from verifyit.grade import Status


@pytest.mark.parametrize(
    ("expected", "candidate", "reward"),
    [
        ("20:7", "40:14", 1.0),
        ("20:7", "7:20", 0.0),
        ("0.5", r"\frac{1}{2}", 1.0),
        ("9007199254740992", "9007199254740993", 0.0),
        ("9007199254740992.5", "18014398509481985/2", 1.0),
        ("20:7", "20:0", 0.0),
        ("1000", "1e3", 0.0),
        ("1000", "1_000", 0.0),
        ("0.5", "1.0:2.0", 0.0),
    ],
)
def test_aime_normalized_answer_exact_rational_equivalence(expected, candidate, reward):
    verdict = grade_aime_candidate(expected, candidate)
    assert (verdict.reward, verdict.status) == (reward, Status.SCORED)


@pytest.mark.parametrize(
    ("expected", "response", "reward"),
    [
        ("1234.0", "Reasoning\n#### 1,234", 1.0),
        ("1234", "#### 12,34", 0.0),
        ("42", "#### 42\nMore prose", 0.0),
        ("42", "#### 42\n#### 41", 0.0),
        ("42", "#### 41\n#### 42", 1.0),
        ("9007199254740992", "#### 9007199254740993", 0.0),
        ("0.5", "#### 0.50", 1.0),
        ("42", "The answer is #### 42", 0.0),
    ],
)
def test_gsm8k_requires_exact_value_on_standalone_final_line(expected, response, reward):
    verdict = grade_gsm8k_final_line(expected, response)
    assert (verdict.reward, verdict.status) == (reward, Status.SCORED)

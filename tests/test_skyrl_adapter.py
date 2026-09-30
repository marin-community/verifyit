# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

import pytest

from verifyit.adapters.skyrl import (
    grade_aime_candidate,
    grade_grid_candidate,
    grade_gsm8k_final_line,
    grade_gsm8k_strict,
    grade_literal_candidate,
    grade_rounded_candidate,
    grade_search_em,
)
from verifyit.grade import InvalidTask, Status


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


@pytest.mark.parametrize(
    ("expected", "response", "reward"),
    [
        ("42", "#### 42\n#### 41", 1.0),
        ("42", "#### 41\n#### 42", 0.04),
        ("42", "no marker 42", 0.0),
        ("1234", "#### 12,34", 1.0),
        ("42", "#### 42.0", 0.04),
        ("42", "#### .", 0.04),
    ],
)
def test_gsm8k_strict_retains_first_marker_literal_equality_and_turn_shaping(expected, response, reward):
    verdict = grade_gsm8k_strict(expected, response, format_score=0.2 / 5)
    assert (verdict.reward, verdict.status) == (reward, Status.SCORED)


@pytest.mark.parametrize(
    ("targets", "response", "reward"),
    [
        (["New York", "NYC"], "<answer>The NYC!</answer>", 1.0),
        ("cat", "<answer>cat</answer><answer>dog</answer>", 0.0),
        ("cat", "<answer>dog</answer><answer>A cat.</answer>", 1.0),
        ("cat", "cat", 0.0),
        ("cat", "<answer>the catfish</answer>", 0.0),
        ("", "<answer>The!!!</answer>", 1.0),
        ("é", "<answer>É</answer>", 1.0),
        ("ss", "<answer>ß</answer>", 0.0),
        ([], "<answer>cat</answer>", 0.0),
    ],
)
def test_search_qa_normalization_alternatives_and_last_tag(targets, response, reward):
    verdict = grade_search_em(targets, response)
    assert (verdict.reward, verdict.status) == (reward, Status.SCORED)


@pytest.mark.parametrize(("candidate", "reward"), [(" 42", 0.0), ("42 ", 0.0), ("42\n", 0.0), ("42", 1.0)])
def test_literal_encoding_keeps_outer_whitespace_significant(candidate, reward):
    assert grade_literal_candidate("42", candidate).reward == reward


@pytest.mark.parametrize(
    ("expected", "candidate", "reward"),
    [(2.5, 1.5, 1.0), (3.5, 2.5, 0.0), (3.5, 4.0, 1.0), (2.0, None, 0.0), (2.0, float("inf"), 0.0)],
)
def test_rounded_answers_use_bankers_rounding_and_reject_nonfinite_candidates(expected, candidate, reward):
    assert grade_rounded_candidate(expected, candidate).reward == reward


@pytest.mark.parametrize(
    ("candidate", "reward"),
    [
        ([[1, 2], [3, 4]], 1.0),
        ([[1, 2, 3, 4]], 0.0),
        ([[True, 2], [3, 4]], 0.0),
        ([[1.0, 2], [3, 4]], 0.0),
        ([[3, 4], [1, 2]], 0.0),
    ],
)
def test_grid_comparison_preserves_rows_and_rejects_boolean_and_float_cells(candidate, reward):
    verdict = grade_grid_candidate([[1, 2], [3, 4]], candidate)
    assert verdict.reward == reward


def test_invalid_grid_reference_is_not_candidate_zero():
    with pytest.raises(InvalidTask, match="expected grid"):
        grade_grid_candidate([[True]], [[1]])


@pytest.mark.parametrize("expected", [".", "nan", "inf"])
def test_gsm8k_malformed_reference_cannot_award_literal_or_format_credit(expected):
    with pytest.raises(InvalidTask, match="finite decimal"):
        grade_gsm8k_strict(expected, f"#### {expected}", format_score=0.04)

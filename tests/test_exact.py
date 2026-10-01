# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import pytest

from verifyit.grade import InvalidTask, Status
from verifyit.grade import grade as dispatch
from verifyit.modes import grade_exact
from verifyit.spec import ExactSpec


def _answer(workspace: Path, text: str) -> None:
    (workspace / "answer.txt").write_text(text)


@pytest.mark.parametrize(
    "spec, text, reward",
    [
        (ExactSpec(expected=("Paris",)), "  Paris \n", 1.0),
        (ExactSpec(expected=("Paris",)), "paris\n", 1.0),
        (ExactSpec(expected=("Paris",), ignore_case=False), "paris\n", 0.0),
        (ExactSpec(expected=("Paris",)), "Lyon\n", 0.0),
        (ExactSpec(expected=("hello world",)), "hello    world\n", 1.0),
        (ExactSpec(expected=("hello world",), ignore_whitespace=False), "hello    world\n", 0.0),
        # A trailing newline never decides the reward, even with whitespace significant.
        (ExactSpec(expected=("hello world",), ignore_whitespace=False), "hello world\n", 1.0),
        # A boxed answer is compared on its own, so surrounding prose does not spoil it.
        (ExactSpec(expected=("Paris",)), "The capital is \\boxed{Paris} of course.\n", 1.0),
        (ExactSpec(expected=("Paris",)), "The capital is \\boxed{Lyon} of course.\n", 0.0),
        (ExactSpec(expected=("Paris",)), "The capital is Paris of course.\n", 0.0),
    ],
)
def test_exact_single_expected_compares_the_whole_candidate(tmp_path, spec, text, reward):
    _answer(tmp_path, text)
    assert grade_exact.grade(spec, tmp_path, tmp_path).reward == reward


@pytest.mark.parametrize(
    "spec, text, reward",
    [
        (ExactSpec(expected=("red", "green", "blue")), "red, green, blue\n", 1.0),
        (ExactSpec(expected=("red", "green", "blue")), "red\ngreen\nblue\n", 1.0),
        (ExactSpec(expected=("red", "green", "blue")), "blue, green, red\n", 0.0),
        (ExactSpec(expected=("red", "green", "blue"), ordered=False), "blue, green, red\n", 1.0),
        (ExactSpec(expected=("red", "green", "blue")), "red, green\n", 0.0),
        (ExactSpec(expected=("red", "green", "blue")), "red, green, blue, yellow\n", 0.0),
        # A multiset counts repeats: two "a" are not the same answer as one.
        (ExactSpec(expected=("a", "a", "b"), ordered=False), "a, b, a\n", 1.0),
        (ExactSpec(expected=("a", "a", "b"), ordered=False), "a, b, b\n", 0.0),
        (ExactSpec(expected=("red", "green")), "\\boxed{red, green}\n", 1.0),
    ],
)
def test_exact_several_expected_compares_the_candidate_as_a_list(tmp_path, spec, text, reward):
    _answer(tmp_path, text)
    assert grade_exact.grade(spec, tmp_path, tmp_path).reward == reward


def test_exact_empty_output_scores_zero_with_no_output(tmp_path):
    _answer(tmp_path, "\n \n")
    result = grade_exact.grade(ExactSpec(expected=("Paris",)), tmp_path, tmp_path)
    assert (result.status, result.reward, result.detail["reason"]) == (Status.SCORED, 0.0, "no_output")


def test_exact_reward_detail_carries_the_extracted_candidate(tmp_path):
    _answer(tmp_path, "The capital is \\boxed{Lyon}.\n")
    detail = grade_exact.grade(ExactSpec(expected=("Paris",)), tmp_path, tmp_path).detail
    assert detail == {"extracted": "Lyon", "expected": ["Paris"]}


def test_exact_without_an_expected_string_is_an_invalid_task(tmp_path):
    _answer(tmp_path, "Paris\n")
    assert dispatch(ExactSpec(expected=()), tmp_path, tmp_path).status == Status.INVALID_TASK


@pytest.mark.parametrize(
    "candidate, expected, reward", [("42 ", "42", 0), (" 42", "42", 0), ("42\n", "42", 0), (" 42", " 42", 1)]
)
def test_exact_literal_boundary_preserves_whitespace(candidate, expected, reward):
    spec = ExactSpec((expected,), ignore_case=False, ignore_whitespace=False, strip_outer_whitespace=False)
    assert grade_exact.grade_exact_candidate(spec, candidate).reward == reward


def test_invalid_direct_normalization_flag_cannot_award_correct_answer():
    with pytest.raises(InvalidTask, match="booleans"):
        grade_exact.grade_exact_candidate(ExactSpec(("2",), ignore_case="false"), "2")


@pytest.mark.parametrize(
    "candidate,score",
    [("The capital is Paris.", 1.0), ("Parisian", 1.0), ("Lyon", 0.0), ("", 0.0)],
)
def test_explicit_substring_contract_grades_containment(candidate, score):
    spec = ExactSpec(("Paris",), substring=True)
    assert grade_exact.grade_exact_candidate(spec, candidate).reward == score


@pytest.mark.parametrize("expected", [("",), ("  \n",), ("Paris", "Lyon")])
def test_substring_vacuous_or_multi_reference_task_invalid_before_missing_output(tmp_path, expected):
    spec = ExactSpec(expected, substring=True)
    with pytest.raises(InvalidTask, match="one nonempty"):
        grade_exact.grade(spec, tmp_path, tmp_path)
    result = dispatch(spec, tmp_path, tmp_path)
    assert result.status == Status.INVALID_TASK
    assert result.reward == 0.0


def test_substring_boolean_flag_is_strict():
    with pytest.raises(InvalidTask, match="booleans"):
        grade_exact.grade_exact_candidate(ExactSpec(("Paris",), substring=1), "Paris")


def test_source_lower_semantics_are_separate_from_casefold():
    spec = ExactSpec(("ß".lower(),), ignore_case=False, ignore_whitespace=False, substring=True)
    assert grade_exact.grade_exact_candidate(spec, "SS".lower()).reward == 0.0
    assert grade_exact.grade_exact_candidate(spec, "Straße".lower()).reward == 1.0


@pytest.mark.parametrize("expected", ["idk", b"idk", {"i": 1, "d": 1, "k": 1}])
def test_direct_reference_container_cannot_award_character_list_credit(tmp_path, expected):
    spec = ExactSpec(expected=expected)
    with pytest.raises(InvalidTask, match="expected string"):
        grade_exact.grade_exact_candidate(spec, "i,d,k")
    _answer(tmp_path, "i,d,k")
    result = dispatch(spec, tmp_path, tmp_path)
    assert result.status == Status.INVALID_TASK
    assert result.reward == 0.0

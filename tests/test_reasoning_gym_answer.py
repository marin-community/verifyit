# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

import json

import pytest

from verifyit.grade import InvalidTask, Status, main
from verifyit.modes import grade_reasoning_gym
from verifyit.spec import ReasoningGymSpec

NEEDLE_ENTRY = {
    "question": "Who savors playing the accordion? Reply only with a name.",
    "answer": "Richard",
    "metadata": {"source_dataset": "needle_haystack", "source_index": 0, "num_statements": 45},
}


@pytest.fixture
def workspace(tmp_path):
    directory = tmp_path / "app"
    directory.mkdir()
    return directory


@pytest.fixture
def tests_dir(tmp_path):
    directory = tmp_path / "tests"
    directory.mkdir()
    (directory / "entry.json").write_text(json.dumps(NEEDLE_ENTRY))
    return directory


def answer(workspace, text):
    (workspace / "answer.txt").write_text(text)


def grade(tests_dir, workspace, dataset="needle_haystack"):
    return grade_reasoning_gym.grade(ReasoningGymSpec(dataset=dataset), tests_dir, workspace)


def test_correct_answer_scores_one(tests_dir, workspace):
    answer(workspace, "Richard\n")
    reward = grade(tests_dir, workspace)
    assert (reward.reward, reward.status) == (1.0, Status.SCORED)


def test_dataset_scorer_decides_equivalence_rather_than_string_equality(tests_dir, workspace):
    # needle_haystack lowercases before comparing, so a differently cased name is still correct.
    answer(workspace, "richard")
    assert grade(tests_dir, workspace).reward == 1.0


def test_wrong_answer_scores_zero(tests_dir, workspace):
    answer(workspace, "Oluwadamiloju")
    reward = grade(tests_dir, workspace)
    assert (reward.reward, reward.status) == (0.0, Status.SCORED)


def test_prose_around_the_answer_is_not_accepted_by_this_dataset(tests_dir, workspace):
    answer(workspace, "The person who savors playing the accordion is Richard.")
    assert grade(tests_dir, workspace).reward == 0.0


def test_partial_credit_from_the_scorer_is_passed_through(tmp_path, workspace):
    # simple_equations keeps reasoning-gym's default scorer, which awards a fraction when the gold
    # answer is buried in a longer response.
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    entry = {"answer": "42", "metadata": {"source_dataset": "simple_equations"}}
    (tests_dir / "entry.json").write_text(json.dumps(entry))
    answer(workspace, "x = 42")
    reward = grade(tests_dir, workspace, dataset="simple_equations")
    assert 0.0 < reward.reward < 1.0
    answer(workspace, "42")
    assert grade(tests_dir, workspace, dataset="simple_equations").reward == 1.0


@pytest.mark.parametrize(
    "dataset,entry,candidate,expected",
    [
        ("letter_jumble", {"answer": "alpha beta"}, "ALPHA BETA", 1.0),
        ("letter_jumble", {"answer": "alpha beta"}, "alpha wrong", 0.5),
        ("letter_jumble", {"answer": "alpha beta"}, "alpha beta extra", 1.0),
        ("letter_jumble", {"answer": "alpha beta"}, "wrong wrong", 0.0),
        (
            "word_sorting",
            {"answer": "alpha, beta", "metadata": {"sorted_words": ["alpha", "beta"]}},
            "alpha, wrong",
            0.5,
        ),
        (
            "word_sorting",
            {"answer": "alpha, beta", "metadata": {"sorted_words": ["alpha", "beta"]}},
            "beta, alpha",
            0.2,
        ),
        ("simple_equations", {"answer": "42"}, "x = 42", 1 / 3),
    ],
)
def test_extracted_candidate_preserves_dataset_partial_credit(dataset, entry, candidate, expected):
    entry.setdefault("metadata", {})["source_dataset"] = dataset
    result = grade_reasoning_gym.grade_reasoning_gym_candidate(ReasoningGymSpec(dataset=dataset), entry, candidate)
    assert (result.reward, result.status) == (expected, Status.SCORED)


def test_scorer_failure_clears_reward_files_and_records_infrastructure_error(tests_dir, workspace, tmp_path):
    spec_path = tests_dir / "verifier.toml"
    spec_path.write_text('mode = "reasoning-gym"\ndataset = "word_sorting"\n')
    entry = {
        "answer": "alpha, beta",
        "metadata": {"source_dataset": "word_sorting", "sorted_words": ["alpha", "beta"]},
    }
    (tests_dir / "entry.json").write_text(json.dumps(entry))
    answer(workspace, "alpha, beta")
    logs_dir = tmp_path / "logs"
    args = [str(spec_path), "--workspace", str(workspace), "--logs-dir", str(logs_dir)]
    assert main(args) == 0
    assert json.loads((logs_dir / "reward.json").read_text()) == {"reward": 1.0}
    assert (logs_dir / "reward.txt").read_text() == "1.0\n"

    # A missing evaluator field is a grader failure, not an incorrect candidate.
    del entry["metadata"]["sorted_words"]
    (tests_dir / "entry.json").write_text(json.dumps(entry))
    assert main(args) == 0
    verdict = json.loads((logs_dir / "verdict.json").read_text())
    assert verdict["status"] == Status.INFRA_ERROR
    assert "KeyError" in verdict["detail"]["error"]
    assert not (logs_dir / "reward.json").exists()
    assert not (logs_dir / "reward.txt").exists()


@pytest.mark.parametrize("text", [None, "", "   \n"])
def test_absent_or_blank_output_scores_zero_with_no_output(tests_dir, workspace, text):
    if text is not None:
        answer(workspace, text)
    reward = grade(tests_dir, workspace)
    candidate_reward = grade_reasoning_gym.grade_reasoning_gym_candidate(
        ReasoningGymSpec(dataset="needle_haystack"), NEEDLE_ENTRY, text
    )
    assert candidate_reward == reward
    assert reward.reward == 0.0
    assert reward.detail == {"reason": "no_output"}


def test_unknown_dataset_is_an_invalid_task(tests_dir, workspace):
    answer(workspace, "Richard")
    with pytest.raises(InvalidTask, match="unknown reasoning-gym dataset"):
        grade(tests_dir, workspace, dataset="not_a_reasoning_gym_dataset")


def test_missing_entry_file_is_an_invalid_task(tmp_path, workspace):
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    answer(workspace, "Richard")
    with pytest.raises(InvalidTask, match="entry not found"):
        grade(tests_dir, workspace)


@pytest.mark.parametrize(
    "entry_text, message",
    [
        ("{not json", "is not JSON"),
        ('{"answer": "Richard"}', "metadata field"),
        ("[1, 2, 3]", "metadata field"),
    ],
)
def test_unusable_entry_file_is_an_invalid_task(tmp_path, workspace, entry_text, message):
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "entry.json").write_text(entry_text)
    answer(workspace, "Richard")
    with pytest.raises(InvalidTask, match=message):
        grade(tests_dir, workspace)

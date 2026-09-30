# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

import json

import pytest

from verifyit.adapters.harbor_answers import grade_answer, main
from verifyit.grade import Status


@pytest.mark.parametrize(
    ("mode", "expected", "candidate", "score"),
    [
        ("aime", "42", " 42\n", 1.0),
        ("aime", "42", "\\boxed{42}", 0.0),
        ("gaia", "The\nAnswer", " theanSwer  ", 1.0),
        ("gaia", "A B", "AB", 0.0),
        ("satbench", "SAT", "[UNSAT] then [SAT]", 1.0),
        ("satbench", "SAT", "[SAT] then [UNSAT]", 0.0),
        ("gpqa-diamond", "B", " b \n", 1.0),
        ("gpqa-diamond", "B", "Answer: B", 0.0),
    ],
)
def test_harbor_answer_routes_preserve_source_extraction(mode, expected, candidate, score):
    reward = grade_answer(mode, expected, candidate)
    assert (reward.status, reward.reward) == (Status.SCORED, score)


def test_harbor_answer_cli_distinguishes_missing_candidate_from_invalid_reference(tmp_path):
    expected = tmp_path / "expected_answer.txt"
    candidate = tmp_path / "answer.txt"
    logs = tmp_path / "logs"
    expected.write_text("answer")
    assert main(["gaia", str(expected), str(candidate), "--logs-dir", str(logs)]) == 0
    assert json.loads((logs / "verdict.json").read_text())["status"] == "scored"
    assert (logs / "reward.txt").read_text().strip() == "0.0"
    expected.unlink()
    assert main(["gaia", str(expected), str(candidate), "--logs-dir", str(logs)]) == 0
    assert json.loads((logs / "verdict.json").read_text())["status"] == "invalid_task"
    assert not (logs / "reward.txt").exists()


def test_harbor_answer_cli_removes_prior_reward_after_candidate_read_failure(tmp_path):
    expected = tmp_path / "expected_answer.txt"
    candidate = tmp_path / "answer.txt"
    logs = tmp_path / "logs"
    expected.write_text("42")
    candidate.write_text("42")
    assert main(["aime", str(expected), str(candidate), "--logs-dir", str(logs)]) == 0
    assert (logs / "reward.txt").read_text().strip() == "1.0"
    candidate.write_bytes(b"\xff")
    assert main(["aime", str(expected), str(candidate), "--logs-dir", str(logs)]) == 0
    assert json.loads((logs / "verdict.json").read_text())["status"] == "infra_error"
    assert not (logs / "reward.txt").exists()

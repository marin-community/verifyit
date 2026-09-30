# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

"""Harbor answer-file clients for existing exact and MCQ primitives."""

import argparse
import json
import re
from pathlib import Path

from verifyit.adapters.skyrl import grade_literal_candidate
from verifyit.grade import InvalidTask, Reward, infra_error, invalid_task, scored, write_reward
from verifyit.modes.grade_mcq import grade_mcq_candidate
from verifyit.spec import McqSpec

SAT_MARKER = re.compile(r"\[(SAT|UNSAT)\]")
ASCII_LOWER = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")
ASCII_UPPER = str.maketrans("abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
ASCII_SPACE = " \t\r\n\v\f"


def grade_answer(mode: str, expected: str, candidate: str | None) -> Reward:
    """Apply the pinned source extractor, then call exact or MCQ candidate grading."""
    if mode == "aime":
        if not expected.isdecimal():
            raise InvalidTask("AIME expected answer must be a decimal integer")
        return grade_literal_candidate(expected, candidate.strip() if candidate is not None else "")
    if mode == "gaia":
        reference = expected.replace("\n", "").translate(ASCII_LOWER).strip(ASCII_SPACE)
        answer = (candidate or "").replace("\n", "").translate(ASCII_LOWER).strip(ASCII_SPACE)
        return grade_literal_candidate(reference, answer)
    if mode == "satbench":
        if not isinstance(expected, str) or expected not in {"SAT", "UNSAT"}:
            raise InvalidTask("SATBench expected answer must be SAT or UNSAT")
        markers = SAT_MARKER.findall(candidate or "")
        return grade_literal_candidate(expected, markers[-1] if markers else "")
    if mode == "gpqa-diamond":
        answer = (candidate or "").translate(ASCII_UPPER)
        answer = "".join(character for character in answer if character not in ASCII_SPACE)
        return grade_mcq_candidate(McqSpec(expected=expected, options=4), answer)
    raise InvalidTask(f"unknown Harbor answer route {mode!r}")


def grade_files(mode: str, expected_path: Path, candidate_path: Path) -> Reward:
    """Read protected task reference and candidate output with distinct failure statuses."""
    try:
        expected = expected_path.read_text()
    except FileNotFoundError as error:
        return invalid_task(f"missing expected answer: {error.filename}")
    except (OSError, UnicodeError) as error:
        return infra_error(f"cannot read expected answer: {error}")
    if mode == "satbench":
        try:
            data = json.loads(expected)
            label = data["expected_answer"]
        except (json.JSONDecodeError, TypeError, KeyError) as error:
            return invalid_task(f"invalid SATBench ground truth: {error}")
        if not isinstance(label, str):
            return invalid_task("SATBench expected answer must be a string")
        expected = label
    try:
        candidate = candidate_path.read_text()
    except FileNotFoundError:
        candidate = None
    except (OSError, UnicodeError) as error:
        return infra_error(f"cannot read candidate answer: {error}")
    try:
        if candidate is None and mode == "gaia":
            return scored(0.0, reason="missing_answer_file")
        return grade_answer(mode, expected, candidate)
    except InvalidTask as error:
        return invalid_task(str(error))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("aime", "gaia", "satbench", "gpqa-diamond"))
    parser.add_argument("expected", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--logs-dir", type=Path, default=Path("/logs/verifier"))
    args = parser.parse_args(argv)
    try:
        reward = grade_files(args.mode, args.expected, args.candidate)
    except Exception as error:
        reward = infra_error(f"{type(error).__name__}: {error}")
    write_reward(args.logs_dir, reward)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

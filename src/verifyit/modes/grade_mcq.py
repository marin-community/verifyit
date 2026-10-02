# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

"""Mode mcq: the option letter the candidate wrote on its ``Answer:`` line.

Extraction is the nemotron_gym MCQA pattern, taking the last ``Answer: X`` in the output. Half of
the Nemotron prompts ask for ``Answer: \\boxed{X}`` and models also write ``**Answer:** (X)``, so
``\\boxed{}``, markdown emphasis, backticks, and brackets around the letter are dropped before
matching. The original verifier fell back to any trailing single letter when that pattern missed;
the fallback scores prose that never states an answer, so it is not reproduced here. Output with no
``Answer:`` line scores zero, as does a letter outside ``A``..the last option.
"""

import math
import re
import string
from collections.abc import Sequence
from enum import StrEnum
from pathlib import Path

from verifyit.grade import InvalidTask, Reward, empty_output_policy, read_output, scored
from verifyit.spec import McqSpec

ANSWER = re.compile(r"Answer\s*:\s*(?!Answer)\s*([A-Za-z0-9])(?![A-Za-z0-9])\s*")
BOXED_LETTER = re.compile(r"\\boxed\{\s*([A-Za-z0-9])\s*\}")
WRAPPERS = re.compile(r"[*`_()\[\]]")
MAX_OPTIONS = len(string.ascii_uppercase)


class LikelihoodScoring(StrEnum):
    MOST_LIKELY = "most_likely"
    PROBABILITY_MASS = "probability_mass"


def grade_mcq_likelihoods(
    likelihoods: Sequence[float],
    correct_indices: Sequence[int],
    *,
    normalization_lengths: Sequence[int],
    policy: LikelihoodScoring,
) -> Reward:
    """Grade choice likelihoods by first argmax or stable correct-answer mass.

    Normalization lengths encode the task's raw, character, byte, or token policy.
    Raw likelihoods use all ones. Correct indices may name several alternatives;
    repeated indices never increase probability mass. Malformed vectors raise
    InvalidTask, so the dispatch boundary emits zero without a reward file.
    """
    if not isinstance(policy, LikelihoodScoring):
        raise InvalidTask("unknown MCQ likelihood scoring policy")
    if (
        not isinstance(normalization_lengths, Sequence)
        or not normalization_lengths
        or any(type(length) is not int or length <= 0 for length in normalization_lengths)
    ):
        raise InvalidTask("MCQ likelihood normalization requires positive integer lengths")
    options = len(normalization_lengths)
    if (
        not isinstance(correct_indices, Sequence)
        or not correct_indices
        or any(type(index) is not int or not 0 <= index < options for index in correct_indices)
    ):
        raise InvalidTask("MCQ requires correct indices within the declared choices")
    if not isinstance(likelihoods, Sequence) or len(likelihoods) != options:
        raise InvalidTask("MCQ requires one finite likelihood per choice")
    try:
        if any(
            isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)
            for value in likelihoods
        ):
            raise InvalidTask("MCQ likelihoods must be finite numbers")
        scores = [value / length for value, length in zip(likelihoods, normalization_lengths, strict=True)]
    except OverflowError as error:
        raise InvalidTask("MCQ likelihoods must be finite numbers") from error
    selected = max(range(options), key=scores.__getitem__)
    correct = sorted(set(correct_indices))
    if policy is LikelihoodScoring.MOST_LIKELY:
        return scored(float(selected in correct), selected_index=selected, correct_indices=correct)
    maximum = scores[selected]
    weights = [math.exp(value - maximum) for value in scores]
    denominator = math.fsum(weights)
    return scored(
        math.fsum(weights[index] for index in correct) / denominator,
        selected_index=selected,
        correct_indices=correct,
        probabilities=[weight / denominator for weight in weights],
    )


def answer_letters(text: str) -> list[str]:
    """Every letter stated on an ``Answer:`` line, wrappers around the letter removed."""
    return ANSWER.findall(WRAPPERS.sub("", BOXED_LETTER.sub(r"\1", text)))


def grade_mcq_candidate(spec: McqSpec, candidate: str) -> Reward:
    """Score an extracted MCQ option letter against a validated task spec.

    The caller extracts the candidate from its own output format. An empty candidate
    means no answer was found; an option outside the declared range scores zero.
    """
    empty_output_policy(spec)
    if not 1 <= spec.options <= MAX_OPTIONS:
        raise InvalidTask(f"mcq options must be 1..{MAX_OPTIONS}, got {spec.options}")
    letters = string.ascii_uppercase[: spec.options]
    expected = spec.expected.strip().upper()
    if expected not in letters:
        raise InvalidTask(f"mcq expected {spec.expected!r} is not one of {letters!r}")

    extracted = candidate.strip().upper()
    if not extracted:
        return scored(0.0, reason="no_answer_line", expected=expected)
    if extracted not in letters:
        return scored(0.0, reason="out_of_range", extracted=extracted, expected=expected)
    return scored(float(extracted == expected), extracted=extracted, expected=expected)


def grade(spec: McqSpec, tests_dir: Path, workspace: Path) -> Reward:
    no_answer_line = grade_mcq_candidate(spec, "")
    text = read_output(spec, workspace)
    if text is None:
        return scored(0.0, reason="no_output")
    matches = answer_letters(text)
    if not matches:
        return no_answer_line
    return grade_mcq_candidate(spec, matches[-1])

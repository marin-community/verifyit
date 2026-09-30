# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

"""JEEBench's prepared-answer scoring composed from exact and numeric modes."""

import math
import re

from verifyit.adapters.skyrl import grade_literal_candidate
from verifyit.grade import Reward, invalid_task, scored
from verifyit.modes.grade_math import grade_numeric_candidate
from verifyit.spec import NumericSpec

LETTERS = "ABCD"
UNSUPPORTED_LABEL = re.compile("[E-Z]")


def grade_jee_answer(expected: object, candidate: object, question_type: str) -> Reward:
    """Score the caller's source-extracted boxed value, retaining subset credit.

    Source A-D membership is case sensitive. Unsupported uppercase labels and
    malformed references fail closed rather than matching empty/filter-only sets.
    Numeric conversion is Python float, followed by the source absolute .01 rule.
    """
    if not isinstance(question_type, str) or question_type not in {"MCQ", "MCQ(multiple)", "Integer", "Numeric"}:
        return invalid_task("unknown JEEBench question type")
    if question_type in {"MCQ", "MCQ(multiple)"}:
        if not isinstance(expected, str) or UNSUPPORTED_LABEL.search(expected):
            return invalid_task("JEEBench choice reference contains an unsupported label")
        reference = "".join(letter for letter in LETTERS if letter in expected)
        if not reference or (question_type == "MCQ" and len(reference) != 1):
            return invalid_task("JEEBench choice reference must define a nonempty valid option set")
        if not isinstance(candidate, str) or UNSUPPORTED_LABEL.search(candidate):
            return scored(0, reason="missing_or_unsupported_candidate_label")
        answer = "".join(letter for letter in LETTERS if letter in candidate)
        exact = grade_literal_candidate(reference, answer)
        if question_type == "MCQ" or exact.reward == 1:
            return exact
        membership = [grade_literal_candidate(letter, option).reward for option in answer for letter in reference]
        matched = sum(membership)
        return scored(0.25 * len(answer) if matched == len(answer) else 0, matched=matched, selected=len(answer))
    if isinstance(expected, bool) or not isinstance(expected, str | int | float):
        return invalid_task("JEEBench numeric reference must be a string or nonboolean number")
    try:
        reference_value = float(expected)
    except (TypeError, ValueError, OverflowError):
        return invalid_task("JEEBench numeric reference is not a valid number")
    if not math.isfinite(reference_value):
        return invalid_task("JEEBench numeric reference must be finite")
    if not isinstance(candidate, str):
        return scored(0, reason="missing_or_nonstring_candidate")
    try:
        value = float(candidate)
    except (TypeError, ValueError, OverflowError):
        return scored(0, reason="invalid_numeric_candidate")
    return grade_numeric_candidate(NumericSpec(reference_value, tolerance_abs=0.01, tolerance_rel=0), value)

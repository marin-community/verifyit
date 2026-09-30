# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

"""Client extraction and canonicalization for SkyRL's existing exact grader."""

import json
import math
import re
import string
from decimal import Decimal, InvalidOperation
from fractions import Fraction

from verifyit.grade import InvalidTask, Reward, scored
from verifyit.modes.grade_exact import grade_exact_candidate
from verifyit.spec import ExactSpec

TEX_FRACTION = re.compile(r"\\[dt]?frac\{(-?\d+(?:\.\d+)?)\}\{(-?\d+(?:\.\d+)?)\}")
SLASH_FRACTION = re.compile(r"(-?\d+(?:\.\d+)?)/(-?\d+(?:\.\d+)?)")
RATIO = re.compile(r"(-?\d+):(-?\d+)")
PLAIN_DECIMAL = re.compile(r"-?\d+(?:\.\d+)?")
GSM8K_FINAL = re.compile(r"#### (-?(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(?:\.[0-9]+)?)")
GSM8K_STRICT = re.compile(r"#### (\-?[0-9\.\,]+)")
ANSWER_TAG = re.compile(r"<answer>(.*?)</answer>", re.DOTALL)


def grade_literal_candidate(expected: str, candidate: str) -> Reward:
    """Compare literal strings through the existing exact mode's strict options."""
    spec = ExactSpec(expected=(expected,), ignore_case=False, ignore_whitespace=False, strip_outer_whitespace=False)
    return grade_exact_candidate(spec, candidate)


def grade_gsm8k_strict(expected: str, response: str, *, format_score: float = 0.0) -> Reward:
    """Score the first source marker; the caller owns turn termination and feedback."""
    _gsm8k_expected(expected)
    match = GSM8K_STRICT.search(response)
    if match is None:
        return scored(0.0, reason="missing_answer_marker")
    answer = match.group(1).replace(",", "")
    result = grade_gsm8k_extracted(expected, answer)
    return scored(result.reward + (1.0 - result.reward) * format_score, **result.detail)


def _gsm8k_expected(expected: str) -> Decimal:
    try:
        value = Decimal(expected)
    except (InvalidOperation, ValueError, TypeError) as error:
        raise InvalidTask("GSM8K expected answer must be a finite decimal") from error
    if not value.is_finite():
        raise InvalidTask("GSM8K expected answer must be a finite decimal")
    return value


def grade_gsm8k_extracted(expected: str, candidate: str) -> Reward:
    """Validate numeric task data before literal strict/flexible comparison."""
    _gsm8k_expected(expected)
    return grade_literal_candidate(expected, candidate)


def _qa_normalize(answer: str) -> str:
    lower = answer.lower()
    unpunctuated = "".join(character for character in lower if character not in string.punctuation)
    return " ".join(re.sub(r"\b(a|an|the)\b", " ", unpunctuated).split())


def grade_search_em(targets: str | list[str], response: str) -> Reward:
    """Extract the last answer tag and compare normalized alternatives with exact."""
    matches = list(ANSWER_TAG.finditer(response))
    if not matches:
        return scored(0.0, reason="missing_answer_tag")
    candidate = _qa_normalize(matches[-1].group(1).strip())
    alternatives = [targets] if isinstance(targets, str) else targets
    results = [grade_literal_candidate(_qa_normalize(target), candidate) for target in alternatives]
    return scored(max((result.reward for result in results), default=0.0), extracted=candidate)


def grade_rounded_candidate(expected: float, candidate: float | None) -> Reward:
    """Compare Python banker-rounded values through exact, with finite task data."""
    if not math.isfinite(expected):
        raise InvalidTask("rounded expected answer must be finite")
    if candidate is None or not math.isfinite(candidate):
        return scored(0.0, reason="missing_or_nonfinite_candidate")
    return grade_literal_candidate(str(round(expected)), str(round(candidate)))


def _valid_grid(value: object) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and isinstance(value[0], list)
        and bool(value[0])
        and all(isinstance(row, list) and len(row) == len(value[0]) for row in value)
        and all(type(cell) is int and 0 <= cell <= 9 for row in value for cell in row)
    )


def grade_grid_candidate(expected: object, candidate: object) -> Reward:
    """Compare validated grid serialization without flattening type or row order."""
    if not _valid_grid(expected):
        raise InvalidTask("expected grid must be rectangular integer palette 0..9")
    if not _valid_grid(candidate):
        return scored(0.0, reason="invalid_candidate_grid")
    return grade_literal_candidate(json.dumps(expected), json.dumps(candidate))


def _rational(answer: str) -> Fraction | None:
    candidate = answer.replace(r"\left", "").replace(r"\right", "").strip()
    for pattern in (TEX_FRACTION, SLASH_FRACTION, RATIO):
        match = pattern.fullmatch(candidate)
        if match is not None:
            denominator = Fraction(match.group(2))
            return Fraction(match.group(1)) / denominator if denominator else None
    return Fraction(candidate) if PLAIN_DECIMAL.fullmatch(candidate) else None


def grade_aime_candidate(expected: str, candidate: str) -> Reward:
    """Score source-normalized AIME answers by literal or exact rational equality.

    The caller retains AIME's tail extraction and text normalization. Strict-box
    scoring is a separate whitespace-sensitive contract; this helper does not implement it.
    """
    spec = ExactSpec(expected=(expected,))
    if candidate == expected:
        return grade_exact_candidate(spec, candidate)
    expected_value, candidate_value = _rational(expected), _rational(candidate)
    if expected_value is None or candidate_value is None:
        return scored(0.0, extracted=candidate, expected=[expected])
    return grade_exact_candidate(ExactSpec(expected=(str(expected_value),)), str(candidate_value))


def grade_gsm8k_final_line(expected: str, response: str) -> Reward:
    """Score a standalone final ``#### number`` line without float rounding."""
    lines = response.strip().splitlines()
    match = GSM8K_FINAL.fullmatch(lines[-1]) if lines else None
    if match is None:
        return scored(0.0, reason="missing_final_answer")
    candidate = match.group(1).replace(",", "")
    expected_value = _gsm8k_expected(expected)
    return grade_exact_candidate(ExactSpec(expected=(str(Fraction(expected_value)),)), str(Fraction(candidate)))

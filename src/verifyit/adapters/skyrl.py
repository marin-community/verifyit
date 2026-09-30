# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

"""Exact answer boundaries for SkyRL's prepared arithmetic tasks."""

import re
from decimal import Decimal
from fractions import Fraction

from verifyit.grade import Reward, scored
from verifyit.modes.grade_exact import grade_exact_candidate
from verifyit.spec import ExactSpec

TEX_FRACTION = re.compile(r"\\[dt]?frac\{(-?\d+(?:\.\d+)?)\}\{(-?\d+(?:\.\d+)?)\}")
SLASH_FRACTION = re.compile(r"(-?\d+(?:\.\d+)?)/(-?\d+(?:\.\d+)?)")
RATIO = re.compile(r"(-?\d+):(-?\d+)")
PLAIN_DECIMAL = re.compile(r"-?\d+(?:\.\d+)?")
GSM8K_FINAL = re.compile(r"#### (-?(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(?:\.[0-9]+)?)")


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
    scoring remains literal and must use the exact primitive directly.
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
    expected_value = Decimal(expected)
    if not expected_value.is_finite():
        return scored(0.0, extracted=candidate, expected=[expected])
    return grade_exact_candidate(ExactSpec(expected=(str(Fraction(expected_value)),)), str(Fraction(candidate)))

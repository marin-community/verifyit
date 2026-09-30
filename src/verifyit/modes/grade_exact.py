# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

r"""Mode exact: the output compared to ``expected`` as strings, after normalization.

Two candidates are tried, and either one matching scores 1: the content of the last ``\boxed{}``
when the output has one, and the whole output.

A single expected entry must equal the candidate. Several expected entries make the candidate a
list: it is split on newlines and commas, empty items are dropped, and the items must match the
expected entries in order when ``ordered``, otherwise as a multiset.

``ignore_case`` casefolds both sides. ``ignore_whitespace`` collapses every run of whitespace to a
single space. Outer whitespace is stripped by default; set ``strip_outer_whitespace=False``
with ``ignore_whitespace=False`` for literal boundary comparison.

``substring=True`` requires one nonempty normalized reference contained in the candidate.
It is an explicit benchmark contract; equality remains the default.
"""

import re
from collections import Counter
from pathlib import Path

from verifyit.grade import InvalidTask, Reward, read_output, scored
from verifyit.modes.extract import extract_boxed
from verifyit.spec import ExactSpec

ITEM_SEPARATOR = re.compile(r"[\n,]")
MAX_DETAIL_CHARS = 400


def _normalize(text: str, spec: ExactSpec) -> str:
    value = text.strip() if spec.strip_outer_whitespace else text
    if spec.ignore_whitespace:
        value = re.sub(r"\s+", " ", value)
    return value.casefold() if spec.ignore_case else value


def _items(text: str, spec: ExactSpec) -> list[str]:
    items = (_normalize(part, spec) for part in ITEM_SEPARATOR.split(text))
    return [item for item in items if item]


def _matches(candidate: str, spec: ExactSpec) -> bool:
    if spec.substring:
        return _normalize(spec.expected[0], spec) in _normalize(candidate, spec)
    if len(spec.expected) == 1:
        return _normalize(candidate, spec) == _normalize(spec.expected[0], spec)
    expected = [_normalize(entry, spec) for entry in spec.expected]
    items = _items(candidate, spec)
    if spec.ordered:
        return items == expected
    return Counter(items) == Counter(expected)


def _validate_spec(spec: ExactSpec) -> None:
    if not spec.expected or any(not isinstance(value, str) for value in spec.expected):
        raise InvalidTask("exact expects at least one expected string")
    if any(
        type(value) is not bool
        for value in (
            spec.ignore_case,
            spec.ignore_whitespace,
            spec.ordered,
            spec.strip_outer_whitespace,
            spec.substring,
        )
    ):
        raise InvalidTask("exact normalization flags must be booleans")
    if spec.substring and (len(spec.expected) != 1 or not _normalize(spec.expected[0], spec)):
        raise InvalidTask("exact substring expects one nonempty normalized reference")


def grade_exact_candidate(spec: ExactSpec, candidate: str) -> Reward:
    """Score answer content after the caller extracts it from its submission format."""
    _validate_spec(spec)
    return scored(
        float(_matches(candidate, spec)),
        extracted=candidate.strip()[:MAX_DETAIL_CHARS],
        expected=list(spec.expected),
    )


def grade(spec: ExactSpec, tests_dir: Path, workspace: Path) -> Reward:
    _validate_spec(spec)

    text = read_output(spec, workspace)
    if text is None:
        return scored(0.0, reason="no_output")
    boxed = extract_boxed(text)
    candidates = [boxed, text] if boxed is not None else [text]
    result = grade_exact_candidate(spec, candidates[0])
    if result.reward or len(candidates) == 1:
        return result
    fallback = grade_exact_candidate(spec, candidates[1])
    return scored(fallback.reward, **result.detail)

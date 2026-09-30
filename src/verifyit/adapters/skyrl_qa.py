# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0
"""QA client composition after the source's normalization and token extraction."""

from collections.abc import Sequence, Set

from verifyit.adapters.skyrl import grade_literal_candidate
from verifyit.grade import InvalidTask, Reward, scored


def grade_qa_exact(candidate: str, references: Sequence[str]) -> Reward:
    """Compare source-normalized alternatives without adding normalization."""
    if not isinstance(candidate, str) or isinstance(references, (str, bytes)):
        raise InvalidTask("QA requires a string candidate and a sequence of normalized references")
    if any(not isinstance(reference, str) for reference in references):
        raise InvalidTask("QA normalized references must be strings")
    results = [grade_literal_candidate(reference, candidate) for reference in references]
    return scored(max((result.reward for result in results), default=0.0))


def grade_qa_token_sets(candidate: Set[str], reference: Set[str]) -> Reward:
    """Source set-token F1, using exact for token identity and client aggregation."""
    if not isinstance(candidate, Set) or not isinstance(reference, Set):
        raise InvalidTask("QA F1 requires token sets")
    if any(not isinstance(token, str) for token in [*candidate, *reference]):
        raise InvalidTask("QA F1 tokens must be strings")
    if not candidate or not reference:
        return scored(0.0, overlap=0, precision=0.0, recall=0.0)
    overlap = sum(grade_qa_exact(token, sorted(reference)).reward for token in sorted(candidate))
    precision = overlap / len(candidate)
    recall = overlap / len(reference)
    reward = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return scored(reward, overlap=overlap, precision=precision, recall=recall)

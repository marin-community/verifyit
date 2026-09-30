# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

import math
from decimal import Decimal, localcontext

import pytest

from verifyit.adapters.harness_probability import probability_mass
from verifyit.grade import InvalidTask


def test_mass_includes_multiple_correct_alternatives_not_argmax():
    result = probability_mass([1, 0, 1], [(math.log(value), False) for value in (0.2, 0.5, 0.3)])
    assert result.reward == pytest.approx(0.5)


def test_finite_underflow_uses_defined_probability_ratio():
    result = probability_mass([1, 0], [(-1000, False), (-1001, False)])
    assert result.reward == pytest.approx(1 / (1 + math.exp(-1)))


def test_arbitrary_choice_count_and_ties():
    assert probability_mass([1] + [0] * 29, [(-1, True)] * 30).reward == pytest.approx(1 / 30)


@pytest.mark.parametrize(
    "labels,responses",
    [
        ([], []),
        ([0], [(-1, False)]),
        ([True], [(-1, False)]),
        ([2], [(-1, False)]),
        ([1, 0], [(-1, False)]),
        ([1], [(float("nan"), False)]),
        ([1], [(float("-inf"), False)]),
        ([1], [(1, False)]),
        ([1], [(-1, 1)]),
        ([1], [(-1,)]),
        ([1], [(10**1000, False)]),
    ],
)
def test_malformed_evidence_cannot_score(labels, responses):
    with pytest.raises(InvalidTask):
        probability_mass(labels, responses)


def test_all_correct_mass_is_exactly_one_despite_probability_rounding():
    likelihoods = [-4.6480028589515, -3.7412643461618327, -1.128800860050413, -3.7261393895864736]
    assert probability_mass([1] * 4, [(value, False) for value in likelihoods]).reward == 1


def test_underflow_mass_matches_high_precision_reference():
    with localcontext() as context:
        context.prec = 80
        weights = [Decimal(-1000).exp(), Decimal(-1001).exp()]
        expected = float(weights[0] / sum(weights))
    assert probability_mass([1, 0], [(-1000, False), (-1001, False)]).reward == pytest.approx(expected, abs=1e-15)

# Copyright 2026 The Marin Authors
# SPDX-License-Identifier: Apache-2.0
"""Shared validation for pinned harness task contracts."""

import functools
import math
from importlib import import_module

from verifyit.grade import InvalidTask


def validate_default_filter(task, label: str) -> None:
    """Require the unmodified harness default ensemble and TakeFirst constructor."""
    ensemble_type = import_module("lm_eval.api.filter").FilterEnsemble
    take_first = import_module("lm_eval.filters.selection").TakeFirstFilter
    filters = task._filters
    if (
        task.config.filter_list is not None
        or len(filters) != 1
        or type(filters[0]) is not ensemble_type
        or filters[0].name != "none"
        or "apply" in vars(filters[0])
    ):
        raise InvalidTask(f"{label} requires the default response filter")
    constructors = filters[0].filters
    if (
        len(constructors) != 1
        or not isinstance(constructors[0], functools.partial)
        or constructors[0].func is not take_first
        or constructors[0].args
        or constructors[0].keywords
    ):
        raise InvalidTask(f"{label} requires the unmodified TakeFirstFilter")


def log_likelihoods(responses, label: str) -> list[float]:
    """Decode finite, nonpositive likelihoods with the source greedy flag intact."""
    values = []
    for response in responses:
        if not isinstance(response, (tuple, list)) or len(response) != 2 or type(response[1]) is not bool:
            raise InvalidTask(f"{label} likelihood responses must be (number, bool) pairs")
        value = response[0]
        try:
            finite = type(value) in (int, float) and math.isfinite(value)
        except OverflowError:
            finite = False
        if not finite or value > 0:
            raise InvalidTask(f"{label} log-likelihoods must be finite and nonpositive")
        values.append(value)
    return values

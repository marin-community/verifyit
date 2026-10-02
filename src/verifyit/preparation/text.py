"""Lossless text capture followed by named, potentially grade-affecting policies."""

import re
import string
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, cast

from harbor_config.errors import error_category

from verifyit.grade import Status
from verifyit.preparation.errors import PreparationFailure


class TextPolicy(StrEnum):
    HARNESS_EXACT = "harness_exact_v1"
    IDENTITY = "identity"


@dataclass(frozen=True)
class TextInputs:
    candidate: str
    references: tuple[str, ...]


@dataclass(frozen=True)
class TextNormalization:
    policy: TextPolicy = TextPolicy.HARNESS_EXACT
    regexes_to_ignore: tuple[str, ...] = ()
    ignore_case: bool = False
    ignore_punctuation: bool = False
    ignore_numbers: bool = False


@dataclass(frozen=True)
class PreparedText:
    raw: TextInputs
    candidate: str
    references: tuple[str, ...]
    normalization: TextNormalization


def structure_text(candidate: str, references: Sequence[str]) -> TextInputs | PreparationFailure:
    """Snapshot strings without filtering, coercion, reordering, or normalization."""
    if not references or any(not isinstance(reference, str) for reference in references):
        return PreparationFailure(
            Status.INVALID_TASK,
            error_category("InvalidTask"),
            "InvalidTask",
            "exact_match references must be a nonempty sequence of strings",
            "structure",
        )
    if not isinstance(candidate, str):
        return PreparationFailure(
            Status.INVALID_TASK,
            error_category("InvalidTask"),
            "InvalidTask",
            "exact_match candidate must be a string",
            "structure",
        )
    return TextInputs(candidate, tuple(references))


def normalize_text(
    inputs: TextInputs | PreparationFailure, normalization: TextNormalization
) -> PreparedText | PreparationFailure:
    """Apply the selected policy, retaining its input snapshot and effective options.

    Harness policy deliberately uses separate fixed-width NumPy arrays for the
    candidate and references. Combining their batches changes Unicode lowering.
    """
    if isinstance(inputs, PreparationFailure):
        return inputs
    if not isinstance(normalization.policy, TextPolicy) or any(
        not isinstance(flag, bool)
        for flag in (normalization.ignore_case, normalization.ignore_punctuation, normalization.ignore_numbers)
    ):
        return PreparationFailure(
            Status.INVALID_TASK,
            error_category("InvalidTask"),
            "InvalidTask",
            "invalid text normalization policy or flags",
            "normalize",
        )
    if not isinstance(normalization.regexes_to_ignore, tuple) or any(
        not isinstance(pattern, str) for pattern in normalization.regexes_to_ignore
    ):
        return PreparationFailure(
            Status.INVALID_TASK,
            error_category("InvalidTask"),
            "InvalidTask",
            "normalization regexes must be a tuple of strings",
            "normalize",
        )
    if normalization.policy == TextPolicy.IDENTITY:
        if normalization.regexes_to_ignore or any(
            (normalization.ignore_case, normalization.ignore_punctuation, normalization.ignore_numbers)
        ):
            return PreparationFailure(
                Status.INVALID_TASK,
                error_category("InvalidTask"),
                "InvalidTask",
                "identity policy does not accept normalization options",
                "normalize",
            )
        return PreparedText(inputs, inputs.candidate, inputs.references, normalization)
    try:
        patterns = tuple(re.compile(pattern) for pattern in normalization.regexes_to_ignore)
    except re.error as error:
        return PreparationFailure(
            Status.INVALID_TASK,
            error_category(type(error).__name__),
            type(error).__name__,
            str(error),
            "normalize",
        )
    try:
        import numpy as np  # noqa: PLC0415
    except ImportError as error:
        return PreparationFailure(
            Status.INFRA_ERROR,
            error_category(type(error).__name__),
            type(error).__name__,
            str(error),
            "normalize",
        )
    batches = []
    for values in ((inputs.candidate,), inputs.references):
        for pattern in patterns:
            values = tuple(pattern.sub("", value) for value in values)
        array = np.asarray(values)
        if normalization.ignore_case:
            array = np.char.lower(array)
        for enabled, characters in (
            (normalization.ignore_punctuation, string.punctuation),
            (normalization.ignore_numbers, string.digits),
        ):
            if enabled:
                array = np.char.translate(array, table=cast(Any, str.maketrans("", "", characters)))
        batches.append(tuple(array.tolist()))
    return PreparedText(inputs, batches[0][0], batches[1], normalization)

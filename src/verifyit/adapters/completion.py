"""Normalize provider completion fields before benchmark-specific extraction."""

import re
from dataclasses import dataclass
from enum import StrEnum

REASONING_END_MARKERS = ("</think>", "<|end_think|>")
BOX_START = re.compile(r"\\(?:boxed|fbox)\s*\{")


class CompletionStatus(StrEnum):
    COMPLETED = "completed"
    TRUNCATED = "truncated"
    FAILED = "failed"


@dataclass(frozen=True)
class Completion:
    content: str
    reasoning: str = ""
    status: CompletionStatus = CompletionStatus.COMPLETED


def final_text(text: str) -> str:
    """Remove a preceding inline reasoning trace using the last end marker."""
    boundary = max(
        (index + len(marker) for marker in REASONING_END_MARKERS if (index := text.rfind(marker)) >= 0),
        default=0,
    )
    return text[boundary:]


def answer_text(completion: Completion, *, require_reasoning_box: bool) -> str:
    """Prefer final content, allowing completed reasoning-only answers explicitly.

    Math integrations require boxed reasoning answers. MCQ integrations may use
    their own final-answer extraction pattern on completed reasoning instead.
    """
    if completion.content:
        return final_text(completion.content)
    if completion.status != CompletionStatus.COMPLETED:
        return ""
    if require_reasoning_box and not BOX_START.search(completion.reasoning):
        return ""
    return final_text(completion.reasoning)

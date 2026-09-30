"""Native existing-mode scoring after harness-owned response filtering.

These functions do not invoke source scorers. Unknown metric options fail closed.
Task loading, extraction filters and corpus aggregations remain caller-owned.
"""

import math
import re
import string
from collections.abc import Sequence
from typing import Any, cast

from verifyit.adapters.harness_agieval import agieval_config_profile, agieval_task_metrics
from verifyit.adapters.harness_math_literal import hendrycks_config_profile, hendrycks_task_metrics
from verifyit.adapters.harness_probability import truthfulqa_mc2_profile, truthfulqa_task_metrics
from verifyit.adapters.harness_profiles import generation_profile, profile_task_metrics
from verifyit.grade import InvalidTask, Reward
from verifyit.modes.grade_exact import grade_exact_candidate
from verifyit.modes.grade_mcq import grade_mcq_candidate
from verifyit.spec import ExactSpec, McqSpec


def exact_match(candidate: str, references: Sequence[str], **options) -> Reward:
    """Harness exact_match normalization, then literal equality against any reference."""
    allowed = {"regexes_to_ignore", "ignore_case", "ignore_punctuation", "ignore_numbers"}
    if unknown := options.keys() - allowed:
        raise InvalidTask(f"unsupported exact_match options: {sorted(unknown)}")
    if not references:
        raise InvalidTask("exact_match requires at least one reference")

    if any(not isinstance(reference, str) for reference in references):
        raise InvalidTask("exact_match references must be strings")
    if not isinstance(candidate, str):
        raise InvalidTask("exact_match candidate must be a string")
    if any(not isinstance(options.get(flag, False), bool) for flag in allowed - {"regexes_to_ignore"}):
        raise InvalidTask("exact_match normalization flags must be booleans")

    def normalize(values: Sequence[str]) -> list[str]:
        # NumPy's fixed-width Unicode lowering can truncate expanding characters.
        # Python str.lower is NOT equivalent for e.g. U+0130; use the source API.
        import numpy as np  # noqa: PLC0415

        for pattern in options.get("regexes_to_ignore") or ():
            values = [re.sub(pattern, "", value) for value in values]
        array = np.asarray(values)
        if options.get("ignore_case", False):
            array = np.char.lower(array)
        for flag, characters in (("ignore_punctuation", string.punctuation), ("ignore_numbers", string.digits)):
            if options.get(flag, False):
                array = np.char.translate(array, table=cast(Any, str.maketrans("", "", characters)))
        return array.tolist()

    value = normalize([candidate])[0]
    normalized_references = normalize(references)
    results = [
        grade_exact_candidate(
            ExactSpec((reference,), ignore_case=False, ignore_whitespace=False, strip_outer_whitespace=False),
            value,
        )
        for reference in normalized_references
    ]
    return max(results, key=lambda result: result.reward)


def likelihood_choice(
    choices: Sequence[str], likelihoods: Sequence[float], gold: Sequence[int], normalization: str = "raw"
) -> Reward:
    """Select the first maximum likelihood, then grade its MCQ option.

    Character and UTF-8 byte normalization deliberately differ. Source F1/MCC
    aggregators still require original (gold, selected index) values.
    """
    if normalization not in {"raw", "characters", "bytes"}:
        raise InvalidTask(f"unsupported likelihood normalization: {normalization}")
    if not choices or len(choices) != len(likelihoods):
        raise InvalidTask("likelihood choices require nonempty options and one likelihood per option")
    if any(not isinstance(choice, str) for choice in choices):
        raise InvalidTask("likelihood choices must be strings")
    if not gold or any(type(index) is not int or index < 0 or index >= len(choices) for index in gold):
        raise InvalidTask("likelihood gold index is outside the available choices")
    lengths = [
        1 if normalization == "raw" else len(value if normalization == "characters" else value.encode())
        for value in choices
    ]
    if any(length == 0 for length in lengths):
        raise InvalidTask("normalized likelihood choices must be nonempty")
    if any(not math.isfinite(value) for value in likelihoods):
        raise InvalidTask("likelihood values must be finite")
    scores = [value / length for value, length in zip(likelihoods, lengths, strict=True)]
    selected = max(range(len(scores)), key=scores.__getitem__)
    if len(choices) > 26:
        return exact_match(str(selected), [str(index) for index in gold])
    results = [
        grade_mcq_candidate(McqSpec(string.ascii_uppercase[index], len(choices)), string.ascii_uppercase[selected])
        for index in gold
    ]
    return max(results, key=lambda result: result.reward)


def native_config_route(config: dict) -> str | None:
    """Recognize implemented source branches; unknown options are not native coverage."""
    if agieval_config_profile(config):
        return "agieval_mcqa"
    if hendrycks_config_profile(config):
        return "hendrycks_literal_exact"
    if truthfulqa_mc2_profile(config):
        return "truthfulqa_mc2"
    if config.get("process_results") or config.get("class"):
        return None
    profile = generation_profile(config)
    if profile is not None:
        return profile
    output = config.get("output_type", "generate_until")
    metrics = config.get("metric_list")
    if metrics is None:
        metrics = (
            [{"metric": "acc"}, {"metric": "acc_norm"}]
            if output == "multiple_choice"
            else [{"metric": "exact_match"}] if output == "generate_until" else []
        )
    if not isinstance(metrics, list) or not metrics:
        return None
    metadata = {"metric", "aggregation", "higher_is_better"}
    if output == "multiple_choice":
        if all(
            isinstance(metric, dict)
            and metric.get("metric") in {"acc", "acc_norm", "acc_bytes", "f1", "mcc", "exact_match", "likelihood"}
            and not metric.keys()
            - (
                metadata
                | {
                    "weight_by_size",
                    "average",
                    "hf_evaluate",
                    "ignore_case",
                    "ignore_punctuation",
                    "ignore_numbers",
                    "regexes_to_ignore",
                    "high_is_better",
                }
            )
            for metric in metrics
        ):
            return "likelihood_choice"
    if output == "generate_until" and len(metrics) == 1:
        metric = metrics[0]
        allowed = metadata | {"regexes_to_ignore", "ignore_case", "ignore_punctuation", "ignore_numbers"}
        if isinstance(metric, dict) and metric.get("metric") == "exact_match" and not metric.keys() - allowed:
            if all(
                isinstance(metric.get(flag, False), bool)
                for flag in ("ignore_case", "ignore_punctuation", "ignore_numbers")
            ):
                regexes = metric.get("regexes_to_ignore")
                if regexes is None or (
                    isinstance(regexes, list) and all(isinstance(pattern, str) for pattern in regexes)
                ):
                    return "exact_match"
    return None


def native_task_metrics(task, doc, responses) -> dict | None:
    """Route only the pinned ConfigurableTask implementation and recognized metrics.

    None means compatibility-only source scoring is required; it is never a reward.
    Invalid recognized task/sample contracts raise InvalidTask instead of fallback.
    """
    method = task.process_results
    if (
        getattr(method, "__module__", None) != "lm_eval.api.task"
        or getattr(method, "__qualname__", None) != "ConfigurableTask.process_results"
    ):
        return None
    agieval = agieval_task_metrics(task, doc, responses)
    if agieval is not None:
        return agieval
    math_metrics = hendrycks_task_metrics(task, doc, responses)
    if math_metrics is not None:
        return math_metrics
    probability_metrics = truthfulqa_task_metrics(task, doc, responses)
    if probability_metrics is not None:
        return probability_metrics
    if task.config.process_results is not None:
        return None
    profile_metrics = profile_task_metrics(task, doc, responses, exact_match)
    if profile_metrics is not None:
        return profile_metrics
    config = {
        "output_type": task.OUTPUT_TYPE,
        "metric_list": [{"metric": metric, **task._metric_fn_kwargs.get(metric, {})} for metric in task._metric_fn_list],
    }
    route = native_config_route(config)
    if route is None:
        return None
    if route == "exact_match":
        fn = task._metric_fn_list["exact_match"]
        if getattr(fn, "__module__", None) != "lm_eval.api.metrics" or getattr(fn, "__name__", None) != "exact_match_fn":
            return None
        if len(responses) != 1:
            raise InvalidTask("generation exact_match requires one filtered response")
        candidate = responses[0]
        gold = task.doc_to_target(doc)
        if task.config.doc_to_choice is not None:
            choices = task.doc_to_choice(doc)
            if not isinstance(gold, int) or not 0 <= gold < len(choices):
                raise InvalidTask("generation target index is outside available choices")
            gold = choices[gold]
        elif task.multiple_target:
            gold = list(gold)
        elif type(gold) is not type(candidate):
            gold = type(candidate)(gold)
        references = gold if task.multiple_target else [gold]
        return {"exact_match": exact_match(candidate, references, **task._metric_fn_kwargs["exact_match"]).reward}
    choices = task.doc_to_choice(doc)
    likelihoods, greedy = zip(*responses, strict=True)
    gold = task.doc_to_text(doc) if task.multiple_input else task.doc_to_target(doc)
    if isinstance(gold, str):
        if gold not in choices:
            raise InvalidTask("choice target text is absent from choices")
        gold = choices.index(gold)
    targets = gold if task.multiple_target else [gold]
    metrics: dict[str, Any] = {}
    for metric in task._metric_fn_list:
        if metric in {"acc", "acc_norm", "acc_bytes"}:
            normalization = {"acc": "raw", "acc_norm": "characters", "acc_bytes": "bytes"}[metric]
            metrics[metric] = likelihood_choice(choices, likelihoods, targets, normalization).reward
        else:
            # Validate likelihoods/targets even when only a structured metric is requested.
            likelihood_choice(choices, likelihoods, targets)
            selected = max(range(len(likelihoods)), key=likelihoods.__getitem__)
            if metric == "exact_match":
                if any(type(flag) is not bool for flag in greedy):
                    raise InvalidTask("greedy completion flags must be booleans")
                metrics[metric] = int(any(greedy[index] for index in targets))
            elif metric == "likelihood":
                metrics[metric] = (gold, likelihoods)
            else:
                metrics[metric] = (gold, selected)
    return metrics

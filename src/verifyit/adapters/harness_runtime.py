# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

"""Execute a trusted harness corpus scorer under the script mode boundary.

This is a retained-runtime integration, not a native correctness projection.
The script returns every sample observation and corpus point metric; its zero
reward deliberately does not reinterpret unbounded or differently scaled metrics.
"""

import json
import math
import sys
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from verifyit.grade import Reward, Status, invalid_task, run
from verifyit.spec import ScriptSpec, render_spec


@dataclass(frozen=True)
class BatchResult:
    observations: tuple[Mapping[str, Any], ...]
    aggregates: Mapping[str, Any]
    verdict: Reward


def corpus_config_profile(config: Mapping[str, Any]) -> str | None:
    """Recognize the narrow retained-runtime profile without importing harness.

    This proves configuration eligibility only. Runtime module identity, metric
    callables, sample validity and the complete batch remain independently checked.
    """
    if config.get("class") is not None or config.get("process_results") is not None:
        return None
    output = config.get("output_type")
    allowed = (
        {"bleu", "chrf", "ter"}
        if output == "generate_until"
        else {"word_perplexity", "byte_perplexity", "bits_per_byte"} if output == "loglikelihood_rolling" else set()
    )
    definitions = config.get("metric_list")
    if not allowed or not isinstance(definitions, list) or not definitions:
        return None
    names = []
    for definition in definitions:
        if not isinstance(definition, Mapping) or set(definition) - {"metric", "aggregation", "higher_is_better"}:
            return None
        name = definition.get("metric")
        if not isinstance(name, str) or name not in allowed:
            return None
        direction = definition.get("higher_is_better")
        if direction is not None and not isinstance(direction, bool):
            return None
        expected = "weighted_perplexity" if name in {"word_perplexity", "byte_perplexity"} else name
        if definition.get("aggregation") not in (None, expected):
            return None
        names.append(name)
    if len(set(names)) != len(names):
        return None
    return "translation_corpus" if output == "generate_until" else "rolling_likelihood_corpus"


def score_corpus(
    source_root: Path,
    config_path: Path,
    samples: Sequence[Mapping[str, Any]],
    *,
    timeout: float = 600.0,
) -> BatchResult:
    """Run the source checkout's trusted corpus producer with JSON-only samples.

    ``source_root`` and ``config_path`` are task-owned installation metadata,
    never candidate-selected paths. Samples contain only ``doc`` and already
    filtered ``responses``. The source runner checks its narrow metric contract.
    """
    source_root = source_root.resolve()
    config_path = config_path.resolve()
    tasks_root = source_root / "lm_eval" / "tasks"
    runner = source_root / "lm_eval" / "verifyit_runtime.py"
    if not config_path.is_relative_to(tasks_root) or not config_path.is_file() or not runner.is_file():
        return BatchResult((), {}, invalid_task("trusted harness config or corpus runner is missing"))
    try:
        serialized = json.dumps({"config": str(config_path), "samples": list(samples)}, allow_nan=False)
    except (TypeError, ValueError) as error:
        return BatchResult((), {}, invalid_task(f"corpus samples must be finite JSON data: {error}"))
    with tempfile.TemporaryDirectory(prefix="verifyit-harness-corpus-") as directory:
        tests = Path(directory)
        payload = tests / "samples.json"
        payload.write_text(serialized, encoding="utf-8")
        (tests / "producer.sh").write_text('exec "$@"\n', encoding="utf-8")
        spec = ScriptSpec(
            "producer.sh",
            args=(sys.executable, str(runner), str(payload)),
            timeout=timeout,
            verdict_file="corpus-verdict.json",
        )
        spec_path = tests / "verifier.toml"
        spec_path.write_text(render_spec(spec), encoding="utf-8")
        verdict = run(spec_path, tests)
    if verdict.status != Status.SCORED:
        return BatchResult((), {}, verdict)
    observations = verdict.detail.get("observations")
    aggregates = verdict.detail.get("aggregates")
    if not isinstance(observations, list) or not all(isinstance(item, dict) for item in observations):
        raise RuntimeError("trusted corpus producer returned malformed observations")
    if len(observations) != len(samples) or not isinstance(aggregates, dict):
        raise RuntimeError("trusted corpus producer omitted samples or aggregate metrics")
    if verdict.reward != 0:
        raise RuntimeError("retained corpus runtime cannot imply a correctness reward")
    if any(set(observation) != set(aggregates) for observation in observations):
        raise RuntimeError("trusted corpus producer returned inconsistent metric coverage")
    if any(
        isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value) or value < 0
        for value in aggregates.values()
    ):
        raise RuntimeError("trusted corpus producer returned invalid corpus point metrics")
    return BatchResult(tuple(observations), aggregates, verdict)

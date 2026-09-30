# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import pytest

from verifyit.adapters.harness_runtime import score_corpus
from verifyit.grade import Status


def producer(tmp_path: Path, verdict: dict) -> tuple[Path, Path]:
    root = tmp_path / "harness"
    package = root / "lm_eval"
    tasks = package / "tasks"
    tasks.mkdir(parents=True)
    config = tasks / "fixture.yaml"
    config.write_text("task: fixture\n")
    (package / "verifyit_runtime.py").write_text(
        "import json, os\nfrom pathlib import Path\n"
        f"payload = {verdict!r}\n"
        "(Path(os.environ['VERIFYIT_LOGS_DIR']) / 'corpus-verdict.json').write_text(json.dumps(payload))\n"
    )
    return root, config


def test_failed_runtime_cannot_export_positive_source_metrics(tmp_path):
    root, config = producer(
        tmp_path,
        {"status": "infra_error", "reward": 0, "detail": {"observations": [{"acc": 1}], "aggregates": {"acc": 1}}},
    )
    result = score_corpus(root, config, [{"doc": {}, "responses": ["answer"]}])
    assert result.verdict.status == Status.INFRA_ERROR
    assert result.verdict.reward == 0
    assert result.observations == ()
    assert result.aggregates == {}


def test_runtime_preserves_unbounded_named_metrics_and_raw_observations(tmp_path):
    root, config = producer(
        tmp_path,
        {
            "status": "scored",
            "reward": 0,
            "detail": {"observations": [{"word_perplexity": [-9, 3]}], "aggregates": {"word_perplexity": 20.0855}},
        },
    )
    result = score_corpus(root, config, [{"doc": {"text": "one two three"}, "responses": [-9]}])
    assert result.verdict.status == Status.SCORED
    assert result.verdict.reward == 0
    assert result.observations == ({"word_perplexity": [-9, 3]},)
    assert result.aggregates == {"word_perplexity": 20.0855}


def test_runtime_rejects_nonfinite_json_and_missing_sample_observations(tmp_path):
    root, config = producer(
        tmp_path, {"status": "scored", "reward": 0, "detail": {"observations": [], "aggregates": {"bleu": 100}}}
    )
    invalid = score_corpus(root, config, [{"doc": {}, "responses": [float("nan")]}])
    assert invalid.verdict.status == Status.INVALID_TASK
    assert invalid.verdict.reward == 0
    assert not invalid.aggregates
    with pytest.raises(RuntimeError, match="omitted samples"):
        score_corpus(root, config, [{"doc": {}, "responses": ["answer"]}])

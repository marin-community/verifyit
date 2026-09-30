# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

"""Mode script: run the task's own grading script and read back the reward it reports.

This is the fallback for converters whose original ``test.sh`` logic fits no other mode. The script
runs in the agent's workspace with ``VERIFYIT_TESTS_DIR``, ``VERIFYIT_WORKSPACE`` and
``VERIFYIT_LOGS_DIR`` exported, and reports its reward through one of three channels, checked in
this order: ``$VERIFYIT_LOGS_DIR/reward.json`` holding the finite numeric ``spec.reward_key``,
``$VERIFYIT_LOGS_DIR/reward.txt`` holding a bare float, or a float on the last non-empty line of
stdout. Named keys require reward.json. Numeric auxiliary metrics are retained in verdict detail.
Malformed authoritative files and scripts reporting no reward produce infrastructure failures.
"""

import json
import logging
import math
import os
import tempfile
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from verifyit.grade import REWARD_JSON, REWARD_TXT, InvalidTask, Reward, scored
from verifyit.modes.extract import last_line
from verifyit.modes.run import STDERR_TAIL, run_command
from verifyit.spec import DEFAULT_REWARD_KEY, DEFAULT_WORKSPACE, ScriptSpec, Spec

SHELL = "bash"
PYTHON = "python3"

logger = logging.getLogger(__name__)


class Channel(StrEnum):
    REWARD_JSON = "reward.json"
    REWARD_TXT = "reward.txt"
    STDOUT = "stdout"


@dataclass(frozen=True)
class Completion:
    """One script run. ``exit_code`` is ``None`` when the script was killed at the timeout."""

    exit_code: int | None
    stdout: str
    stderr: str


@dataclass(frozen=True)
class Reported:
    value: float
    channel: Channel
    metrics: dict[str, float] | None = None


def grade(spec: Spec, tests_dir: Path, workspace: Path) -> Reward:
    assert isinstance(spec, ScriptSpec)
    script = tests_dir / spec.path
    if not script.is_file():
        raise InvalidTask(f"script {spec.path!r} is missing from the tests directory")

    cwd = workspace if spec.workspace == DEFAULT_WORKSPACE else Path(spec.workspace)
    interpreter = SHELL if script.suffix == ".sh" else PYTHON
    command = [interpreter, str(script), *spec.args]

    with tempfile.TemporaryDirectory(prefix="verifyit-script-") as logs:
        logs_dir = Path(logs)
        env = {
            **os.environ,
            "VERIFYIT_TESTS_DIR": str(tests_dir),
            "VERIFYIT_WORKSPACE": str(cwd),
            "VERIFYIT_LOGS_DIR": str(logs_dir),
        }
        completion = _run(command, cwd, env, spec.timeout)
        reported = _reported_reward(logs_dir, completion.stdout, spec.reward_key)

    detail: dict = {"exit_code": completion.exit_code, "stderr": completion.stderr[-STDERR_TAIL:]}
    if completion.exit_code is None:
        return scored(0.0, reason="timeout", timeout=spec.timeout, **detail)
    if reported is None:
        raise RuntimeError(
            f"script {spec.path!r} exited {completion.exit_code} without reporting a reward; "
            f"stderr tail: {completion.stderr[-STDERR_TAIL:]!r}"
        )
    detail["channel"] = reported.channel.value
    if reported.metrics is not None:
        detail["metrics"] = reported.metrics
    if not 0.0 <= reported.value <= 1.0:
        return scored(0.0, reason="reward_out_of_range", reported=reported.value, **detail)
    return scored(reported.value, **detail)


def _run(command: list[str], cwd: Path, env: dict[str, str], timeout: float) -> Completion:
    completed = run_command(command, cwd, timeout, env=env)
    if completed.timed_out:
        logger.warning("script %s exceeded %.1fs; killed its process group", command[1], timeout)
        return Completion(None, completed.stdout, completed.stderr)
    return Completion(completed.returncode, completed.stdout, completed.stderr)


def _reported_reward(logs_dir: Path, stdout: str, reward_key: str) -> Reported | None:
    json_path = logs_dir / REWARD_JSON
    if json_path.is_file():
        return _json_reward(json_path, reward_key)
    if reward_key != DEFAULT_REWARD_KEY:
        raise RuntimeError(f"named reward {reward_key!r} requires reward.json")
    text_path = logs_dir / REWARD_TXT
    if text_path.is_file():
        value = _float(text_path.read_text(errors="replace"))
        if value is None or not math.isfinite(value):
            raise RuntimeError(f"{text_path} does not contain a finite numeric reward")
        return Reported(value, Channel.REWARD_TXT)
    value = _float(last_line(stdout))
    if value is not None and not math.isfinite(value):
        raise RuntimeError("script stdout does not contain a finite numeric reward")
    return Reported(value, Channel.STDOUT) if value is not None else None


def _json_reward(path: Path, reward_key: str) -> Reported:
    try:
        payload = json.loads(path.read_text(errors="replace"))
    except ValueError as error:
        raise RuntimeError(f"{path} is not valid JSON: {error}") from error
    if not isinstance(payload, dict) or reward_key not in payload:
        raise RuntimeError(f"{path} must contain the selected reward {reward_key!r}")
    value = _float(payload[reward_key])
    if value is None or not math.isfinite(value):
        raise RuntimeError(f"{path} does not contain a finite numeric reward {reward_key!r}")
    metrics = {}
    for key, raw_value in payload.items():
        metric = _float(raw_value)
        if metric is not None:
            if not math.isfinite(metric):
                raise RuntimeError(f"{path} contains nonfinite metric {key!r}")
            metrics[key] = metric
    return Reported(value, Channel.REWARD_JSON, metrics)


def _float(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, str | int | float):
        return None
    try:
        return float(value)
    except ValueError:
        return None

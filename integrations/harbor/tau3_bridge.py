# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0
"""Run tau3's retained evaluator through ScriptSpec's explicit verdict channel."""

import json
import math
import os
import subprocess
import sys
from pathlib import Path


def normalize(result: object) -> dict:
    if not isinstance(result, dict):
        raise ValueError("tau3 result must be an object")
    status = result.get("status")
    reward = result.get("reward")
    if status in {"missing_runtime_log", "invalid_runtime_log", "tau2_runtime_log_error"}:
        return {"status": "infra_error", "reward": 0.0, "detail": {"native": result}}
    if status not in {"passed", "mismatch"}:
        raise ValueError(f"unsupported tau3 result status {status!r}")
    if isinstance(reward, bool) or not isinstance(reward, int | float) or not math.isfinite(reward):
        raise ValueError("tau3 reward must be finite numeric data")
    if not 0 <= reward <= 1:
        raise ValueError("tau3 reward lies outside the declared unit interval")
    return {"status": "scored", "reward": float(reward), "detail": {"native": result}}


def main() -> None:
    tests = Path(os.environ["VERIFYIT_TESTS_DIR"])
    logs = Path(os.environ["VERIFYIT_LOGS_DIR"])
    result_path = logs / "native-result.json"
    config_path = tests / "config.json"
    try:
        config = json.loads(config_path.read_text())
        if not isinstance(config, dict) or not isinstance(config.get("task"), dict):
            raise ValueError("tau3 config requires a task object")
        if config.get("domain") not in {"airline", "retail", "telecom", "banking_knowledge"}:
            raise ValueError("tau3 config declares an unsupported domain")
    except (OSError, ValueError) as error:
        verdict = {"status": "invalid_task", "reward": 0.0, "detail": {"error": str(error)}}
    else:
        runtime = os.environ.get("TAU3_RUNTIME_STATE_PATH", "/logs/agent/tau3_runtime_state.json")
        completed = subprocess.run(
            [
                sys.executable,
                str(tests / "evaluate.py"),
                "--config",
                str(config_path),
                "--runtime-log",
                runtime,
                "--reward",
                str(logs / "native-reward.txt"),
                "--result",
                str(result_path),
            ],
            capture_output=True,
            text=True,
        )
        try:
            if completed.returncode:
                raise RuntimeError(f"tau3 evaluator exited {completed.returncode}")
            verdict = normalize(json.loads(result_path.read_text()))
        except (OSError, ValueError, RuntimeError) as error:
            verdict = {"status": "infra_error", "reward": 0.0, "detail": {"error": str(error)}}
        verdict["detail"]["native_process"] = {"exit_code": completed.returncode, "stderr": completed.stderr[-2000:]}
    (logs / "result.json").write_text(json.dumps(verdict, allow_nan=False))


if __name__ == "__main__":
    main()

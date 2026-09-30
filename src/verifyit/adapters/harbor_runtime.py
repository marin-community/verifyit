# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

"""Run a trusted Harbor task script inside ScriptSpec and normalize its legacy reward."""

import argparse
import json
import math
import os
import subprocess
from pathlib import Path

VERDICT = "native-verdict.json"


def _numeric(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float | str):
        raise ValueError("native reward must be numeric")
    try:
        result = float(value)
    except (ValueError, OverflowError) as error:
        raise ValueError("native reward must be numeric") from error
    if not math.isfinite(result):
        raise ValueError("native reward must be finite")
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"nonfinite JSON constant {value}")


def _native_reward(logs: Path, reward_key: str) -> tuple[float, dict[str, float]]:
    reward_json = logs / "reward.json"
    if reward_json.exists():
        payload = json.loads(reward_json.read_text(), parse_constant=_reject_constant)
        if not isinstance(payload, dict) or reward_key not in payload:
            raise ValueError(f"native reward.json lacks {reward_key!r}")
        reward = _numeric(payload[reward_key])
        metrics = {key: _numeric(value) for key, value in payload.items() if key != reward_key}
        return reward, metrics
    if reward_key != "reward":
        raise ValueError(f"named reward {reward_key!r} requires reward.json")
    reward_txt = logs / "reward.txt"
    if not reward_txt.exists():
        raise ValueError("native script wrote no reward file")
    return _numeric(reward_txt.read_text().strip()), {}


def run_native(script_name: str, reward_key: str = "reward") -> dict:
    tests = Path(os.environ["VERIFYIT_TESTS_DIR"]).resolve()
    workspace = Path(os.environ["VERIFYIT_WORKSPACE"])
    legacy = Path(os.environ.get("VERIFYIT_NATIVE_LOGS_DIR", "/logs/verifier"))
    script = (tests / script_name).resolve()
    if not script.is_relative_to(tests) or not script.is_file():
        raise ValueError("native script must be a file under the trusted tests directory")
    legacy.mkdir(parents=True, exist_ok=True)
    for filename in ("reward.txt", "reward.json", "verdict.json"):
        (legacy / filename).unlink(missing_ok=True)
    completed = subprocess.run(["bash", str(script)], cwd=workspace, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(f"native script exited {completed.returncode}: {completed.stderr[-1000:]}")
    reward, metrics = _native_reward(legacy, reward_key)
    if not 0.0 <= reward <= 1.0:
        raise ValueError("native reward must be in the unit interval")
    return {"status": "scored", "reward": reward, "detail": {"native_metrics": metrics}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", help="relative source test script under the trusted tests directory")
    parser.add_argument("--reward-key", default="reward")
    args = parser.parse_args(argv)
    try:
        verdict = run_native(args.script, args.reward_key)
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        verdict = {"status": "infra_error", "reward": 0.0, "detail": {"error": f"{type(error).__name__}: {error}"}}
    private = Path(os.environ["VERIFYIT_LOGS_DIR"])
    (private / VERDICT).write_text(json.dumps(verdict, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

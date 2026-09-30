# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0
"""Run tau3's retained evaluator through ScriptSpec's explicit verdict channel."""

import hashlib
import json
import math
import os
import re
import shutil
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


def validate_assets(tests: Path, domain: str) -> None:
    manifest = json.loads((tests / "tau2-assets.json").read_text())
    if not isinstance(manifest, dict) or set(manifest) != {"revision", "domain", "files"}:
        raise ValueError("invalid tau2 asset manifest")
    if manifest["revision"] != "fc0055dc4e0a316c3f83133267fbd6faaa770992" or manifest["domain"] != domain:
        raise ValueError("tau2 manifest revision/domain mismatch")
    files = manifest["files"]
    database = "db.toml" if domain == "telecom" else "db.json"
    if not isinstance(files, dict) or not files or f"data/tau2/domains/{domain}/{database}" not in files:
        raise ValueError("tau2 manifest lacks required database assets")
    root = Path(os.environ.get("TAU2_BENCH_ROOT", "/opt/tau2-bench")).resolve()
    data_root = os.environ.get("TAU2_DATA_DIR")
    if data_root and Path(data_root).resolve() != root / "data":
        raise ValueError("tau2 data directory differs from protected assets")
    for relative, digest in files.items():
        if not isinstance(relative, str) or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("invalid tau2 manifest entry")
        path = Path(relative)
        if (
            path.is_absolute()
            or ".." in path.parts
            or not (
                (relative.startswith("src/tau2/") and relative.endswith(".py"))
                or relative.startswith(f"data/tau2/domains/{domain}/")
            )
        ):
            raise ValueError("tau2 manifest path outside protected domain/source")
        asset = root / path
        if not asset.resolve().is_relative_to(root) or asset.is_symlink():
            raise ValueError("tau2 asset escapes runtime directory")
        if hashlib.sha256(asset.read_bytes()).hexdigest() != digest:
            raise ValueError(f"tau2 asset modified: {relative}")
    # Native imports must read the checked source, not agent-written bytecode.
    for cache in (root / "src/tau2").rglob("__pycache__"):
        if cache.is_symlink() or not cache.resolve().is_relative_to(root):
            raise ValueError("tau2 bytecode cache escapes runtime directory")
        shutil.rmtree(cache)


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
        try:
            validate_assets(tests, config["domain"])
        except (OSError, ValueError) as error:
            (logs / "result.json").write_text(
                json.dumps({"status": "infra_error", "reward": 0.0, "detail": {"error": str(error)}})
            )
            return
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

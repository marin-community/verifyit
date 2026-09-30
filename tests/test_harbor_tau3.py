# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from verifyit.grade import run, write_reward
from verifyit.spec import ScriptSpec, render_spec

BRIDGE = Path(__file__).resolve().parents[1] / "integrations/harbor/tau3_bridge.py"


@pytest.mark.parametrize(
    "native_status,value,expected",
    [
        ("mismatch", 0, "scored"),
        ("passed", 1, "scored"),
        ("missing_runtime_log", 0, "infra_error"),
        ("invalid_runtime_log", 0, "infra_error"),
        ("tau2_runtime_log_error", 0, "infra_error"),
    ],
)
def test_tau3_bridge_preserves_zero_and_masks_native_runtime_errors(
    tmp_path, monkeypatch, native_status, value, expected
):
    tests = tmp_path / "tests"
    tests.mkdir()
    workspace = tmp_path / "app"
    workspace.mkdir()
    runtime = tmp_path / "runtime"
    asset = runtime / "data/tau2/domains/retail/db.json"
    asset.parent.mkdir(parents=True)
    asset.write_text("{}")
    monkeypatch.setenv("TAU2_BENCH_ROOT", str(runtime))
    monkeypatch.delenv("TAU2_DATA_DIR", raising=False)
    (tests / "tau2-assets.json").write_text(
        json.dumps(
            {
                "revision": "fc0055dc4e0a316c3f83133267fbd6faaa770992",
                "domain": "retail",
                "files": {"data/tau2/domains/retail/db.json": hashlib.sha256(asset.read_bytes()).hexdigest()},
            }
        )
    )
    native = {
        "status": native_status,
        "reward": value,
        "used_tau2_evaluator": native_status in {"passed", "mismatch"},
        "reward_info": {"reward": value, "reward_basis": ["state", "nl"], "info": {"trajectory_message_count": 3}},
    }
    # A separate native-runtime process emits the pinned evaluator's result contract.
    (tests / "evaluate.py").write_text(
        (
            "import argparse,json\n"
            "from pathlib import Path\n"
            "p=argparse.ArgumentParser()\n"
            "for n in ['config','runtime-log','reward','result']:p.add_argument('--'+n)\n"
            "a=p.parse_args()\n"
        )
        + f"Path(a.result).write_text({json.dumps(native)!r})\nPath(a.reward).write_text('0')\n"
    )
    shutil.copyfile(BRIDGE, tests / "bridge.py")
    (tests / "config.json").write_text('{"domain":"retail","task":{}}')
    (tests / "verifier.toml").write_text(render_spec(ScriptSpec(path="bridge.py", verdict_file="result.json")))
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "reward.txt").write_text("1")
    reward = run(tests / "verifier.toml", workspace)
    write_reward(logs, reward)
    assert reward.status.value == expected
    assert reward.reward == value
    assert reward.detail["native"] == native
    assert (logs / "reward.txt").exists() == (expected == "scored")


def test_tau3_bridge_rejects_modified_runtime_database(tmp_path, monkeypatch):
    tests = tmp_path / "tests"
    tests.mkdir()
    workspace = tmp_path / "app"
    workspace.mkdir()
    runtime = tmp_path / "runtime"
    asset = runtime / "data/tau2/domains/retail/db.json"
    asset.parent.mkdir(parents=True)
    asset.write_text("trusted database")
    digest = hashlib.sha256(asset.read_bytes()).hexdigest()
    (tests / "tau2-assets.json").write_text(
        json.dumps(
            {
                "revision": "fc0055dc4e0a316c3f83133267fbd6faaa770992",
                "domain": "retail",
                "files": {"data/tau2/domains/retail/db.json": digest},
            }
        )
    )
    # The retained producer would award one if tampered assets reached it.
    (tests / "evaluate.py").write_text("raise AssertionError('modified database reached evaluator')")
    asset.write_text("candidate changed database")
    monkeypatch.setenv("TAU2_BENCH_ROOT", str(runtime))
    monkeypatch.delenv("TAU2_DATA_DIR", raising=False)
    shutil.copyfile(BRIDGE, tests / "bridge.py")
    (tests / "config.json").write_text('{"domain":"retail","task":{}}')
    (tests / "verifier.toml").write_text(render_spec(ScriptSpec(path="bridge.py", verdict_file="result.json")))
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "reward.txt").write_text("1")
    reward = run(tests / "verifier.toml", workspace)
    write_reward(logs, reward)
    assert reward.status.value == "infra_error"
    assert reward.reward == 0
    assert "asset modified" in reward.detail["error"]
    assert not (logs / "reward.txt").exists()

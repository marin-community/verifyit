# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

"""Consequential ScriptSpec behavior for legacy Harbor reward files."""

import json

import pytest

from verifyit.grade import Status, run, write_reward
from verifyit.spec import ScriptSpec, render_spec


@pytest.fixture
def native_task(tmp_path, monkeypatch):
    tests = tmp_path / "tests"
    tests.mkdir()
    workspace = tmp_path / "app"
    workspace.mkdir()
    logs = tmp_path / "legacy-logs"
    logs.mkdir()
    monkeypatch.setenv("VERIFYIT_NATIVE_LOGS_DIR", str(logs))
    (tests / "native_bridge.py").write_text(
        "from verifyit.adapters.harbor_runtime import main\n"
        "raise SystemExit(main(['test.sh']))\n"
    )
    (tests / "verifier.toml").write_text(
        render_spec(ScriptSpec(path="native_bridge.py", verdict_file="native-verdict.json"))
    )
    return tests, workspace, logs


def test_native_script_zero_replaces_stale_positive_reward(native_task, tmp_path):
    tests, workspace, logs = native_task
    (logs / "reward.txt").write_text("1")
    (tests / "test.sh").write_text(
        "#!/bin/bash\n"
        'echo 0 > "$VERIFYIT_NATIVE_LOGS_DIR/reward.txt"\n'
    )
    reward = run(tests / "verifier.toml", workspace)
    assert (reward.status, reward.reward) == (Status.SCORED, 0.0)
    outer = tmp_path / "outer"
    outer.mkdir()
    (outer / "reward.txt").write_text("1")
    write_reward(outer, reward)
    assert (outer / "reward.txt").read_text().strip() == "0.0"


@pytest.mark.parametrize(
    "script,old_reward,expected_error",
    [
        ("#!/bin/bash\nexit 1\n", "1", "exited 1"),
        ('#!/bin/bash\necho 1 > "$VERIFYIT_NATIVE_LOGS_DIR/reward.txt"\nexit 7\n', "1", "exited 7"),
        ("#!/bin/bash\ntrue\n", "1", "no reward file"),
        ('#!/bin/bash\necho garbage > "$VERIFYIT_NATIVE_LOGS_DIR/reward.txt"\n', "1", "numeric"),
        (
            '#!/bin/bash\necho 1 > "$VERIFYIT_NATIVE_LOGS_DIR/reward.txt"\n'
            'echo broken > "$VERIFYIT_NATIVE_LOGS_DIR/reward.json"\n',
            "1",
            "JSON",
        ),
    ],
)
def test_native_runtime_failure_cannot_reuse_previous_reward(native_task, tmp_path, script, old_reward, expected_error):
    tests, workspace, logs = native_task
    (logs / "reward.txt").write_text(old_reward)
    (tests / "test.sh").write_text(script)
    reward = run(tests / "verifier.toml", workspace)
    assert reward.status is Status.INFRA_ERROR and reward.reward == 0.0
    assert expected_error in str(reward.detail)
    outer = tmp_path / "outer"
    outer.mkdir()
    (outer / "reward.txt").write_text("1")
    write_reward(outer, reward)
    assert not (outer / "reward.txt").exists()
    assert json.loads((outer / "verdict.json").read_text())["status"] == "infra_error"


def test_native_json_keeps_named_numeric_metrics(native_task):
    tests, workspace, _ = native_task
    (tests / "test.sh").write_text(
        "#!/bin/bash\n"
        'echo \'{"reward":0.5,"pass_rate":0.75}\' > "$VERIFYIT_NATIVE_LOGS_DIR/reward.json"\n'
    )
    reward = run(tests / "verifier.toml", workspace)
    assert (reward.status, reward.reward) == (Status.SCORED, 0.5)
    assert reward.detail["native_metrics"] == {"pass_rate": 0.75}

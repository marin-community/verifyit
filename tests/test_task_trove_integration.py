# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

WRAPPER = Path(__file__).resolve().parents[1] / "integrations/task-trove/test.sh"
SUFFIXES = ("BASE_URL", "API_KEY", "MODEL")


@pytest.mark.parametrize("configured", [None, "", "explicit"])
def test_task_trove_wrapper_maps_old_judge_capability_without_overriding_new(tmp_path, configured):
    directory = tmp_path / "bin"
    directory.mkdir()
    command = directory / "verifyit"
    command.write_text(
        f"#!{sys.executable}\nimport json, os\n"
        'names = ["VERIFYIT_JUDGE_BASE_URL", "VERIFYIT_JUDGE_API_KEY", "VERIFYIT_JUDGE_MODEL"]\n'
        "print(json.dumps({name: os.environ.get(name) for name in names}))\n"
    )
    command.chmod(0o755)
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith(("TASKTROVE_JUDGE_", "VERIFYIT_JUDGE_"))
    }
    environment["PATH"] = f"{directory}:{environment['PATH']}"
    for suffix in SUFFIXES:
        environment[f"TASKTROVE_JUDGE_{suffix}"] = f"old-{suffix}"
        if configured is not None:
            environment[f"VERIFYIT_JUDGE_{suffix}"] = configured
    result = subprocess.run(["bash", str(WRAPPER)], env=environment, capture_output=True, text=True, check=True)
    assert json.loads(result.stdout) == {
        f"VERIFYIT_JUDGE_{suffix}": f"old-{suffix}" if configured is None else configured for suffix in SUFFIXES
    }


def test_task_trove_wrapper_runs_real_cli_and_persists_verdict(tmp_path):
    workspace = tmp_path / "app"
    workspace.mkdir()
    (workspace / "answer.txt").write_text("42")
    spec = tmp_path / "verifier.toml"
    spec.write_text('mode="exact"\nexpected="42"\n')
    logs = tmp_path / "logs"
    subprocess.run(
        ["bash", str(WRAPPER), str(spec), "--workspace", str(workspace), "--logs-dir", str(logs)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads((logs / "verdict.json").read_text())["status"] == "scored"
    assert json.loads((logs / "reward.json").read_text()) == {"reward": 1.0}


@pytest.mark.parametrize("absolute", [False, True])
def test_existing_script_migration_uses_dynamic_workspace_and_transient_logs(tmp_path, absolute):
    task = tmp_path / "task"
    tests = task / "tests"
    tests.mkdir(parents=True)
    workspace = task / "app"
    workspace.mkdir()
    (workspace / "candidate.txt").write_text("correct")
    (tests / "expected.txt").write_text("correct")
    (tests / "verifier.toml").write_text('mode="script"\npath="check.py"\n')
    (tests / "check.py").write_text(
        "import os, json\nfrom pathlib import Path\n"
        "tests=Path(os.environ['TASKTROVE_TESTS_DIR'])\n"
        "workspace=Path(os.environ['TASKTROVE_WORKSPACE'])\n"
        "logs=Path(os.environ['TASKTROVE_LOGS_DIR'])\n"
        "assert logs.name.startswith('verifyit-script-')\n"
        "reward=float((workspace/'candidate.txt').read_text()==(tests/'expected.txt').read_text())\n"
        "(logs/'reward.json').write_text(json.dumps({'reward': reward}))\n"
    )
    if absolute:
        (tests / "verifier.toml").write_text(f'mode="script"\npath={json.dumps(str(tests / "check.py"))}\n')
    migration = WRAPPER.with_name("migrate.py")
    original_script = (tests / "check.py").read_bytes()
    subprocess.run([sys.executable, str(migration), str(task)], check=True)
    migrated_spec = (tests / "verifier.toml").read_bytes()
    subprocess.run([sys.executable, str(migration), str(task)], check=True)
    assert (tests / "verifier.toml").read_bytes() == migrated_spec
    assert (tests / "check.py").read_bytes() == original_script
    logs = task / "logs"
    subprocess.run(
        [
            "bash",
            str(tests / "test.sh"),
            str(tests / "verifier.toml"),
            "--workspace",
            str(workspace),
            "--logs-dir",
            str(logs),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    verdict = json.loads((logs / "verdict.json").read_text())
    assert verdict["status"] == "scored"
    assert verdict["reward"] == 1.0
    assert verdict["detail"]["channel"] == "reward.json"
    assert not (workspace / "reward.json").exists()


def test_migration_preserves_literal_answers_and_task_files_and_is_idempotent(tmp_path):
    task = tmp_path / "task"
    tests = task / "tests"
    tests.mkdir(parents=True)
    workspace = task / "app"
    workspace.mkdir()
    (workspace / "answer.txt").write_text("TASKTROVE_WORKSPACE")
    original = 'mode="exact"\nexpected="TASKTROVE_WORKSPACE"\n'
    (tests / "verifier.toml").write_text(original)
    literals = {"data.toml": b'expected="TASKTROVE_TESTS_DIR"\n', "check.py": b"EXPECTED='TASKTROVE_LOGS_DIR'\n"}
    for name, content in literals.items():
        (tests / name).write_bytes(content)
    migration = WRAPPER.with_name("migrate.py")
    for _ in range(2):
        subprocess.run([sys.executable, str(migration), str(task)], check=True)
    assert (tests / "verifier.toml").read_text() == original
    for name, content in literals.items():
        assert (tests / name).read_bytes() == content
    logs = task / "logs"
    subprocess.run(
        [
            "bash",
            str(tests / "test.sh"),
            str(tests / "verifier.toml"),
            "--workspace",
            str(workspace),
            "--logs-dir",
            str(logs),
        ],
        check=True,
        capture_output=True,
    )
    assert json.loads((logs / "verdict.json").read_text())["reward"] == 1.0


def test_migration_setup_exports_task_owned_legacy_paths(tmp_path):
    task = tmp_path / "task"
    tests = task / "tests"
    tests.mkdir(parents=True)
    workspace = task / "app"
    workspace.mkdir()
    (tests / "ready.txt").write_text("ready")
    (workspace / "test_candidate.py").write_text(
        "from pathlib import Path\ndef test_setup():\n assert Path('ready.txt').read_text() == 'ready'\n"
    )
    (tests / "verifier.toml").write_text(
        'mode="pytest"\nsetup=\'cp "$TASKTROVE_TESTS_DIR/ready.txt" "$TASKTROVE_WORKSPACE/ready.txt"\'\n'
    )
    migration = WRAPPER.with_name("migrate.py")
    subprocess.run([sys.executable, str(migration), str(task)], check=True)
    once = (tests / "verifier.toml").read_bytes()
    subprocess.run([sys.executable, str(migration), str(task)], check=True)
    assert (tests / "verifier.toml").read_bytes() == once
    logs = task / "logs"
    subprocess.run(
        [
            "bash",
            str(tests / "test.sh"),
            str(tests / "verifier.toml"),
            "--workspace",
            str(workspace),
            "--logs-dir",
            str(logs),
        ],
        check=True,
        capture_output=True,
    )
    assert json.loads((logs / "verdict.json").read_text())["reward"] == 1.0

# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

"""Mode pytest: run pytest with ``pytest-json-report`` and grade the node ids in the report.

This is the SWE-bench shape: ``must_pass`` is FAIL_TO_PASS (the bug the agent had to fix) and
``must_not_break`` is PASS_TO_PASS (what it must not regress). Node ids look like
``tests/test_x.py::test_y``. A missing pytest or json-report plugin is a defect in the task image,
not a failed attempt, so it raises instead of scoring zero.
"""

import json
import os
import tempfile
from collections import Counter
from dataclasses import replace
from pathlib import Path

from verifyit.grade import Reward, scored
from verifyit.modes.run import STDERR_TAIL, check_ids, restore, run_command, run_setup, workdir
from verifyit.spec import PytestSpec

REPORT_NAME = "report.json"
PASS_OUTCOMES = frozenset({"passed", "xpassed"})
FAIL_OUTCOMES = frozenset({"failed", "error"})


def grade(spec: PytestSpec, tests_dir: Path, workspace: Path) -> Reward:
    directory = workdir(spec, workspace)
    restore(spec.restore, tests_dir, directory)
    if spec.setup:
        setup = run_setup(spec.setup, tests_dir, directory, spec.timeout)
        if setup.timed_out or setup.returncode != 0:
            if spec.setup_failure_is_infra:
                reason = "timed out" if setup.timed_out else f"exited {setup.returncode}"
                raise RuntimeError(f"pytest setup {reason}: {_tail(setup.stderr or setup.stdout, STDERR_TAIL)}")
            return scored(0.0, reason="setup_failed", stderr=setup.stderr[-STDERR_TAIL:], passed=0, total=0)
    with tempfile.TemporaryDirectory(prefix="verifyit-pytest-") as scratch:
        report_path = Path(scratch) / REPORT_NAME
        argv = [
            spec.python,
            "-m",
            "pytest",
            "--json-report",
            f"--json-report-file={report_path}",
            "-p",
            "no:cacheprovider",
            "-o",
            "addopts=",
            *spec.args,
            *spec.paths,
        ]
        result = run_command(argv, directory, spec.timeout)
        if result.timed_out:
            return scored(0.0, reason="timeout", passed=0, total=0)
        if result.returncode not in (0, 1, 5):
            raise RuntimeError(
                f"pytest producer failed before a usable json report (exit {result.returncode}): "
                f"{_tail(result.stderr or result.stdout)}"
            )
        if not report_path.is_file():
            output = _tail(result.stderr or result.stdout)
            raise RuntimeError(f"pytest wrote no json report (exit {result.returncode}): {output}")
        report = json.loads(report_path.read_text())
    if result.returncode == 5:
        return scored(0.0, reason="no_tests", passed=0, total=0, exit_code=5)
    if any(collector.get("outcome") == "failed" for collector in report.get("collectors", [])):
        raise RuntimeError("pytest report contains collection failures")
    _validate_summary(report)
    outcomes = _outcomes(report, directory)
    if result.returncode == 1 and outcomes and all(outcomes.values()):
        raise RuntimeError("pytest producer failed without reporting a failing test")
    reward = check_ids(outcomes, spec.must_pass, spec.must_not_break, exit_code=result.returncode)
    if reward.reward < 1.0:
        output = _tail(result.stdout + result.stderr, STDERR_TAIL)
        reward = replace(reward, detail={**reward.detail, "output": output})
    return reward


def _outcomes(report: dict, workspace: Path) -> dict[str, bool]:
    """Node id to pass/fail. Skipped and xfailed tests are neither and stay out of the map.

    pytest writes node ids relative to its rootdir, which a ``tests/pytest.ini`` moves below the
    workspace (``unit/test_x.py::test_y`` for ``tests/unit/test_x.py``); the spec's ids are relative
    to the workspace, so the ids are rebased before they are compared.
    """
    root = Path(report.get("root", workspace))
    outcomes = {}
    for test in report.get("tests", []):
        outcome = test.get("outcome")
        if outcome in PASS_OUTCOMES:
            test_id = _rebase(test["nodeid"], root, workspace)
            outcomes[test_id] = outcomes.get(test_id, True)
        elif outcome in FAIL_OUTCOMES:
            outcomes[_rebase(test["nodeid"], root, workspace)] = False
    return outcomes


def _rebase(nodeid: str, root: Path, workspace: Path) -> str:
    file, separator, rest = nodeid.partition("::")
    return os.path.relpath(root / file, workspace) + separator + rest


def _tail(text: str, limit: int = 500) -> str:
    return text.strip()[-limit:]


def _validate_summary(report: dict) -> None:
    tests = report.get("tests", [])
    counts = Counter(test.get("outcome") for test in tests)
    allowed = PASS_OUTCOMES | FAIL_OUTCOMES | {"skipped", "xfailed"}
    if set(counts) - allowed:
        raise RuntimeError("pytest report contains unsupported test outcomes")
    summary = report.get("summary", {})
    if not isinstance(summary, dict):
        raise RuntimeError("pytest report summary must be an object")
    expected = {"total": len(tests), **{name: counts[name] for name in allowed}}
    for field, observed in expected.items():
        if field not in summary:
            continue
        declared = summary[field]
        if isinstance(declared, bool) or not isinstance(declared, int) or declared != observed:
            raise RuntimeError(f"incomplete pytest report: declared {field}={declared}, observed {observed}")

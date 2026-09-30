# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0
"""Record source converter contracts and mode drift against Task Trove's grader pin."""

import argparse
import ast
import hashlib
import json
from pathlib import Path

REVISION = "b76d03131cd88bd9fc711dba206659027edba3a8"
MODE_FILES = {
    "exact": "grade_exact",
    "math": "grade_math",
    "mcq": "grade_mcq",
    "judge": "grade_judge",
    "ifeval": "grade_ifeval",
    "reasoning-gym": "grade_reasoning_gym",
    "json-schema": "grade_json_schema",
    "xml-elements": "grade_xml",
    "csv-columns": "grade_csv",
    "pytest": "grade_pytest",
    "stdio": "grade_stdio",
    "script": "grade_script",
}
COVERAGE = {
    "exact": (
        "candidate API refactor preserves file-grader boxed/whole-answer fallback",
        [
            "test_exact.py::test_exact_single_expected_compares_the_whole_candidate",
            "test_exact.py::test_exact_several_expected_compares_the_candidate_as_a_list",
        ],
    ),
    "math": (
        (
            "malformed final boxes do not expose earlier answers; worker-thread timeout "
            "uses supported zero sentinel; numeric tolerances reject invalid tasks"
        ),
        [
            "test_math_answer.py::test_math_scalar_answers_are_compared_symbolically",
            "test_math_answer.py::test_math_grades_from_a_worker_thread",
            "test_numeric.py::test_numeric_reads_the_final_number",
            "test_numeric.py::test_numeric_invalid_contract_is_an_invalid_task",
        ],
    ),
    "mcq": (
        "option must be complete token; candidate API preserves declared option range",
        [
            "test_mcq.py::test_mcq_option_must_be_a_complete_alphanumeric_token",
            "test_mcq.py::test_mcq_letter_beyond_the_option_count_is_wrong_not_a_task_defect",
        ],
    ),
    "judge": (
        (
            "environment namespace migrated by executable wrapper; malformed/truncated "
            "replies become infra_error and remove stale rewards"
        ),
        [
            "test_judge.py::test_unparseable_reply_is_retried_once_then_masks_candidate",
            "test_judge.py::test_incomplete_judge_score_is_unscored_and_removes_stale_rewards",
            "test_task_trove_integration.py::test_task_trove_wrapper_maps_old_judge_capability_without_overriding_new",
        ],
    ),
    "pytest": (
        "duplicate passing report cannot erase required failure; required test completeness remains",
        [
            "test_pytest_report.py::test_pytest_report_repeated_pass_does_not_erase_required_failure",
            "test_pytest_report.py::test_pytest_id_absent_from_report_counts_as_failed",
        ],
    ),
    "stdio": (
        "nonzero candidate exit rejects even correct stdout; no new output-size limit was added",
        [
            "test_stdio.py::test_stdio_correct_output_before_candidate_crash_scores_zero",
            "test_stdio.py::test_stdio_crashing_special_judge_rejects_instead_of_falling_back",
        ],
    ),
    "script": (
        (
            "nonzero producers cannot score positively; authoritative scalar/structured "
            "files never fall back; named metric selection is explicit"
        ),
        [
            "test_script.py::test_invalid_authoritative_reward_cannot_be_replaced_by_stdout",
            "test_script.py::test_named_reward_survives_spec_roundtrip_and_preserves_metrics",
            "test_script.py::test_named_reward_cannot_be_replaced_by_scalar_channel",
        ],
    ),
    "ifeval": (
        "dispatcher unchanged; helper requires exactly two distinct responses rather than at least two",
        [
            "test_ifeval.py::test_every_constraint_must_hold_for_a_full_reward",
            "test_ifeval.py::test_two_responses_requires_exactly_two_distinct_answers",
        ],
    ),
    "reasoning-gym": ("same native dataset scorer and stored-entry contract after import rename", []),
    "json-schema": (
        "same schema parsing and validation after import rename",
        ["test_json_schema.py::test_document_matching_the_schema_scores_one"],
    ),
    "xml-elements": ("same declared element-count scoring after import rename", []),
    "csv-columns": ("same declared CSV header/count scoring after import rename", []),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inventory(source: Path, repo: Path) -> dict:
    tree = json.loads((source / "tree.json").read_text())
    if tree["sha"] != REVISION:
        raise ValueError("unexpected source grader revision")
    rows = json.loads((repo / "docs/unification/task_trove_inventory.json").read_text())["records"]
    converters = []
    converter_root = Path("experiments/post_training/tasktrove/converters")
    for name in sorted({row["converter"] for row in rows}):
        module = "nemotron_gym" if name in {"nemotron_math", "nemotron_mcqa"} else name
        relative = converter_root / f"{module}.py"
        data = (source / relative).read_bytes()
        syntax = ast.parse(data)
        functions = [
            {"name": node.name, "line": node.lineno} for node in ast.walk(syntax) if isinstance(node, ast.FunctionDef)
        ]
        converters.append(
            {
                "converter": name,
                "source_path": str(relative),
                "source_sha256": digest(data),
                "functions": functions,
                "source_contract": ast.get_docstring(syntax),
                "modes": sorted({row["mode"] for row in rows if row["converter"] == name}),
                "rows": sum(row["count"] for row in rows if row["converter"] == name),
            }
        )
    modes = []
    for mode, module in MODE_FILES.items():
        source_path = Path("lib/tasktrove-verify/src/tasktrove_verify/modes") / f"{module}.py"
        current_path = Path("src/verifyit/modes") / f"{module}.py"
        old = (source / source_path).read_bytes()
        current = (repo / current_path).read_bytes()
        description, tests = COVERAGE[mode]
        for test in tests:
            filename, function = test.split("::")
            if f"def {function}(" not in (repo / "tests" / filename).read_text():
                raise ValueError(f"missing regression evidence {test}")
        modes.append(
            {
                "mode": mode,
                "source_path": str(source_path),
                "source_sha256": digest(old),
                "current_path": str(current_path),
                "current_sha256": digest(current),
                "identical_after_import_rename": old.decode().replace("tasktrove_verify", "verifyit")
                == current.decode(),
                "contract_or_change": description,
                "regression_tests": tests,
            }
        )
    helpers = []
    helper_contracts = {
        "modes/extract.py": ("shared extraction unchanged after import rename", []),
        "modes/ifeval.py": (
            "two_responses rejects empty interior sections, excess responses and duplicates",
            ["test_ifeval.py::test_two_responses_requires_exactly_two_distinct_answers"],
        ),
        "modes/run.py": (
            (
                "setup exports VERIFYIT_TESTS_DIR/WORKSPACE; task-owned migration exports "
                "old setup tokens; timeout cleanup retained"
            ),
            [
                "test_pytest_report.py::test_setup_runs_in_the_workspace_before_the_tests",
                (
                    "test_task_trove_integration.py::test_existing_script_migration_uses_dynamic"
                    "_workspace_and_transient_logs"
                ),
            ],
        ),
        "spec.py": (
            (
                "ScriptSpec reward_key appended without shifting previous positional "
                "fields; environment documentation renamed"
            ),
            ["test_script.py::test_named_reward_survives_spec_roundtrip_and_preserves_metrics"],
        ),
        "grade.py": (
            (
                "finite/nonnegative numeric tolerances validated; negative probe exceeds "
                "declared tolerance; unscored verdict removes stale scalar files"
            ),
            [
                "test_numeric.py::test_numeric_invalid_contract_is_an_invalid_task",
                "test_numeric.py::test_numeric_negative_candidate_exceeds_the_configured_tolerance",
                "test_cli.py::test_unscored_rerun_removes_prior_harbor_reward_files",
            ],
        ),
        "modes/grade_gotest.py": (
            (
                "no dataset rows; duplicate observations merge by package+test; package/test"
                " completeness guards runner failures"
            ),
            ["test_gotest.py::test_gotest_repeated_test_failure_is_not_erased"],
        ),
        "modes/grade_junit.py": (
            (
                "no dataset rows; duplicate observations merge by classname+name; report out"
                "puts must be fresh and inside workspace"
            ),
            ["test_junit.py::test_junit_duplicate_failure_cannot_be_overwritten_by_later_pass"],
        ),
    }
    for relative, (description, tests) in helper_contracts.items():
        old_path = Path("lib/tasktrove-verify/src/tasktrove_verify") / relative
        current_path = Path("src/verifyit") / relative
        old, current = (source / old_path).read_bytes(), (repo / current_path).read_bytes()
        for test in tests:
            filename, function = test.split("::")
            if f"def {function}(" not in (repo / "tests" / filename).read_text():
                raise ValueError(f"missing regression evidence {test}")
        helpers.append(
            {
                "source_path": str(old_path),
                "source_sha256": digest(old),
                "current_path": str(current_path),
                "current_sha256": digest(current),
                "identical_after_import_rename": old.decode().replace("tasktrove_verify", "verifyit")
                == current.decode(),
                "contract_or_change": description,
                "regression_tests": tests,
            }
        )
    return {
        "helper_closure": helpers,
        "source_revision": REVISION,
        "converters": converters,
        "modes": modes,
        "scope": (
            "all 19 retained converters, 12 retained mode implementations and shared "
            "helpers plus unused Go/JUnit; archive bytes not inspected"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    args.output.write_text(json.dumps(inventory(args.source, repo), indent=2) + "\n")


if __name__ == "__main__":
    main()

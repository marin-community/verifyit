# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0
"""Inventory extracted verifier files from Harbor's two remotely fetched cohorts."""

import argparse
import collections
import hashlib
import json
from pathlib import Path

COMPILEBENCH_REVISION = "66e27468505706643088b79f8efad6260c274dc5"
DEEPSWE_DIGEST = "sha256:5affcd534fd90ac85d202d4c63f8b35ddc942140afdd5d60014a21365440a2f5"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(compilebench: Path, deepswe: Path, archive_evidence: Path) -> dict:
    compile_records = []
    for config in sorted(compilebench.glob("datasets/compilebench/*/task.toml")):
        tests = config.parent / "tests"
        script = tests / "test.sh"
        if "pytest" not in script.read_text():
            raise ValueError(f"unreviewed CompileBench entrypoint {script}")
        compile_records.append(
            {
                "task": config.parent.name,
                "primitive": "pytest",
                "classification": "adapter",
                "contract": "binary all-pass artifact/build/CLI assertions; retain every task-specific pytest assertion",
                "files": [
                    {"path": str(path.relative_to(compilebench)), "sha256": digest(path)}
                    for path in sorted(tests.iterdir())
                    if path.is_file()
                ],
            }
        )
    if len(compile_records) != 15:
        raise ValueError("CompileBench population changed from pinned 15 tasks")
    evidence = {row["task"]: row for row in json.loads(archive_evidence.read_text())}
    deep_records = []
    for config in sorted(deepswe.glob("*/tests/config.json")):
        task_name = config.parent.parent.name
        data = json.loads(config.read_text())
        grade = data["grade"]
        format_name = grade["format"]
        if format_name not in {"junit", "ctrf"} or not data["f2p_node_ids"]:
            raise ValueError(f"unreviewed DeepSWE report contract {task_name}")
        task_evidence = evidence[task_name]
        deep_records.append(
            {
                "task": task_name,
                "content_hash": task_evidence["content_hash"],
                "archive_path": task_evidence["archive_path"],
                "archive_sha256": task_evidence["archive_sha256"],
                "downloaded_bytes": task_evidence["downloaded_bytes"],
                "primitive": "junit" if format_name == "junit" else "script",
                "classification": "adapter" if format_name == "junit" else "spec-needed",
                "specification": "harbor_specs.md#structured-report" if format_name == "ctrf" else None,
                "grade": grade,
                "f2p_count": len(data["f2p_node_ids"]),
                "p2p_count": len(data["p2p_node_ids"]),
                "config_sha256": digest(config),
                "grader_sha256": digest(config.parent / "grader.py"),
                "entrypoint_sha256": digest(config.parent / "test.sh"),
                "contract": (
                    "nonempty FAIL_TO_PASS whitelist must all pass and all PASS_TO_PASS must pass; "
                    "missing/skipped IDs fail, duplicate IDs merge worst-status-wins. "
                    "Apply model patch then restore hidden test patch; hidden patch failure is infrastructure error. "
                    "Binary reward plus f2p/p2p/partial and count metrics must be retained."
                ),
            }
        )
    if len(deep_records) != 113 or set(evidence) != {record["task"] for record in deep_records}:
        raise ValueError("DeepSWE population changed from pinned 113 tasks")
    return {
        "compilebench": {
            "repository": "https://github.com/QuesmaOrg/CompileBench",
            "revision": COMPILEBENCH_REVISION,
            "task_count": len(compile_records),
            "records": compile_records,
        },
        "deepswe": {
            "dataset": "datacurve/deep-swe-1-1",
            "digest": DEEPSWE_DIGEST,
            "task_count": len(deep_records),
            "downloaded_bytes": sum(row["downloaded_bytes"] for row in deep_records),
            "report_formats": dict(collections.Counter(row["grade"]["format"] for row in deep_records)),
            "records": deep_records,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compilebench", type=Path, required=True)
    parser.add_argument("--deepswe", type=Path, required=True)
    parser.add_argument("--archive-evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = inventory(args.compilebench, args.deepswe, args.archive_evidence)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()

"""Discover the pinned harness runtime registry without loading datasets or models.

Run in an environment with lm-eval v0.4.12 installed; output is a JSON runtime index.
"""

import argparse
import hashlib
import importlib.metadata
import json
from collections import Counter
from dataclasses import fields
from pathlib import Path

import lm_eval.tasks
from lm_eval.config.group import GroupConfig
from lm_eval.tasks import TaskManager

IMPLEMENTATION_FILES = ("manager.py", "_index.py", "_factory.py", "_yaml_loader.py")


def runtime_index(source):
    installed = Path(lm_eval.tasks.__file__).parent
    implementation = {}
    for name in IMPLEMENTATION_FILES:
        expected = source / "lm_eval/tasks" / name
        actual = installed / name
        if expected.read_bytes() != actual.read_bytes():
            raise ValueError(f"Installed harness source differs from pinned checkout: {name}")
        implementation[name] = hashlib.sha256(actual.read_bytes()).hexdigest()
    manager = TaskManager(include_path=source / "lm_eval/tasks", include_defaults=False)
    registry = manager.task_index
    group_fields = {field.name for field in fields(GroupConfig)}
    inline_tasks = []
    invalid_members = []
    group_overrides = []
    for name, entry in sorted(registry.items()):
        if entry.kind.name != "GROUP":
            continue
        config = entry.cfg
        overrides = {key: value for key, value in config.items() if key not in group_fields}
        group_overrides.append({"group": name, "overrides": overrides, "members": config.get("task", [])})
        pending = [(name, config.get("task", []), overrides)]
        while pending:
            group, members, defaults = pending.pop()
            for member in members:
                if isinstance(member, str):
                    base_name, effective = member, defaults
                elif "group" in member:
                    if member["group"] not in registry:
                        nested = {key: value for key, value in member.items() if key not in group_fields}
                        pending.append((group + "::" + member["group"], member.get("task", []), {**nested, **defaults}))
                    continue
                elif "task" not in member:
                    invalid_members.append(
                        {"group": group, "member": member, "source_path": str(entry.yaml_path.relative_to(source))}
                    )
                    continue
                else:
                    base_name, effective = member["task"], {**defaults, **member}
                if base_name not in registry:
                    inline_tasks.append(
                        {
                            "name": group + "::" + base_name,
                            "source_path": str(entry.yaml_path.relative_to(source)),
                            "config": {**effective, "task": group + "::" + base_name},
                        }
                    )
    records = []
    for name, entry in sorted(manager.task_index.items()):
        records.append(
            {
                "name": name,
                "kind": entry.kind.name,
                "path": str(entry.yaml_path.relative_to(source)) if entry.yaml_path else None,
                "members": sorted(entry.tags) if entry.kind.name == "TAG" else None,
            }
        )
    return {
        "installed_version": importlib.metadata.version("lm-eval"),
        "implementation_hashes": implementation,
        "counts": dict(Counter(record["kind"] for record in records)),
        "entries": records,
        "inline_tasks": inline_tasks,
        "invalid_group_members": invalid_members,
        "group_overrides": group_overrides,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = runtime_index(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    print(payload["counts"])


if __name__ == "__main__":
    main()

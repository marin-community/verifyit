# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0
"""Migrate an extracted task through task-owned execution boundaries."""

import argparse
import shlex
from pathlib import Path

import tomlkit

SUFFIXES = ("TESTS_DIR", "WORKSPACE", "LOGS_DIR")
SCRIPT_WRAPPER = "verifyit-tasktrove-script.sh"


def migrate(task: Path) -> None:
    tests = task / "tests"
    spec_path = tests / "verifier.toml"
    if not spec_path.is_file() or spec_path.is_symlink():
        raise ValueError("expected an extracted task with tests/verifier.toml")
    document = tomlkit.parse(spec_path.read_text())
    setup = document.get("setup")
    if isinstance(setup, str) and setup:
        aliases = "; ".join(f'export TASKTROVE_{suffix}="$VERIFYIT_{suffix}"' for suffix in SUFFIXES[:2])
        if not setup.startswith(aliases):
            document["setup"] = f"{aliases}; {setup}"
    if document.get("mode") == "script" and document.get("path") != SCRIPT_WRAPPER:
        original = document["path"]
        if not isinstance(original, str):
            raise ValueError("script path must be a string")
        original_path = tests / original
        if not original_path.resolve().is_relative_to(tests.resolve()) or not original_path.is_file():
            raise ValueError("script path must name a file within tests")
        relative_script = original_path.resolve().relative_to(tests.resolve()).as_posix()
        target = tests / SCRIPT_WRAPPER
        if target.exists():
            raise ValueError("task already owns the proposed script-wrapper path")
        interpreter = "bash" if original_path.suffix == ".sh" else "python3"
        aliases = "\n".join(f'export TASKTROVE_{suffix}="$VERIFYIT_{suffix}"' for suffix in SUFFIXES)
        target.write_text(
            "#!/bin/bash\nset -euo pipefail\n"
            + aliases
            + "\n"
            + f'exec {interpreter} "$VERIFYIT_TESTS_DIR"/{shlex.quote(relative_script)} "$@"\n'
        )
        target.chmod(0o755)
        document["path"] = SCRIPT_WRAPPER
    spec_path.write_text(tomlkit.dumps(document))
    target = tests / "test.sh"
    if target.is_symlink():
        raise ValueError("refusing symlinked test.sh")
    target.write_bytes(Path(__file__).with_name("test.sh").read_bytes())
    target.chmod(0o755)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", type=Path)
    migrate(parser.parse_args().task)


if __name__ == "__main__":
    main()

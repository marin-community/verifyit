# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

"""Grade one ARC-AGI-2 output grid with verifyit's JSON Schema primitive."""

import argparse
import errno
import json
import os
import stat
from pathlib import Path

from verifyit.grade import InvalidTask, Reward, infra_error, invalid_task, scored, write_reward
from verifyit.modes.grade_json_schema import grade_json_schema_candidate

MAX_GRID_FILE_BYTES = 1_000_000


def _is_grid(value: object) -> bool:
    """ARC cells are JSON integers 0-9; Python bool and integral floats are not cells."""
    return (
        isinstance(value, list)
        and 1 <= len(value) <= 30
        and isinstance(value[0], list)
        and 1 <= len(value[0]) <= 30
        and all(
            isinstance(row, list)
            and len(row) == len(value[0])
            and all(type(cell) is int and 0 <= cell <= 9 for cell in row)
            for row in value
        )
    )


def grade_grids(expected: object, candidate: object) -> Reward:
    """Keep the source's per-test-pair binary equality with strict cell types."""
    if not _is_grid(expected):
        raise InvalidTask("ARC-AGI-2 expected grid must be rectangular, 1-30 cells per side, integers 0-9")
    if not _is_grid(candidate):
        return scored(0.0, reason="invalid_candidate_grid")
    return grade_json_schema_candidate({"const": expected}, candidate)


def _read_grid_json(path: Path) -> object:
    """Read a bounded regular file through a non-symlink parent directory handle."""
    try:
        directory = os.open(
            path.parent,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
        )
    except OSError as error:
        if error.errno in (errno.ELOOP, errno.ENOTDIR):
            raise ValueError("grid parent is not a real directory") from error
        raise
    try:
        try:
            descriptor = os.open(
                path.name,
                os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                dir_fd=directory,
            )
        except OSError as error:
            if error.errno == errno.ELOOP:
                raise ValueError("grid file is a symbolic link") from error
            raise
    finally:
        os.close(directory)
    with os.fdopen(descriptor, "rb") as source:
        info = os.fstat(source.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("grid file is not a regular file")
        if info.st_size > MAX_GRID_FILE_BYTES:
            raise ValueError("grid file is too large")
        data = source.read(MAX_GRID_FILE_BYTES + 1)
    if len(data) > MAX_GRID_FILE_BYTES:
        raise ValueError("grid file is too large")
    return json.loads(data)


def grade_files(expected_path: Path, candidate_path: Path) -> Reward:
    """Treat a bad protected reference separately from a bad candidate file."""
    try:
        expected = _read_grid_json(expected_path)
    except (FileNotFoundError, UnicodeError, ValueError) as error:
        return invalid_task(f"invalid ARC-AGI-2 expected grid: {error}")
    except OSError as error:
        return infra_error(f"cannot read ARC-AGI-2 expected grid: {error}")
    if not _is_grid(expected):
        return invalid_task("ARC-AGI-2 expected grid must be rectangular, 1-30 cells per side, integers 0-9")
    try:
        candidate = _read_grid_json(candidate_path)
    except FileNotFoundError:
        return scored(0.0, reason="missing_output_file")
    except (UnicodeError, ValueError):
        return scored(0.0, reason="invalid_candidate_json")
    except OSError as error:
        return infra_error(f"cannot read ARC-AGI-2 output: {error}")

    try:
        return grade_grids(expected, candidate)
    except InvalidTask as error:
        return invalid_task(str(error))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("expected", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--logs-dir", type=Path, default=Path("/logs/verifier"))
    args = parser.parse_args(argv)
    try:
        reward = grade_files(args.expected, args.candidate)
    except Exception as error:
        reward = infra_error(f"{type(error).__name__}: {error}")
    write_reward(args.logs_dir, reward)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

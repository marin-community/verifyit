# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

"""Install source-pinned Evalchemy overrides into the trusted harness task tree."""

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


def install(source_root: Path, harness_root: Path) -> Path:
    manifest = json.loads(Path(__file__).with_name("uncheatable-source.json").read_text())
    source = source_root.resolve() / "eval/lm_eval_tasks/uncheatable_eval"
    files = {}
    for name, digest in manifest["files"].items():
        data = (source / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError(f"Unreviewed Evalchemy source file: {name}")
        files[name] = data
    template = "_uncheatable_eval_template"
    files[template] += b"  verifyit_corpus_runtime: true\n  verifyit_source_contract: evalchemy-uncheatable-v1\n"
    harness_root = harness_root.resolve()
    tasks = (harness_root / "lm_eval/tasks").resolve()
    if not tasks.is_relative_to(harness_root) or not (harness_root / "lm_eval/verifyit_uncheatable.py").is_file():
        raise ValueError("Install the reviewed harness Uncheatable integration patch first")
    destination = tasks / "evalchemy_uncheatable"
    if destination.is_symlink():
        raise ValueError("Uncheatable installation must not be a symbolic link")
    if destination.exists():
        if all((destination / name).read_bytes() == data for name, data in files.items()):
            return destination
        raise ValueError("Existing Uncheatable installation differs; refusing to overwrite it")
    temporary = Path(tempfile.mkdtemp(prefix=".verifyit-uncheatable-", dir=tasks))
    try:
        for name, data in files.items():
            (temporary / name).write_bytes(data)
        temporary.rename(destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evalchemy-root", type=Path, required=True)
    parser.add_argument("--harness-root", type=Path, required=True)
    args = parser.parse_args()
    print(install(args.evalchemy_root, args.harness_root))


if __name__ == "__main__":
    main()

# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0
"""Create a trusted verifier asset manifest from pinned Git objects."""
import hashlib
import json
import subprocess
from pathlib import Path

REVISION = "fc0055dc4e0a316c3f83133267fbd6faaa770992"


def manifest(repository: Path, domain: str) -> dict:
    if domain not in {"airline", "retail", "telecom", "banking_knowledge"}:
        raise ValueError("unsupported tau3 domain")
    paths = subprocess.check_output(
        [
            "git",
            "-C",
            str(repository),
            "ls-tree",
            "-r",
            "--name-only",
            REVISION,
            "src/tau2",
            f"data/tau2/domains/{domain}",
        ],
        text=True,
    ).splitlines()
    files = {}
    for path in paths:
        if path.startswith("src/") and not path.endswith(".py"):
            continue
        content = subprocess.check_output(["git", "-C", str(repository), "show", f"{REVISION}:{path}"])
        files[path] = hashlib.sha256(content).hexdigest()
    return {"revision": REVISION, "domain": domain, "files": files}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("repository", type=Path)
    parser.add_argument("domain")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_text(json.dumps(manifest(args.repository, args.domain), sort_keys=True) + "\n")

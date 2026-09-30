# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

"""Run clean client boundaries against pinned, unmodified SkyRL scorer files."""

import argparse
import hashlib
import importlib.util
import sys
from pathlib import Path

from verifyit.adapters.skyrl import (
    grade_grid_candidate,
    grade_gsm8k_strict,
    grade_literal_candidate,
    grade_rounded_candidate,
    grade_search_em,
)


def load_source(root: Path, name: str, relative: str, digest: str):
    path = root / relative
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError(f"source pin mismatch: {relative}")
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise ValueError(f"cannot load scorer: {relative}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    root = parser.parse_args().source
    sys.path.insert(0, str(root / "skyrl-gym"))
    gsm = load_source(
        root,
        "source_gsm8k",
        "skyrl-gym/skyrl_gym/envs/gsm8k/utils.py",
        "01ae9bc8110da5b5d360e5d6501432b3d12eb6c67e4cdc534b6dcf706bb604d1",
    )
    search = load_source(
        root,
        "source_search",
        "skyrl-gym/skyrl_gym/envs/search/utils.py",
        "989d04655cd9441ee004c1f9c612d7ced21a96b71b88aecf7c7333978960da01",
    )
    chemistry = load_source(
        root,
        "source_chemistry",
        "skyrl-gym/skyrl_gym/envs/nemotron_ultra/rdkit_chemistry.py",
        "8c41da86140963eae6eaa46ef12e3fcabbd5b14e79978a81096c1d4a0c98dc36",
    )
    arc = load_source(
        root,
        "source_arc",
        "skyrl-gym/skyrl_gym/envs/nemotron_ultra/nvarc.py",
        "387448d4dbfa00f31730b96b4da8b796f8e0c9c9514e128ff222797059247659",
    )
    aime = load_source(
        root,
        "source_aime",
        "skyrl-gym/skyrl_gym/envs/aime/utils.py",
        "44a9c35eaf3cf2d2b973599c89f8c984b396981daeed18b67637cbe9cdb896ee",
    )
    count = 0
    for expected, response in [
        ("42", "#### 42\n#### 41"),
        ("42", "#### 41\n#### 42"),
        ("42", "no marker 42"),
        ("1234", "#### 12,34"),
        ("42", "#### 42.0"),
        ("42", "#### ."),
        ("42", "#### 42 prose"),
        ("42", "####42"),
    ]:
        for format_score in [0.0, 0.2 / 5]:
            actual = grade_gsm8k_strict(expected, response, format_score=format_score).reward
            original = gsm.compute_score(response, expected, method="strict", format_score=format_score)
            assert actual == original, (expected, response, actual, original)
            count += 1
    for targets, response in [
        (["New York", "NYC"], "<answer>The NYC!</answer>"),
        ("cat", "<answer>cat</answer><answer>dog</answer>"),
        ("cat", "<answer>dog</answer><answer>A cat.</answer>"),
        ("cat", "cat"),
        ("cat", "<answer>the catfish</answer>"),
        ("", "<answer>The!!!</answer>"),
        ("é", "<answer>É</answer>"),
        ("ss", "<answer>ß</answer>"),
        ([], "<answer>cat</answer>"),
    ]:
        actual = grade_search_em(targets, response).reward
        original = search.compute_score(response, {"target": targets})
        assert actual == original, (targets, response, actual, original)
        count += 1
    for text, expected in [
        ("((1.5))", 2.5),
        ("((2.5))", 3.5),
        (r"\boxed{4.0}", 3.5),
        ("((answer: 2))", 2.0),
        ("2", 2.0),
    ]:
        original, detail = chemistry.grade_rdkit_chemistry(
            text, {"property_type": "count", "expected_answer": expected, "use_box_format": "boxed" in text}
        )
        actual = grade_rounded_candidate(expected, detail["predicted_value"]).reward
        assert actual == original, (text, actual, original)
        count += 1
    for text in ["12\n34", "[[1,2],[3,4]]", "[[true,2],[3,4]]", "[[1.0,2],[3,4]]", "[[3,4],[1,2]]", "[[1,2],[3]]"]:
        expected = [[1, 2], [3, 4]]
        original, detail = arc.grade_transductive_arc(text, {"expected_output": expected})
        actual = grade_grid_candidate(expected, detail["predicted_output"]).reward
        assert actual == original, (text, actual, original)
        count += 1
    for text in [r"\boxed{42}", r"\boxed{ 42}", r"\boxed{42 }", "42", r"\boxed{42}" + "x" * 101]:
        original, extracted = aime.is_correct_strict_box(text, "42")
        actual = grade_literal_candidate("42", extracted).reward if extracted is not None else 0.0
        assert actual == (original + 1) / 2, (text, actual, original)
        count += 1
    print(f"{count} source-pinned client parity cases passed")


if __name__ == "__main__":
    main()

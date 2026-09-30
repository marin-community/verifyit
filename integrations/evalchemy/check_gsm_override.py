import argparse
import importlib.util
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("source_root", type=Path)
parser.add_argument("patched_root", type=Path)
args = parser.parse_args()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load source module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


native = load("patched_gsm", args.patched_root / "eval/lm_eval_tasks/gsm8k/utils.py")
source = load("source_gsm", args.source_root / "eval/lm_eval_tasks/gsm8k/utils.py")
cases = [
    ("28.00", "28", 1),
    ("0.5", r"\frac{1}{2}", 1),
    ("2", r"\frac{4}{2}", 1),
    ("0.50", "0.5", 1),
    ("28.01", "28", 0),
    ("[invalid]", "28", 0),
    ("x+1", "x+2", 0),
    ("x+x", "2*x", 1),
]
results = []
for candidate, target, expected in cases:
    doc = {"answer": "Solution #### " + target}
    before = source.process_results(doc, [candidate])
    after = native.process_results(doc, [candidate])
    assert before == after == {"exact_match": float(expected)}, (candidate, target, before, after)
    results.append({"candidate": candidate, "target": target, "source": before, "native": after})


# Exceptions in the retained symbolic scorer propagate; no success/default projection.
def broken(*args):
    raise RuntimeError("scorer infrastructure failure")


native.is_equiv = broken
try:
    native.process_results({"answer": "#### x"}, ["y"])
except RuntimeError:
    pass
else:
    raise AssertionError("scorer error swallowed")
print(json.dumps({"cases": results, "infra_propagation": "passed"}))

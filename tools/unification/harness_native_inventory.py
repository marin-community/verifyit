"""Count resolved configurations eligible for implemented native scorer routes."""

import argparse
import json
from collections import Counter
from pathlib import Path

from eval_inventory import resolve_config, revision

from verifyit.adapters.harness_native import native_config_route


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    inventory = json.loads(args.inventory.read_text())
    records = []
    for record in inventory["configs"]:
        if record["kind"] != "task":
            continue
        config, _ = resolve_config(args.source / record["path"])
        records.append({"path": record["path"], "task": record["task"], "native_route": native_config_route(config)})
    payload = {
        "revision": revision(args.source),
        "population": len(records),
        "eligibility_counts": dict(Counter(record["native_route"] or "not_native" for record in records)),
        "boundary": (
            "Resolved configuration eligibility; sample validity and runtime scorer identity "
            "checked by adapter. Not full dataset execution."
        ),
        "records": records,
    }
    records = payload.pop("records")
    header = json.dumps(payload, separators=(",", ":"))[:-1]
    lines = [json.dumps(record, separators=(",", ":")) for record in records]
    args.output.write_text(header + ',\n"records":[\n' + ",\n".join(lines) + "\n]}\n")
    print(json.dumps(payload["eligibility_counts"]))


if __name__ == "__main__":
    main()

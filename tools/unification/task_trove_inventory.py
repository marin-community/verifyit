# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0
"""Inventory all Task Trove metadata using byte ranges, without task archives.

Run with ``uv run --with pyarrow python tools/unification/task_trove_inventory.py
--output docs/unification/task_trove_inventory.json``. Downloads about 1 MB and
creates a temporary sparse parquet file. The source revision is immutable.
"""

import argparse
import collections
import concurrent.futures
import json
import struct
import tempfile
import urllib.request
from pathlib import Path

import pyarrow.parquet as parquet

REVISION = "9065fa568394f286dab0081e43dc76fc87c48984"
BASE = f"https://huggingface.co/datasets/open-athena/task-trove/resolve/{REVISION}"
SIZE = 2607364326
COLUMNS = ("source", "family", "template_id", "converter", "mode")
MODES = {
    "exact",
    "math",
    "mcq",
    "judge",
    "ifeval",
    "reasoning-gym",
    "json-schema",
    "xml-elements",
    "csv-columns",
    "pytest",
    "stdio",
    "script",
}


def byte_range(start: int, length: int) -> bytes:
    request = urllib.request.Request(
        f"{BASE}/data/part-00000.parquet?range={start}",
        headers={"Range": f"bytes={start}-{start + length - 1}"},
    )
    with urllib.request.urlopen(request) as response:
        if response.status != 206:
            raise RuntimeError("server did not honor byte range; refusing full download")
        data = response.read(length + 1)
    if len(data) != length:
        raise RuntimeError("unexpected range response length")
    return data


def inventory() -> dict:
    with urllib.request.urlopen(f"{BASE}/manifest.json") as response:
        manifest = json.load(response)
    footer = byte_range(SIZE - 8, 8)
    footer_length = struct.unpack("<I", footer[:4])[0]
    footer_start = SIZE - footer_length - 8
    footer_data = byte_range(footer_start, footer_length + 8)
    with tempfile.TemporaryDirectory(prefix="task-trove-metadata-") as temporary:
        path = Path(temporary) / "metadata.parquet"
        with path.open("wb") as output:
            output.write(b"PAR1")
            output.seek(footer_start)
            output.write(footer_data)
        metadata = parquet.read_metadata(path)
        ranges = []
        for group in range(metadata.num_row_groups):
            for column in range(metadata.num_columns):
                chunk = metadata.row_group(group).column(column)
                if chunk.path_in_schema in COLUMNS:
                    start = chunk.dictionary_page_offset or chunk.data_page_offset
                    ranges.append((start, chunk.total_compressed_size))
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            futures = [(start, pool.submit(byte_range, start, length)) for start, length in ranges]
            with path.open("r+b") as output:
                for start, future in futures:
                    output.seek(start)
                    output.write(future.result())
        table = parquet.read_table(path, columns=list(COLUMNS))
    counts = collections.Counter(zip(*(table[column].to_pylist() for column in COLUMNS), strict=True))
    mode_totals = collections.Counter()
    source_totals = collections.Counter()
    records = []
    for values, count in sorted(counts.items()):
        record = dict(zip(COLUMNS, values, strict=True))
        record.update(count=count, verifyit_mode=record["mode"], classification="direct")
        records.append(record)
        mode_totals[record["mode"]] += count
        source_totals[record["source"]] += count
    if set(mode_totals) - MODES:
        raise RuntimeError(f"unmapped modes: {set(mode_totals) - MODES}")
    if dict(mode_totals) != manifest["by_mode"]:
        raise RuntimeError("row metadata does not reconcile with release mode counts")
    expected_sources = {
        source: statuses["converted"] for source, statuses in manifest["by_source"].items() if "converted" in statuses
    }
    if dict(source_totals) != expected_sources or table.num_rows != manifest["clean_tasks"]:
        raise RuntimeError("row metadata does not reconcile with release source counts")
    return {
        "dataset": "open-athena/task-trove",
        "revision": REVISION,
        "grader_revision": manifest["verify_tool_ref"],
        "rows": table.num_rows,
        "sources": len(source_totals),
        "converters": len(set(table["converter"].to_pylist())),
        "templates": len(set(table["template_id"].to_pylist())),
        "downloaded_bytes": sum(length for _, length in ranges) + len(footer_data) + 8,
        "verification_scope": "all metadata rows; embedded verifier.toml task binaries not downloaded",
        "mode_totals": dict(mode_totals),
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = inventory()
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()

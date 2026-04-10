#!/usr/bin/env python3
"""
Vocabulary & Template Validation Pipeline — Reconciliation

Compares the validated JSON vocabularies with the analyzer's hardcoded
Python sets. Reports what's in JSON but not Python, in Python but not JSON,
and which differences matter.

Reads reference_data/ and legacy/analyze_compositionality.py.
Never writes to production files.
Outputs: analysis_outputs/reconciliation_report.json + human summary to stdout.

Usage: python3 scripts/reconcile.py
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
VOCAB_FILE = BASE_DIR / "reference_data" / "slot_vocabularies.json"
ANALYZER_FILE = BASE_DIR / "legacy" / "analyze_compositionality.py"
REPORT_FILE = BASE_DIR / "analysis_outputs" / "reconciliation_report.json"


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------
def load_vocabs():
    with open(VOCAB_FILE, encoding="utf-8") as f:
        data = json.load(f)
    vocabs = {}
    for _cat, slots in data["categories"].items():
        for name, tokens in slots.items():
            vocabs[name] = set(tokens)
    return data, vocabs


def parse_python_sets(filepath):
    """Extract token sets from Python source by regex.

    Handles both multi-line set definitions:
        NAME_TOKENS = {
            "token1", "token2",
            ...
        }
    And single-line:
        NAME_TOKENS = {"token1", "token2"}
    And empty:
        NAME_TOKENS = set()
    """
    source = filepath.read_text(encoding="utf-8")
    sets = {}

    # Pattern: UPPERCASE_TOKENS = { ... } (multi-line or single-line)
    # We find the start, then collect everything until the closing }
    pattern = re.compile(
        r'^([A-Z][A-Z0-9_]*_TOKENS)\s*=\s*\{',
        re.MULTILINE,
    )
    empty_pattern = re.compile(
        r'^([A-Z][A-Z0-9_]*_TOKENS)\s*=\s*set\(\)',
        re.MULTILINE,
    )

    # Handle set() definitions
    for match in empty_pattern.finditer(source):
        name = match.group(1)
        sets[name] = set()

    # Handle { ... } definitions
    for match in pattern.finditer(source):
        name = match.group(1)
        start = match.end()
        # Find matching closing brace
        depth = 1
        pos = start
        while pos < len(source) and depth > 0:
            if source[pos] == '{':
                depth += 1
            elif source[pos] == '}':
                depth -= 1
            pos += 1
        body = source[start:pos - 1]
        # Extract quoted strings
        tokens = set(re.findall(r'"([^"]*)"', body))
        sets[name] = tokens

    return sets


# ---------------------------------------------------------------------------
# Reconciliation
# ---------------------------------------------------------------------------
def reconcile(json_vocabs, python_sets):
    """Compare JSON vocabs with Python sets."""
    all_names = sorted(set(json_vocabs.keys()) | set(python_sets.keys()))

    results = {}
    for name in all_names:
        json_set = json_vocabs.get(name, set())
        py_set = python_sets.get(name, set())

        only_json = sorted(json_set - py_set)
        only_python = sorted(py_set - json_set)
        common = sorted(json_set & py_set)

        in_json = name in json_vocabs
        in_python = name in python_sets

        if in_json and in_python and not only_json and not only_python:
            status = "identical"
        elif in_json and in_python:
            status = "diverged"
        elif in_json and not in_python:
            status = "json_only"
        elif not in_json and in_python:
            status = "python_only"
        else:
            status = "unknown"

        results[name] = {
            "status": status,
            "in_json": in_json,
            "in_python": in_python,
            "json_count": len(json_set),
            "python_count": len(py_set),
            "common_count": len(common),
            "only_in_json": only_json,
            "only_in_python": only_python,
            "only_json_count": len(only_json),
            "only_python_count": len(only_python),
        }

    return results


# ---------------------------------------------------------------------------
# Human summary
# ---------------------------------------------------------------------------
def print_summary(report):
    print(f"\n{'='*70}")
    print(f"  RECONCILIATION REPORT")
    print(f"  JSON version: {report['json_version']}")
    print(f"{'='*70}\n")

    summary = report["summary"]
    print(f"  Vocabularies:")
    print(f"    Identical:    {summary['identical']:>3}")
    print(f"    Diverged:     {summary['diverged']:>3}")
    print(f"    JSON-only:    {summary['json_only']:>3}")
    print(f"    Python-only:  {summary['python_only']:>3}")
    print(f"    Total:        {summary['total']:>3}")

    print(f"\n  Token counts:")
    print(f"    Tokens only in JSON:    {summary['total_only_json']:>4}")
    print(f"    Tokens only in Python:  {summary['total_only_python']:>4}")
    print(f"    Common tokens:          {summary['total_common']:>4}")

    # Show diverged vocabs
    diverged = {n: d for n, d in report["vocabularies"].items() if d["status"] == "diverged"}
    if diverged:
        print(f"\n  Diverged vocabularies ({len(diverged)}):")
        for name, data in sorted(diverged.items()):
            print(f"\n    {name} (JSON={data['json_count']}, Python={data['python_count']}, common={data['common_count']}):")
            if data["only_in_json"]:
                # Show first 10
                shown = data["only_in_json"][:10]
                suffix = f" ... +{len(data['only_in_json']) - 10} more" if len(data["only_in_json"]) > 10 else ""
                print(f"      Only in JSON ({data['only_json_count']}): {', '.join(shown)}{suffix}")
            if data["only_in_python"]:
                shown = data["only_in_python"][:10]
                suffix = f" ... +{len(data['only_in_python']) - 10} more" if len(data["only_in_python"]) > 10 else ""
                print(f"      Only in Python ({data['only_python_count']}): {', '.join(shown)}{suffix}")

    # Show JSON-only vocabs
    json_only = {n: d for n, d in report["vocabularies"].items() if d["status"] == "json_only"}
    if json_only:
        print(f"\n  JSON-only vocabularies ({len(json_only)}):")
        for name, data in sorted(json_only.items()):
            print(f"    {name:<40s} {data['json_count']:>3} tokens")

    # Show Python-only vocabs
    py_only = {n: d for n, d in report["vocabularies"].items() if d["status"] == "python_only"}
    if py_only:
        print(f"\n  Python-only vocabularies ({len(py_only)}):")
        for name, data in sorted(py_only.items()):
            print(f"    {name:<40s} {data['python_count']:>3} tokens")

    print(f"\n  Report: {REPORT_FILE.relative_to(BASE_DIR)}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if not ANALYZER_FILE.exists():
        print(f"ERROR: Analyzer not found at {ANALYZER_FILE}")
        print("Copy analyze_compositionality.py to legacy/ first.")
        return 1

    print("Loading JSON vocabularies...", end=" ", flush=True)
    vocab_raw, json_vocabs = load_vocabs()
    print(f"{len(json_vocabs)} vocabularies")

    print("Parsing Python sets...", end=" ", flush=True)
    python_sets = parse_python_sets(ANALYZER_FILE)
    print(f"{len(python_sets)} sets found")

    print("Reconciling...")
    vocab_results = reconcile(json_vocabs, python_sets)

    # Summary counts
    status_counts = {"identical": 0, "diverged": 0, "json_only": 0, "python_only": 0}
    total_only_json = 0
    total_only_python = 0
    total_common = 0
    for data in vocab_results.values():
        status_counts[data["status"]] = status_counts.get(data["status"], 0) + 1
        total_only_json += data["only_json_count"]
        total_only_python += data["only_python_count"]
        total_common += data["common_count"]

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "json_version": vocab_raw["metadata"].get("version", "unknown"),
        "json_source": str(VOCAB_FILE),
        "python_source": str(ANALYZER_FILE),
        "summary": {
            **status_counts,
            "total": len(vocab_results),
            "total_only_json": total_only_json,
            "total_only_python": total_only_python,
            "total_common": total_common,
        },
        "vocabularies": vocab_results,
    }

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")

    print_summary(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Vocabulary & Template Validation Pipeline — Step 2: Suggest

Reads the validation report from validate.py and proposes a changeset
of concrete, reviewable modifications to vocabularies and templates.

Reads reference_data/ and analysis_outputs/validation_report.json.
Never writes to production files.
Outputs: analysis_outputs/changeset.json + human summary to stdout.

Usage: python3 scripts/suggest.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
VOCAB_FILE = BASE_DIR / "reference_data" / "slot_vocabularies.json"
TEMPLATES_FILE = BASE_DIR / "reference_data" / "family_templates.json"
REPORT_FILE = BASE_DIR / "analysis_outputs" / "validation_report.json"
CHANGESET_FILE = BASE_DIR / "analysis_outputs" / "changeset.json"

# Categories of zero-hit tokens that are intentional and should NOT be removed
KEEP_CATEGORIES = {"british_spelling", "prefix"}


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------
def load_report():
    with open(REPORT_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_vocabs():
    with open(VOCAB_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_templates():
    with open(TEMPLATES_FILE, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Suggestion generators
# ---------------------------------------------------------------------------
def suggest_zero_hit_removals(report):
    """Suggest removing problematic zero-hit tokens (not british/prefix)."""
    changes = []
    for vocab_name, tokens in report["token_health"]["zero_hit_by_vocab"].items():
        for entry in tokens:
            if entry["category"] in KEEP_CATEGORIES:
                continue
            changes.append({
                "type": "remove_token",
                "vocabulary": vocab_name,
                "token": entry["token"],
                "reason": f"Zero-hit token: not found in any ICD-10-CM term",
                "category": "zero_hit",
                "severity": "low",
            })
    return changes


def suggest_cross_slot_fixes(report):
    """Flag cross-slot overlaps as advisories — resolution requires human judgment."""
    advisories = []
    for token, owners in report["token_health"]["cross_slot_overlap"].items():
        advisories.append({
            "type": "advisory",
            "subtype": "cross_slot_overlap",
            "token": token,
            "vocabularies": owners,
            "reason": f"Token '{token}' appears in {len(owners)} vocabularies: {', '.join(owners)}. "
                      f"May cause ambiguous slot assignment in templates using multiple of these vocabs.",
            "category": "cross_slot",
            "severity": "medium",
        })
    return advisories


def suggest_orphaned_vocab_actions(report):
    """Suggest actions for orphaned vocabularies (defined but no template uses them)."""
    changes = []
    orphaned = report["template_health"]["orphaned_vocabs"]
    sizes = report["template_health"]["orphaned_vocab_sizes"]

    for vocab_name in orphaned:
        size = sizes.get(vocab_name, 0)
        changes.append({
            "type": "advisory",
            "subtype": "orphaned_vocab",
            "vocabulary": vocab_name,
            "token_count": size,
            "reason": f"Vocabulary '{vocab_name}' ({size} tokens) is not referenced by any template family. "
                      f"Either create templates that use it or remove it to reduce dead weight.",
            "category": "orphaned",
            "severity": "medium",
        })
    return changes


def suggest_order_variant_consolidation(report):
    """Suggest consolidating order-variant template groups."""
    changes = []
    for combo_key, family_names in report["template_health"]["order_variant_groups"].items():
        # Keep the first (alphabetically) as canonical, suggest removing others
        canonical = sorted(family_names)[0]
        duplicates = [f for f in sorted(family_names) if f != canonical]
        for dup in duplicates:
            changes.append({
                "type": "remove_template",
                "template": dup,
                "reason": f"Order variant of '{canonical}' — same vocabulary slots in different order. "
                          f"Group: {', '.join(sorted(family_names))}",
                "category": "order_variant",
                "severity": "low",
            })
    return changes


def suggest_ground_truth_flags(report):
    """Flag templates with 0% ground-truth hit rate."""
    advisories = []
    gt = report.get("ground_truth", {})
    for template_name, data in gt.items():
        if data["hit_rate"] == 0.0 and data["sampled"] >= 100:
            advisories.append({
                "type": "advisory",
                "subtype": "zero_hit_rate_template",
                "template": template_name,
                "cross_product_size": data["cross_product_size"],
                "sampled": data["sampled"],
                "reason": f"Template '{template_name}' has 0% hit rate across {data['sampled']} "
                          f"sampled combinations (cross-product: {data['cross_product_size']:,}). "
                          f"May be too specific or token combinations don't co-occur in ICD-10-CM.",
                "category": "ground_truth",
                "severity": "info",
            })
    return advisories


def suggest_metadata_fixes(report):
    """Suggest metadata corrections if mismatched."""
    changes = []
    meta = report["structural"]["metadata"]
    for key, info in meta.items():
        if not info["ok"]:
            changes.append({
                "type": "fix_metadata",
                "field": key,
                "declared": info["declared"],
                "actual": info["actual"],
                "reason": f"Metadata '{key}' declares {info['declared']} but actual count is {info['actual']}",
                "category": "metadata",
                "severity": "high",
            })
    return changes


def suggest_duplicate_removals(report):
    """Suggest removing intra-vocabulary duplicate tokens."""
    changes = []
    for vocab_name, dupes in report["structural"]["intra_vocab_duplicates"].items():
        for token, count in dupes.items():
            changes.append({
                "type": "remove_duplicate",
                "vocabulary": vocab_name,
                "token": token,
                "duplicate_count": count,
                "reason": f"Token '{token}' appears {count} times in {vocab_name}",
                "category": "duplicate",
                "severity": "high",
            })
    return changes


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if not REPORT_FILE.exists():
        print(f"ERROR: Validation report not found at {REPORT_FILE}")
        print("Run scripts/validate.py first.")
        return 1

    report = load_report()
    print(f"Reading validation report: {report['status']} (vocab {report['vocab_version']})")

    # Collect all suggestions
    changes = []
    changes.extend(suggest_duplicate_removals(report))
    changes.extend(suggest_metadata_fixes(report))
    changes.extend(suggest_zero_hit_removals(report))
    changes.extend(suggest_order_variant_consolidation(report))
    changes.extend(suggest_orphaned_vocab_actions(report))
    changes.extend(suggest_cross_slot_fixes(report))
    changes.extend(suggest_ground_truth_flags(report))

    # Build changeset
    changeset = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "based_on_validation": report["timestamp"],
        "based_on_vocab_version": report["vocab_version"],
        "summary": {
            "total_suggestions": len(changes),
            "by_type": {},
            "by_severity": {},
            "by_category": {},
        },
        "changes": changes,
    }

    # Compute summary counts
    for change in changes:
        t = change["type"]
        changeset["summary"]["by_type"][t] = changeset["summary"]["by_type"].get(t, 0) + 1
        s = change.get("severity", "unknown")
        changeset["summary"]["by_severity"][s] = changeset["summary"]["by_severity"].get(s, 0) + 1
        c = change.get("category", "unknown")
        changeset["summary"]["by_category"][c] = changeset["summary"]["by_category"].get(c, 0) + 1

    CHANGESET_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHANGESET_FILE, "w", encoding="utf-8") as f:
        json.dump(changeset, f, indent=2)
        f.write("\n")

    # Human summary
    print(f"\n{'='*70}")
    print(f"  CHANGESET SUMMARY")
    print(f"  Based on validation: {report['vocab_version']} ({report['status']})")
    print(f"{'='*70}\n")

    print(f"  Total suggestions: {len(changes)}\n")

    print(f"  By type:")
    for t, count in sorted(changeset["summary"]["by_type"].items()):
        print(f"    {t:<25s} {count:>3}")

    print(f"\n  By severity:")
    for s, count in sorted(changeset["summary"]["by_severity"].items()):
        print(f"    {s:<25s} {count:>3}")

    print(f"\n  By category:")
    for c, count in sorted(changeset["summary"]["by_category"].items()):
        print(f"    {c:<25s} {count:>3}")

    # Show actionable changes (non-advisory)
    actionable = [c for c in changes if c["type"] != "advisory"]
    if actionable:
        print(f"\n  Actionable changes ({len(actionable)}):")
        for c in actionable:
            if c["type"] == "remove_token":
                print(f"    REMOVE {c['vocabulary']}.{c['token']}")
            elif c["type"] == "remove_template":
                print(f"    REMOVE template '{c['template']}'")
            elif c["type"] == "fix_metadata":
                print(f"    FIX metadata '{c['field']}': {c['declared']} -> {c['actual']}")
            elif c["type"] == "remove_duplicate":
                print(f"    DEDUP {c['vocabulary']}.{c['token']} (x{c['duplicate_count']})")
            else:
                print(f"    {c['type'].upper()}: {c.get('reason', '')[:60]}")

    # Show advisories summary
    advisories = [c for c in changes if c["type"] == "advisory"]
    if advisories:
        print(f"\n  Advisories ({len(advisories)}) — require human judgment:")
        by_subtype = {}
        for a in advisories:
            st = a.get("subtype", "other")
            by_subtype.setdefault(st, []).append(a)
        for st, items in sorted(by_subtype.items()):
            print(f"    {st}: {len(items)}")

    print(f"\n  Changeset: {CHANGESET_FILE.relative_to(BASE_DIR)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

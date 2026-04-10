#!/usr/bin/env python3
"""
Vocabulary & Template Validation Pipeline — Step 1: Validate

Checks structural integrity, token health, template health, and
ground-truth co-occurrence against ICD-10-CM terms.

Reads reference_data/ and ICD-10-CM source. Never writes to production files.
Outputs: analysis_outputs/validation_report.json + human summary to stdout.

Usage: python3 scripts/validate.py
"""

import csv
import json
import os
import random
import sys
from collections import defaultdict
from datetime import datetime, timezone
from itertools import product as cartesian_product
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
VOCAB_FILE = BASE_DIR / "reference_data" / "slot_vocabularies.json"
TEMPLATES_FILE = BASE_DIR / "reference_data" / "family_templates.json"
ICD_CSV = Path(os.environ.get(
    "ICD10CM_CSV",
    "/home/bguide/compositional_analysis/icd10cm_terms_2026.csv",
))
LEGACY_CSV = BASE_DIR / "legacy" / "template_families.csv"
REPORT_FILE = BASE_DIR / "analysis_outputs" / "validation_report.json"

GROUND_TRUTH_SAMPLE_SIZE = 500
GROUND_TRUTH_EXHAUSTIVE_LIMIT = 50_000  # exhaustive validation for CP below this
random.seed(42)


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------
def load_vocabs():
    with open(VOCAB_FILE, encoding="utf-8") as f:
        data = json.load(f)
    vocabs = {}
    for _cat, slots in data["categories"].items():
        for name, tokens in slots.items():
            vocabs[name] = tokens
    return data, vocabs


def load_templates():
    with open(TEMPLATES_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_icd_index():
    """Build inverted index: word -> set of term indices."""
    terms = []
    token_to_terms = defaultdict(set)
    with open(ICD_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            term = row["Term"].lower().strip()
            idx = len(terms)
            terms.append(term)
            for word in term.replace(",", " ").replace("(", " ").replace(")", " ").replace("/", " ").split():
                token_to_terms[word].add(idx)
    return terms, dict(token_to_terms)


# ---------------------------------------------------------------------------
# Check 1: Structural sanity
# ---------------------------------------------------------------------------
def check_structural(vocab_raw, vocabs, tpl_data):
    issues = []
    vocab_names = set(vocabs.keys())

    # Broken template -> vocab refs
    broken_refs = []
    for fam_name, fam in tpl_data["families"].items():
        for slot in fam["slots"]:
            v = slot["vocabulary"]
            if v not in vocab_names:
                broken_refs.append({"template": fam_name, "vocabulary": v})
    if broken_refs:
        issues.append("broken_vocab_refs")

    # Duplicate tokens within a vocabulary
    intra_dupes = {}
    for v_name, tokens in vocabs.items():
        if len(tokens) != len(set(tokens)):
            from collections import Counter
            dupes = {t: c for t, c in Counter(tokens).items() if c > 1}
            intra_dupes[v_name] = dupes
    if intra_dupes:
        issues.append("intra_vocab_duplicates")

    # Metadata accuracy
    actual_slots = len(vocabs)
    actual_tokens = sum(len(t) for t in vocabs.values())
    meta_slots_ok = vocab_raw["metadata"]["total_slots"] == actual_slots
    meta_tokens_ok = vocab_raw["metadata"]["total_tokens"] == actual_tokens
    actual_families = len(tpl_data["families"])
    meta_families_ok = tpl_data["metadata"]["total_families"] == actual_families
    if not (meta_slots_ok and meta_tokens_ok and meta_families_ok):
        issues.append("metadata_mismatch")

    return {
        "broken_refs": broken_refs,
        "intra_vocab_duplicates": intra_dupes,
        "metadata": {
            "vocab_slots": {"declared": vocab_raw["metadata"]["total_slots"], "actual": actual_slots, "ok": meta_slots_ok},
            "vocab_tokens": {"declared": vocab_raw["metadata"]["total_tokens"], "actual": actual_tokens, "ok": meta_tokens_ok},
            "template_families": {"declared": tpl_data["metadata"]["total_families"], "actual": actual_families, "ok": meta_families_ok},
        },
        "issues": issues,
    }


# ---------------------------------------------------------------------------
# Check 2: Token health
# ---------------------------------------------------------------------------
BRITISH_SPELLINGS = {
    "anaemia", "goitre", "haemorrhage", "haemorrhagic", "leukaemia",
    "septicemia", "tumour", "haemolytic", "oesophagus",
}

def check_token_health(vocabs, token_to_terms):
    zero_hit = {}
    for v_name, tokens in vocabs.items():
        missing = []
        for tok in tokens:
            words = tok.lower().split()
            if not all(w in token_to_terms for w in words):
                category = "british_spelling" if tok.lower() in BRITISH_SPELLINGS else \
                           "prefix" if v_name == "LOCATION_PREFIX_TOKENS" else \
                           "problematic"
                missing.append({"token": tok, "category": category})
        if missing:
            zero_hit[v_name] = missing

    # Cross-slot overlap
    token_owners = defaultdict(list)
    for v_name, tokens in vocabs.items():
        for tok in tokens:
            token_owners[tok].append(v_name)
    cross_slot = {tok: owners for tok, owners in token_owners.items() if len(owners) > 1}

    total_zero = sum(len(v) for v in zero_hit.values())
    return {
        "zero_hit_by_vocab": zero_hit,
        "zero_hit_total": total_zero,
        "cross_slot_overlap_count": len(cross_slot),
        "cross_slot_overlap": cross_slot,
    }


# ---------------------------------------------------------------------------
# Check 3: Template health
# ---------------------------------------------------------------------------
def check_template_health(vocabs, tpl_data):
    vocab_names = set(vocabs.keys())
    template_vocab_refs = set()
    for fam in tpl_data["families"].values():
        for slot in fam["slots"]:
            template_vocab_refs.add(slot["vocabulary"])

    orphaned = sorted(vocab_names - template_vocab_refs)

    # Order-variant detection
    sorted_combos = defaultdict(list)
    for fam_name, fam in tpl_data["families"].items():
        key = tuple(sorted(s["vocabulary"] for s in fam["slots"]))
        sorted_combos[key].append(fam_name)
    order_variants = {str(k): v for k, v in sorted_combos.items() if len(v) > 1}

    return {
        "orphaned_vocabs": orphaned,
        "orphaned_vocab_sizes": {v: len(vocabs[v]) for v in orphaned},
        "order_variant_groups": order_variants,
        "order_variant_count": len(order_variants),
    }


# ---------------------------------------------------------------------------
# Check 4: Ground-truth sampling
# ---------------------------------------------------------------------------
def _check_combo(combo, token_to_terms):
    """Check if all tokens in a combo co-occur in at least one ICD term."""
    sets = []
    for token in combo:
        for word in token.lower().split():
            s = token_to_terms.get(word)
            if not s:
                return False
            sets.append(s)
    sets.sort(key=len)
    result = set(sets[0])
    for s in sets[1:]:
        result &= s
        if not result:
            return False
    return True


def check_ground_truth(vocabs, tpl_data, token_to_terms):
    """Validate ALL templates against ICD-10-CM ground truth.

    Small templates (CP <= EXHAUSTIVE_LIMIT) are checked exhaustively.
    Larger templates are sampled.
    """
    results = {}

    for fam_name, fam in tpl_data["families"].items():
        slot_vocabs = [vocabs.get(s["vocabulary"], []) for s in fam["slots"]]
        if not all(slot_vocabs):
            continue

        cp_size = 1
        for sv in slot_vocabs:
            cp_size *= len(sv)

        exhaustive = cp_size <= GROUND_TRUTH_EXHAUSTIVE_LIMIT
        if exhaustive:
            combos = list(cartesian_product(*slot_vocabs))
        else:
            combos = [tuple(random.choice(v) for v in slot_vocabs)
                       for _ in range(GROUND_TRUTH_SAMPLE_SIZE)]

        hits = sum(1 for c in combos if _check_combo(c, token_to_terms))

        results[fam_name] = {
            "slot_count": len(fam["slots"]),
            "cross_product_size": cp_size,
            "sampled": len(combos),
            "exhaustive": exhaustive,
            "hits": hits,
            "hit_rate": round(hits / len(combos), 4) if combos else 0,
        }

    return results


# ---------------------------------------------------------------------------
# Overall status
# ---------------------------------------------------------------------------
def compute_status(structural, token_health, template_health):
    if structural["broken_refs"] or structural["intra_vocab_duplicates"]:
        return "FAIL"
    if structural["issues"]:
        return "WARN"
    if token_health["zero_hit_total"] > 120:
        return "WARN"
    if template_health["orphaned_vocabs"]:
        return "WARN"
    return "PASS"


# ---------------------------------------------------------------------------
# Human-readable summary
# ---------------------------------------------------------------------------
def print_summary(report):
    status = report["status"]
    marker = {"PASS": "PASS", "WARN": "WARN", "FAIL": "FAIL"}[status]
    print(f"\n{'='*70}")
    print(f"  VALIDATION REPORT — {marker}")
    print(f"  Vocab version: {report['vocab_version']}  |  {report['timestamp']}")
    print(f"{'='*70}\n")

    s = report["structural"]
    print(f"  Structural:")
    print(f"    Broken vocab refs:    {len(s['broken_refs'])}")
    print(f"    Intra-vocab dupes:    {len(s['intra_vocab_duplicates'])}")
    meta = s["metadata"]
    print(f"    Metadata slots:       {meta['vocab_slots']['actual']} {'OK' if meta['vocab_slots']['ok'] else 'MISMATCH'}")
    print(f"    Metadata tokens:      {meta['vocab_tokens']['actual']} {'OK' if meta['vocab_tokens']['ok'] else 'MISMATCH'}")
    print(f"    Metadata families:    {meta['template_families']['actual']} {'OK' if meta['template_families']['ok'] else 'MISMATCH'}")

    th = report["token_health"]
    print(f"\n  Token health:")
    print(f"    Zero-hit tokens:      {th['zero_hit_total']}")
    print(f"    Cross-slot overlaps:  {th['cross_slot_overlap_count']}")

    tmpl = report["template_health"]
    print(f"\n  Template health:")
    print(f"    Orphaned vocabs:      {len(tmpl['orphaned_vocabs'])} {tmpl['orphaned_vocabs'] if tmpl['orphaned_vocabs'] else ''}")
    print(f"    Order-variant groups: {tmpl['order_variant_count']}")

    if report.get("ground_truth"):
        gt = report["ground_truth"]
        # Group by slot count
        by_slots = {}
        for name, data in gt.items():
            n = data.get("slot_count", name.count("_x_") + 1)
            by_slots.setdefault(n, []).append((name, data))
        print(f"\n  Ground-truth ({len(gt)} templates):")
        for n in sorted(by_slots):
            entries = sorted(by_slots[n], key=lambda x: -x[1]["hit_rate"])
            avg_hit = sum(d["hit_rate"] for _, d in entries) / len(entries)
            print(f"\n    {n}-slot ({len(entries)} templates, avg hit_rate={avg_hit:.1%}):")
            for name, data in entries:
                ex = "EXH" if data.get("exhaustive") else "SMP"
                print(f"      {name[:50]:<50s} {data['hit_rate']:>6.1%}  ({data['hits']:>5}/{data['sampled']:<5}) [{ex}]")

    print(f"\n  Status: {marker}")
    print(f"  Report: {REPORT_FILE.relative_to(BASE_DIR)}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Loading vocabularies...", end=" ", flush=True)
    vocab_raw, vocabs = load_vocabs()
    print(f"{len(vocabs)} slots, {sum(len(t) for t in vocabs.values())} tokens")

    print("Loading templates...", end=" ", flush=True)
    tpl_data = load_templates()
    print(f"{len(tpl_data['families'])} families")

    icd_available = ICD_CSV.exists()
    token_to_terms = {}
    if icd_available:
        print("Loading ICD-10-CM index...", end=" ", flush=True)
        _terms, token_to_terms = load_icd_index()
        print(f"{len(token_to_terms):,} unique words")
    else:
        print(f"ICD-10-CM CSV not found at {ICD_CSV} — skipping ground-truth checks")

    print("Running checks...")
    structural = check_structural(vocab_raw, vocabs, tpl_data)
    token_health = check_token_health(vocabs, token_to_terms) if token_to_terms else {"zero_hit_by_vocab": {}, "zero_hit_total": 0, "cross_slot_overlap_count": 0, "cross_slot_overlap": {}}
    template_health = check_template_health(vocabs, tpl_data)
    ground_truth = check_ground_truth(vocabs, tpl_data, token_to_terms) if token_to_terms else {}

    status = compute_status(structural, token_health, template_health)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "vocab_version": vocab_raw["metadata"].get("version", "unknown"),
        "status": status,
        "structural": structural,
        "token_health": token_health,
        "template_health": template_health,
        "ground_truth": ground_truth,
    }

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
        f.write("\n")

    print_summary(report)
    return 0 if status != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())

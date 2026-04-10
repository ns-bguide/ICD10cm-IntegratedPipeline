#!/usr/bin/env python3
"""
Vocabulary & Template Validation Pipeline — Precision Analysis

Scores every token for medical specificity and every template for
DLP false-positive risk. Identifies cross-slot collisions per template.

Reads reference_data/ and ICD-10-CM source. Never writes to production files.
Outputs: analysis_outputs/precision_report.json + human summary to stdout.

Usage: python3 scripts/precision.py
"""

import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
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
REPORT_FILE = BASE_DIR / "analysis_outputs" / "precision_report.json"

# Common English words that appear in everyday (non-medical) text.
# A token that only appears in medical contexts is HIGH specificity.
# A token that appears in everyday English is LOW specificity (FP risk).
COMMON_ENGLISH = {
    # Body parts used colloquially
    "arm", "back", "bone", "chest", "ear", "eye", "face", "finger", "foot",
    "gum", "hand", "head", "heart", "hip", "jaw", "joint", "knee", "leg",
    "lip", "mouth", "nail", "neck", "nerve", "nose", "rib", "shoulder",
    "skin", "skull", "spine", "tongue", "tooth", "wrist",
    # Common English words that overlap with medical vocabulary
    "failure", "depression", "shock", "block", "collapse", "pain", "stress",
    "disease", "disorder", "burn", "wound", "injury", "trauma",
    "old", "new", "other", "left", "right", "multiple", "second", "level",
    "brief", "routine", "delayed", "sustained", "week", "month", "alive",
    "died", "healing", "chronic", "acute", "primary", "secondary",
    "associated", "lead", "foreign", "solid", "pressure",
    "type", "stage", "site", "involvement", "episode",
}


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


def load_icd_word_freq():
    """Count how many ICD-10-CM terms contain each word."""
    freq = defaultdict(int)
    term_count = 0
    with open(ICD_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            term = row["Term"].lower().strip()
            term_count += 1
            seen = set()
            for word in term.replace(",", " ").replace("(", " ").replace(")", " ").replace("/", " ").split():
                if word not in seen:
                    freq[word] += 1
                    seen.add(word)
    return dict(freq), term_count


# ---------------------------------------------------------------------------
# Token specificity scoring
# ---------------------------------------------------------------------------
def score_tokens(vocabs, icd_freq, icd_total):
    """Score each token: HIGH (medical-specific), MEDIUM, LOW (common English)."""
    results = {}
    for vocab_name, tokens in vocabs.items():
        for token in tokens:
            words = token.lower().split()
            # ICD frequency: fraction of ICD terms containing this token
            icd_hits = min(icd_freq.get(w, 0) for w in words)
            icd_frac = icd_hits / icd_total if icd_total else 0

            # Common English check
            is_common = any(w in COMMON_ENGLISH for w in words)

            # Specificity: HIGH if not common English and appears in ICD
            # LOW if common English regardless of ICD frequency
            # MEDIUM otherwise
            if is_common:
                specificity = "low"
            elif icd_hits > 0:
                specificity = "high"
            else:
                specificity = "medium"  # not common, but not in ICD either

            results.setdefault(vocab_name, {})[token] = {
                "specificity": specificity,
                "icd_term_count": icd_hits,
                "icd_fraction": round(icd_frac, 6),
                "is_common_english": is_common,
            }
    return results


# ---------------------------------------------------------------------------
# Template FP risk scoring
# ---------------------------------------------------------------------------
def score_templates(vocabs, tpl_data, token_scores):
    """Score each template for FP risk based on token specificity."""
    results = {}

    for fam_name, fam in tpl_data["families"].items():
        slot_vocabs = [s["vocabulary"] for s in fam["slots"]]
        slot_vocab_tokens = [vocabs.get(v, []) for v in slot_vocabs]

        if not all(slot_vocab_tokens):
            continue

        # Count low-specificity tokens per slot
        slot_specificity = []
        for vocab_name, tokens in zip(slot_vocabs, slot_vocab_tokens):
            scores = token_scores.get(vocab_name, {})
            low = sum(1 for t in tokens if scores.get(t, {}).get("specificity") == "low")
            high = sum(1 for t in tokens if scores.get(t, {}).get("specificity") == "high")
            total = len(tokens)
            slot_specificity.append({
                "vocabulary": vocab_name,
                "total": total,
                "high": high,
                "low": low,
                "low_fraction": round(low / total, 4) if total else 0,
            })

        # FP risk: estimate fraction of cross-product where ALL slots use low-specificity tokens
        # P(all_low) = product of (low_fraction per slot)
        all_low_prob = 1.0
        for ss in slot_specificity:
            all_low_prob *= ss["low_fraction"]
        # Also: any-slot-low probability
        any_low_prob = 1.0 - 1.0
        for ss in slot_specificity:
            any_low_prob = 1.0 - (1.0 - any_low_prob) * (1.0 - ss["low_fraction"])

        # Cross-slot collision: check if vocabs share tokens
        collisions = []
        for i, v1 in enumerate(slot_vocabs):
            for j, v2 in enumerate(slot_vocabs):
                if j <= i:
                    continue
                shared = set(vocabs.get(v1, [])) & set(vocabs.get(v2, []))
                if shared:
                    collisions.append({
                        "slot_a": v1,
                        "slot_b": v2,
                        "shared_tokens": sorted(shared),
                        "count": len(shared),
                    })

        # Risk level
        if all_low_prob > 0.01:
            risk = "HIGH"
        elif all_low_prob > 0.001:
            risk = "MEDIUM"
        elif collisions:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        cp = 1
        for sv in slot_vocab_tokens:
            cp *= len(sv)

        results[fam_name] = {
            "slot_count": len(fam["slots"]),
            "cross_product_size": cp,
            "fp_risk": risk,
            "all_low_probability": round(all_low_prob, 6),
            "slot_specificity": slot_specificity,
            "cross_slot_collisions": collisions,
            "collision_count": sum(c["count"] for c in collisions),
        }

    return results


# ---------------------------------------------------------------------------
# Human summary
# ---------------------------------------------------------------------------
def print_summary(report):
    print(f"\n{'='*70}")
    print(f"  PRECISION REPORT")
    print(f"  Vocab version: {report['vocab_version']}")
    print(f"{'='*70}\n")

    ts = report["token_specificity_summary"]
    print(f"  Token specificity:")
    print(f"    High (medical-specific):  {ts['high']:>4}")
    print(f"    Medium (not common):      {ts['medium']:>4}")
    print(f"    Low (common English):     {ts['low']:>4}")
    print(f"    Total:                    {ts['total']:>4}")

    tr = report["template_risk_summary"]
    print(f"\n  Template FP risk:")
    print(f"    HIGH risk:   {tr['HIGH']:>3}")
    print(f"    MEDIUM risk: {tr['MEDIUM']:>3}")
    print(f"    LOW risk:    {tr['LOW']:>3}")

    # Show HIGH risk templates
    high_risk = [(n, d) for n, d in report["template_scores"].items() if d["fp_risk"] == "HIGH"]
    if high_risk:
        print(f"\n  HIGH FP-risk templates ({len(high_risk)}):")
        for name, data in sorted(high_risk, key=lambda x: -x[1]["all_low_probability"]):
            print(f"    {name[:55]:<55s} P(all_low)={data['all_low_probability']:.3%}")
            for ss in data["slot_specificity"]:
                print(f"      {ss['vocabulary']:<35s} {ss['low']}/{ss['total']} low ({ss['low_fraction']:.0%})")

    # Show templates with cross-slot collisions
    colliding = [(n, d) for n, d in report["template_scores"].items() if d["cross_slot_collisions"]]
    if colliding:
        print(f"\n  Templates with cross-slot collisions ({len(colliding)}):")
        for name, data in sorted(colliding, key=lambda x: -x[1]["collision_count"]):
            print(f"    {name[:55]:<55s} {data['collision_count']} shared tokens")
            for c in data["cross_slot_collisions"]:
                print(f"      {c['slot_a']} <-> {c['slot_b']}: {c['shared_tokens']}")

    # Show vocabs with most low-specificity tokens
    print(f"\n  Vocabs with highest low-specificity fraction:")
    vocab_low = []
    for vocab_name, tokens in report["token_scores"].items():
        low = sum(1 for t in tokens.values() if t["specificity"] == "low")
        total = len(tokens)
        if low > 0:
            vocab_low.append((vocab_name, low, total))
    for vname, low, total in sorted(vocab_low, key=lambda x: -x[1]/x[2]):
        print(f"    {vname:<35s} {low:>3}/{total:<3} low ({low/total:.0%})")

    print(f"\n  Report: {REPORT_FILE.relative_to(BASE_DIR)}\n")


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

    if not ICD_CSV.exists():
        print(f"ERROR: ICD-10-CM CSV not found at {ICD_CSV}")
        return 1

    print("Loading ICD-10-CM word frequencies...", end=" ", flush=True)
    icd_freq, icd_total = load_icd_word_freq()
    print(f"{len(icd_freq):,} unique words from {icd_total:,} terms")

    print("Scoring token specificity...")
    token_scores = score_tokens(vocabs, icd_freq, icd_total)

    print("Scoring template FP risk...")
    template_scores = score_templates(vocabs, tpl_data, token_scores)

    # Summaries
    spec_counts = {"high": 0, "medium": 0, "low": 0}
    for vocab_tokens in token_scores.values():
        for data in vocab_tokens.values():
            spec_counts[data["specificity"]] += 1

    risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for data in template_scores.values():
        risk_counts[data["fp_risk"]] += 1

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "vocab_version": vocab_raw["metadata"].get("version", "unknown"),
        "token_specificity_summary": {**spec_counts, "total": sum(spec_counts.values())},
        "template_risk_summary": risk_counts,
        "token_scores": token_scores,
        "template_scores": template_scores,
    }

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")

    print_summary(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())

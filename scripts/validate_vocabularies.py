#!/usr/bin/env python3
"""
Vocabulary Validation & Refinement Tool

Uses empirical evidence from core terms expansion to validate and suggest
improvements to slot vocabularies.

Analyzes:
- Token usage: which tokens are empirically attested vs unused
- Missing tokens: high-frequency patterns not in vocabulary
- Misclassifications: adjectival tokens in ANATOMY_TOKENS
- Condition productivity: ranking for CONDITION_TOKENS priority
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, Set, List, Tuple

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
SLOT_VOC_FILE = BASE_DIR / "reference_data" / "slot_vocabularies.json"
FAMILY_TPL_FILE = BASE_DIR / "reference_data" / "family_templates.json"
EXPANSION_REPORT = BASE_DIR / "analysis_outputs" / "core_terms_expansion_report.txt"
CORE_TERMS_FILE = BASE_DIR / "reference_data" / "icd10cm_core_terms.txt"

# Outputs
VALIDATION_REPORT = BASE_DIR / "analysis_outputs" / "vocabulary_validation_report.md"
REFINEMENT_SUGGESTIONS = BASE_DIR / "analysis_outputs" / "vocabulary_refinement_suggestions.json"

# Source file for ADJECTIVAL_ANATOMY list
EXPAND_SCRIPT = Path("/home/bguide/compositional_analysis/core_terms/icd10cm-core-terms/scripts/expand_with_templates.py")


def load_slot_vocabularies() -> Dict[str, Set[str]]:
    """Load slot vocabularies from JSON."""
    with open(SLOT_VOC_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    vocabs = {}
    for category, slots in data['categories'].items():
        for slot_name, tokens in slots.items():
            vocabs[slot_name] = set(t.lower() for t in tokens)

    return vocabs


def parse_expansion_report() -> Dict[str, any]:
    """Parse the core terms expansion report for empirical evidence."""
    with open(EXPANSION_REPORT, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract empirical pairs count
    empirical_anatomies = 0
    conditions_with_variants = 0

    match = re.search(r'Noun anatomy tokens \(of-position\)\s*:\s*(\d+)', content)
    if match:
        empirical_anatomies = int(match.group(1))

    match = re.search(r'Conditions with anatomy variants\s*:\s*(\d+)', content)
    if match:
        conditions_with_variants = int(match.group(1))

    # Extract condition productivity rankings
    condition_productivity = {}
    in_productivity_section = False

    for line in content.split('\n'):
        if 'Top expanded conditions' in line:
            in_productivity_section = True
            continue

        if in_productivity_section:
            # Parse line like: "  thrombosis               : +122 new  (3 attested)"
            match = re.match(r'\s+(\w+)\s*:\s*\+(\d+)\s+new\s+\((\d+)\s+attested\)', line)
            if match:
                condition = match.group(1)
                new_count = int(match.group(2))
                attested = int(match.group(3))
                condition_productivity[condition] = {
                    'new_variants': new_count,
                    'attested': attested,
                    'ratio': new_count / attested if attested > 0 else 0
                }
            elif line.strip() == '':
                break  # End of section

    # Extract anatomy-bearing templates
    anatomy_bearing_templates = []
    in_template_section = False

    for line in content.split('\n'):
        if 'Family templates with anatomy' in line:
            in_template_section = True
            continue

        if in_template_section:
            line = line.strip()
            if line and not line.startswith('Top expanded'):
                anatomy_bearing_templates.append(line)
            elif line.startswith('Top expanded'):
                break

    return {
        'empirical_anatomies': empirical_anatomies,
        'conditions_with_variants': conditions_with_variants,
        'condition_productivity': condition_productivity,
        'anatomy_bearing_templates': anatomy_bearing_templates
    }


def extract_adjectival_anatomy() -> Set[str]:
    """Extract ADJECTIVAL_ANATOMY set from expand_with_templates.py."""
    if not EXPAND_SCRIPT.exists():
        return set()

    with open(EXPAND_SCRIPT, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find ADJECTIVAL_ANATOMY = { ... }
    match = re.search(r'ADJECTIVAL_ANATOMY\s*=\s*\{([^}]+)\}', content, re.DOTALL)
    if not match:
        return set()

    # Extract tokens from the set
    tokens_str = match.group(1)
    tokens = re.findall(r'"([^"]+)"', tokens_str)

    return set(t.lower() for t in tokens)


def analyze_anatomy_tokens(vocabs: Dict[str, Set[str]],
                           empirical_count: int,
                           adjectival_anatomy: Set[str]) -> Dict:
    """Analyze ANATOMY_TOKENS for usage and misclassification."""
    anatomy_tokens = vocabs.get('ANATOMY_TOKENS', set())

    # Count tokens in ANATOMY_TOKENS that are also in ADJECTIVAL_ANATOMY
    misclassified = anatomy_tokens & adjectival_anatomy

    # Estimate unused (total - empirical, rough approximation)
    total_anatomy = len(anatomy_tokens)
    unused_estimate = total_anatomy - empirical_count

    return {
        'total_anatomy_tokens': total_anatomy,
        'empirical_attested': empirical_count,
        'usage_rate': f"{(empirical_count / total_anatomy * 100):.1f}%" if total_anatomy > 0 else "0%",
        'unused_estimate': unused_estimate,
        'misclassified_count': len(misclassified),
        'misclassified_tokens': sorted(misclassified)
    }


def analyze_condition_tokens(vocabs: Dict[str, Set[str]],
                             productivity: Dict[str, Dict]) -> Dict:
    """Analyze CONDITION_TOKENS for productivity."""
    condition_tokens = vocabs.get('CONDITION_TOKENS', set())

    # Check which high-productivity conditions are in vocabulary
    high_productivity = {k: v for k, v in productivity.items() if v['ratio'] > 30}

    in_vocab = set()
    missing = set()

    for condition in high_productivity:
        if condition in condition_tokens:
            in_vocab.add(condition)
        else:
            missing.add(condition)

    return {
        'total_condition_tokens': len(condition_tokens),
        'high_productivity_count': len(high_productivity),
        'in_vocabulary': sorted(in_vocab),
        'missing_from_vocabulary': sorted(missing),
        'top_by_productivity': sorted(
            productivity.items(),
            key=lambda x: x[1]['ratio'],
            reverse=True
        )[:20]
    }


def extract_empirical_anatomy_tokens() -> Set[str]:
    """Extract anatomy tokens empirically used in core terms."""
    empirical_anatomies = set()

    if not CORE_TERMS_FILE.exists():
        return empirical_anatomies

    # Load anatomy tokens for matching
    vocabs = load_slot_vocabularies()
    anatomy_tokens = vocabs.get('ANATOMY_TOKENS', set())

    with open(CORE_TERMS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            term = line.strip().lower()

            # Look for "X of anatomy" patterns
            if ' of ' in term:
                parts = term.split(' of ')
                if len(parts) >= 2:
                    # Check words after "of"
                    words = parts[1].split()
                    if words and words[0] in anatomy_tokens:
                        empirical_anatomies.add(words[0])

            # Look for "anatomy X" patterns (2-word terms)
            words = term.split()
            if len(words) == 2 and words[0] in anatomy_tokens:
                empirical_anatomies.add(words[0])

    return empirical_anatomies


def generate_validation_report(analysis: Dict) -> str:
    """Generate markdown validation report."""
    lines = [
        "# Vocabulary Validation Report",
        "",
        f"**Generated**: {Path(__file__).name}",
        f"**Source**: Core terms expansion empirical evidence",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"- **ANATOMY_TOKENS**: {analysis['anatomy']['total_anatomy_tokens']} defined, "
        f"{analysis['anatomy']['empirical_attested']} empirically attested ({analysis['anatomy']['usage_rate']})",
        f"- **Unused tokens estimate**: {analysis['anatomy']['unused_estimate']} tokens (candidates for review)",
        f"- **Misclassified tokens**: {analysis['anatomy']['misclassified_count']} adjectival tokens in ANATOMY_TOKENS",
        f"- **CONDITION_TOKENS**: {analysis['conditions']['total_condition_tokens']} defined",
        f"- **High-productivity conditions**: {analysis['conditions']['high_productivity_count']} (ratio >30x)",
        "",
        "---",
        "",
        "## 1. ANATOMY_TOKENS Analysis",
        "",
        "### Usage Statistics",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total ANATOMY_TOKENS | {analysis['anatomy']['total_anatomy_tokens']} |",
        f"| Empirically attested (noun form) | {analysis['anatomy']['empirical_attested']} |",
        f"| Usage rate | {analysis['anatomy']['usage_rate']} |",
        f"| Unused estimate | ~{analysis['anatomy']['unused_estimate']} tokens |",
        "",
        "**Insight**: Only 60.8% of ANATOMY_TOKENS are empirically attested as noun forms in "
        "\"condition of anatomy\" patterns. The remaining tokens may be:",
        "- Purely adjectival (e.g., 'cardiac', 'pulmonary')",
        "- Rarely used anatomical regions",
        "- Misclassified tokens",
        "",
        "### Misclassified Tokens (Adjectival in ANATOMY_TOKENS)",
        "",
        f"**Count**: {analysis['anatomy']['misclassified_count']} tokens",
        "",
    ]

    if analysis['anatomy']['misclassified_tokens']:
        lines.append("These tokens are in ANATOMY_TOKENS but marked as adjectival in expand_with_templates.py:")
        lines.append("")
        for i, token in enumerate(analysis['anatomy']['misclassified_tokens'], 1):
            lines.append(f"{i}. `{token}`")
            if i % 10 == 0 and i < len(analysis['anatomy']['misclassified_tokens']):
                lines.append("")
    else:
        lines.append("No misclassifications detected.")

    lines.extend([
        "",
        "**Recommendation**: Consider creating separate `ANATOMY_ADJECTIVE_TOKENS` vocabulary for proper classification.",
        "",
        "---",
        "",
        "## 2. CONDITION_TOKENS Analysis",
        "",
        "### Productivity Rankings",
        "",
        "Top conditions by expansion potential (ratio = new variants / attested):",
        "",
        "| Rank | Condition | New Variants | Attested | Ratio | In Vocab? |",
        "|------|-----------|--------------|----------|-------|-----------|",
    ])

    vocabs = load_slot_vocabularies()
    condition_tokens = vocabs.get('CONDITION_TOKENS', set())

    for i, (condition, stats) in enumerate(analysis['conditions']['top_by_productivity'][:15], 1):
        in_vocab = "✓" if condition in condition_tokens else "✗"
        lines.append(
            f"| {i} | {condition} | +{stats['new_variants']} | "
            f"{stats['attested']} | {stats['ratio']:.1f}x | {in_vocab} |"
        )

    lines.extend([
        "",
        "### High-Productivity Conditions Missing from Vocabulary",
        "",
    ])

    if analysis['conditions']['missing_from_vocabulary']:
        lines.append(f"**Count**: {len(analysis['conditions']['missing_from_vocabulary'])} conditions")
        lines.append("")
        lines.append("These high-productivity conditions (ratio >30x) are NOT in CONDITION_TOKENS:")
        lines.append("")
        for condition in analysis['conditions']['missing_from_vocabulary']:
            stats = analysis['condition_productivity'][condition]
            lines.append(f"- `{condition}` — {stats['new_variants']} variants, ratio {stats['ratio']:.1f}x")
    else:
        lines.append("✓ All high-productivity conditions are in vocabulary.")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Empirical Token Discovery",
        "",
        f"**Empirically used anatomy tokens**: {len(analysis['empirical_anatomies'])}",
        "",
    ])

    # Find tokens used empirically but not in vocabulary
    anatomy_tokens = vocabs.get('ANATOMY_TOKENS', set())
    missing_anatomies = analysis['empirical_anatomies'] - anatomy_tokens

    if missing_anatomies:
        lines.append("### Anatomy Tokens Found in Core Terms but NOT in ANATOMY_TOKENS")
        lines.append("")
        lines.append(f"**Count**: {len(missing_anatomies)}")
        lines.append("")
        lines.append("These tokens appear in core terms but are missing from vocabulary:")
        lines.append("")
        for token in sorted(missing_anatomies):
            lines.append(f"- `{token}`")
    else:
        lines.append("✓ All empirical anatomy tokens are in vocabulary.")

    lines.extend([
        "",
        "---",
        "",
        "## 4. Recommendations",
        "",
        "### High Priority",
        "",
        "1. **Review misclassified tokens** ({} tokens)".format(analysis['anatomy']['misclassified_count']),
        "   - Create `ANATOMY_ADJECTIVE_TOKENS` vocabulary",
        "   - Move adjectival forms from ANATOMY_TOKENS",
        "   - Keep noun forms (e.g., 'heart') in ANATOMY_TOKENS",
        "",
        "2. **Review unused anatomy tokens** (~{} tokens)".format(analysis['anatomy']['unused_estimate']),
        "   - Check if tokens are valid but rare",
        "   - Remove if misclassified or not applicable",
        "   - Consider moving to specialty vocabulary",
        "",
        "### Medium Priority",
        "",
    ])

    if missing_anatomies:
        lines.append(f"3. **Add missing anatomy tokens** ({len(missing_anatomies)} candidates)")
        lines.append("   - Review empirically discovered tokens")
        lines.append("   - Add if clinically valid")
        lines.append("")

    lines.extend([
        "4. **Prioritize high-productivity conditions**",
        "   - Focus on conditions with ratio >30x",
        "   - Ensure all are in CONDITION_TOKENS",
        "",
        "### Validation Checklist",
        "",
        "Before applying vocabulary changes:",
        "",
        "- [ ] Token appears in 3+ empirical patterns",
        "- [ ] Token improves coverage (test with test_vocabulary_change.py)",
        "- [ ] Token doesn't introduce false positives",
        "- [ ] Token is correctly classified (anatomy vs condition vs qualifier)",
        "- [ ] Core terms pipeline runs successfully with change",
        "",
        "---",
        "",
        "## Next Steps",
        "",
        "1. Review this report with domain experts",
        "2. Apply high-priority changes to vocabularies",
        "3. Test changes: `python scripts/test_vocabulary_change.py`",
        "4. Re-run validation after changes",
        "5. Export updated vocabularies to source projects",
        "",
        "---",
        "",
        "**See also**:",
        "- [vocabulary_refinement_suggestions.json](vocabulary_refinement_suggestions.json) - Machine-readable suggestions",
        "- [CORE_TERMS_INTEGRATION.md](../docs/CORE_TERMS_INTEGRATION.md) - Integration guide",
        "- [VOCABULARY_CURATION_GUIDE.md](../docs/VOCABULARY_CURATION_GUIDE.md) - Curation workflow",
    ])

    return "\n".join(lines)


def generate_refinement_suggestions(analysis: Dict) -> Dict:
    """Generate machine-readable refinement suggestions."""
    return {
        "metadata": {
            "generated_by": "validate_vocabularies.py",
            "source": "core_terms expansion empirical evidence"
        },
        "anatomy_tokens": {
            "total": analysis['anatomy']['total_anatomy_tokens'],
            "empirical_attested": analysis['anatomy']['empirical_attested'],
            "usage_rate": analysis['anatomy']['usage_rate'],
            "misclassified": {
                "count": analysis['anatomy']['misclassified_count'],
                "tokens": analysis['anatomy']['misclassified_tokens'],
                "action": "move_to_ANATOMY_ADJECTIVE_TOKENS"
            },
            "unused_estimate": analysis['anatomy']['unused_estimate'],
            "add_candidates": sorted(analysis['empirical_anatomies'] -
                                    load_slot_vocabularies().get('ANATOMY_TOKENS', set()))
        },
        "condition_tokens": {
            "total": analysis['conditions']['total_condition_tokens'],
            "high_productivity": {
                "count": analysis['conditions']['high_productivity_count'],
                "missing": analysis['conditions']['missing_from_vocabulary'],
                "action": "add_to_CONDITION_TOKENS"
            },
            "top_productive": [
                {
                    "condition": cond,
                    "new_variants": stats['new_variants'],
                    "attested": stats['attested'],
                    "ratio": round(stats['ratio'], 1)
                }
                for cond, stats in analysis['conditions']['top_by_productivity'][:20]
            ]
        },
        "recommendations": {
            "high_priority": [
                {
                    "action": "create_ANATOMY_ADJECTIVE_TOKENS",
                    "tokens_affected": analysis['anatomy']['misclassified_count'],
                    "reason": "Separate adjectival from noun forms"
                },
                {
                    "action": "review_unused_anatomy_tokens",
                    "tokens_affected": analysis['anatomy']['unused_estimate'],
                    "reason": "Validate rare/unused tokens"
                }
            ],
            "medium_priority": [
                {
                    "action": "add_empirical_anatomy_tokens",
                    "tokens_affected": len(analysis['empirical_anatomies'] -
                                          load_slot_vocabularies().get('ANATOMY_TOKENS', set())),
                    "reason": "Include validated empirical discoveries"
                },
                {
                    "action": "prioritize_high_productivity_conditions",
                    "tokens_affected": analysis['conditions']['high_productivity_count'],
                    "reason": "Maximize expansion potential"
                }
            ]
        }
    }


def main():
    """Main execution."""
    print("=" * 80)
    print("VOCABULARY VALIDATION & REFINEMENT TOOL")
    print("=" * 80)
    print()

    # Load data
    print("Loading vocabularies...")
    vocabs = load_slot_vocabularies()
    print(f"  ✓ Loaded {len(vocabs)} vocabulary slots")

    print("Parsing expansion report...")
    report_data = parse_expansion_report()
    print(f"  ✓ Empirical anatomies: {report_data['empirical_anatomies']}")
    print(f"  ✓ Conditions with variants: {report_data['conditions_with_variants']}")
    print(f"  ✓ Condition productivity rankings: {len(report_data['condition_productivity'])}")

    print("Extracting ADJECTIVAL_ANATOMY list...")
    adjectival_anatomy = extract_adjectival_anatomy()
    print(f"  ✓ Found {len(adjectival_anatomy)} adjectival tokens")

    print("Extracting empirical anatomy tokens from core terms...")
    empirical_anatomies = extract_empirical_anatomy_tokens()
    print(f"  ✓ Found {len(empirical_anatomies)} empirically used anatomy tokens")

    # Analyze
    print("\nAnalyzing ANATOMY_TOKENS...")
    anatomy_analysis = analyze_anatomy_tokens(
        vocabs,
        report_data['empirical_anatomies'],
        adjectival_anatomy
    )
    print(f"  ✓ Usage rate: {anatomy_analysis['usage_rate']}")
    print(f"  ✓ Misclassified: {anatomy_analysis['misclassified_count']} tokens")

    print("Analyzing CONDITION_TOKENS...")
    condition_analysis = analyze_condition_tokens(
        vocabs,
        report_data['condition_productivity']
    )
    print(f"  ✓ High-productivity conditions: {condition_analysis['high_productivity_count']}")

    # Compile analysis
    analysis = {
        'anatomy': anatomy_analysis,
        'conditions': condition_analysis,
        'condition_productivity': report_data['condition_productivity'],
        'empirical_anatomies': empirical_anatomies
    }

    # Generate outputs
    print("\nGenerating validation report...")
    report = generate_validation_report(analysis)
    VALIDATION_REPORT.write_text(report, encoding='utf-8')
    print(f"  ✓ Saved: {VALIDATION_REPORT}")

    print("Generating refinement suggestions...")
    suggestions = generate_refinement_suggestions(analysis)
    with open(REFINEMENT_SUGGESTIONS, 'w', encoding='utf-8') as f:
        json.dump(suggestions, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved: {REFINEMENT_SUGGESTIONS}")

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"ANATOMY_TOKENS: {anatomy_analysis['total_anatomy_tokens']} defined, "
          f"{anatomy_analysis['empirical_attested']} attested ({anatomy_analysis['usage_rate']})")
    print(f"Misclassified tokens: {anatomy_analysis['misclassified_count']}")
    print(f"CONDITION_TOKENS: {condition_analysis['total_condition_tokens']} defined")
    print(f"High-productivity conditions: {condition_analysis['high_productivity_count']}")
    print()
    print(f"📊 Review report: {VALIDATION_REPORT.relative_to(BASE_DIR)}")
    print(f"📋 Refinement suggestions: {REFINEMENT_SUGGESTIONS.relative_to(BASE_DIR)}")
    print()


if __name__ == "__main__":
    main()

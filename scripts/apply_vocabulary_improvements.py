#!/usr/bin/env python3
"""
Apply Vocabulary Improvements

Implements the recommendations from vocabulary validation:
1. Create ANATOMY_ADJECTIVE_TOKENS vocabulary
2. Move adjectival tokens from ANATOMY_TOKENS to ANATOMY_ADJECTIVE_TOKENS
3. Update metadata with version and change log
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
SLOT_VOC_FILE = BASE_DIR / "reference_data" / "slot_vocabularies.json"
REFINEMENT_FILE = BASE_DIR / "analysis_outputs" / "vocabulary_refinement_suggestions.json"
IMPACT_REPORT = BASE_DIR / "analysis_outputs" / "vocabulary_improvement_impact.md"

def load_vocabularies():
    """Load current vocabularies."""
    with open(SLOT_VOC_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_refinement_suggestions():
    """Load refinement suggestions."""
    with open(REFINEMENT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def apply_improvements(vocabs, suggestions):
    """Apply vocabulary improvements."""
    changes = []

    # Get tokens to move
    adjectival_tokens = suggestions['anatomy_tokens']['misclassified']['tokens']

    # Create ANATOMY_ADJECTIVE_TOKENS if it doesn't exist
    if 'ANATOMY_ADJECTIVE_TOKENS' not in vocabs['categories'].get('Anatomical Modifiers', {}):
        # Find or create Anatomical Modifiers category
        if 'Anatomical Modifiers' not in vocabs['categories']:
            vocabs['categories']['Anatomical Modifiers'] = {}

        vocabs['categories']['Anatomical Modifiers']['ANATOMY_ADJECTIVE_TOKENS'] = []
        changes.append("Created ANATOMY_ADJECTIVE_TOKENS vocabulary")

    # Move tokens from ANATOMY_TOKENS to ANATOMY_ADJECTIVE_TOKENS
    anatomy_tokens = vocabs['categories']['Core Compositional Slots']['ANATOMY_TOKENS']
    anatomy_adjective_tokens = vocabs['categories']['Anatomical Modifiers']['ANATOMY_ADJECTIVE_TOKENS']

    moved_count = 0
    for token in adjectival_tokens:
        # Case-insensitive search
        found = None
        for i, t in enumerate(anatomy_tokens):
            if t.lower() == token.lower():
                found = i
                break

        if found is not None:
            removed_token = anatomy_tokens.pop(found)
            if removed_token not in anatomy_adjective_tokens:
                anatomy_adjective_tokens.append(removed_token)
                moved_count += 1

    # Sort the new vocabulary
    anatomy_adjective_tokens.sort()

    changes.append(f"Moved {moved_count} tokens from ANATOMY_TOKENS to ANATOMY_ADJECTIVE_TOKENS")

    # Update metadata
    old_total = vocabs['metadata'].get('total_tokens', 0)
    new_total = sum(
        len(tokens)
        for category in vocabs['categories'].values()
        for tokens in category.values()
    )

    old_slots = vocabs['metadata'].get('total_slots', 0)
    new_slots = sum(len(category) for category in vocabs['categories'].values())

    vocabs['metadata'].update({
        'total_slots': new_slots,
        'total_tokens': new_total,
        'last_updated': datetime.now().isoformat(),
        'version': '2026-03-27-v2',
        'changes': changes
    })

    return vocabs, {
        'moved_count': moved_count,
        'old_anatomy_count': len(anatomy_tokens) + moved_count,
        'new_anatomy_count': len(anatomy_tokens),
        'new_adjective_count': len(anatomy_adjective_tokens),
        'old_slots': old_slots,
        'new_slots': new_slots,
        'old_total_tokens': old_total,
        'new_total_tokens': new_total
    }

def generate_impact_report(stats, changes):
    """Generate impact report."""
    lines = [
        "# Vocabulary Improvement Impact Report",
        "",
        f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Version**: 2026-03-27-v2",
        "",
        "---",
        "",
        "## Changes Applied",
        "",
    ]

    for i, change in enumerate(changes, 1):
        lines.append(f"{i}. {change}")

    lines.extend([
        "",
        "---",
        "",
        "## Impact Summary",
        "",
        "### Token Reclassification",
        "",
        "| Metric | Before | After | Change |",
        "|--------|--------|-------|--------|",
        f"| ANATOMY_TOKENS | {stats['old_anatomy_count']} | {stats['new_anatomy_count']} | -{stats['moved_count']} |",
        f"| ANATOMY_ADJECTIVE_TOKENS | 0 | {stats['new_adjective_count']} | +{stats['new_adjective_count']} |",
        f"| Total vocabulary slots | {stats['old_slots']} | {stats['new_slots']} | +{stats['new_slots'] - stats['old_slots']} |",
        f"| Total tokens | {stats['old_total_tokens']} | {stats['new_total_tokens']} | {stats['new_total_tokens'] - stats['old_total_tokens']:+d} |",
        "",
        "### Benefits",
        "",
        "1. **Improved Classification**",
        "   - Adjectival forms now properly separated from noun forms",
        "   - Prevents invalid term generation like \"abscess of cardiac\"",
        "   - Enables correct pattern matching in expansion algorithms",
        "",
        "2. **Reduced False Positives**",
        "   - Template expansion uses ANATOMY_TOKENS for \"of anatomy\" patterns",
        "   - Only noun forms generate valid terms",
        "   - ~30 fewer invalid term candidates",
        "",
        "3. **Enhanced Expressiveness**",
        "   - ANATOMY_ADJECTIVE_TOKENS available for adjectival patterns",
        "   - Future templates can use adjectives appropriately",
        "   - Better semantic modeling",
        "",
        "---",
        "",
        "## Moved Tokens",
        "",
        f"The following {stats['moved_count']} tokens were moved from ANATOMY_TOKENS to ANATOMY_ADJECTIVE_TOKENS:",
        ""
    ])

    # Get the actual moved tokens from refinement suggestions
    with open(REFINEMENT_FILE, 'r', encoding='utf-8') as f:
        suggestions = json.load(f)

    adjectival_tokens = suggestions['anatomy_tokens']['misclassified']['tokens']
    for i, token in enumerate(adjectival_tokens, 1):
        lines.append(f"{i}. `{token}`")
        if i % 5 == 0 and i < len(adjectival_tokens):
            lines.append("")

    lines.extend([
        "",
        "---",
        "",
        "## Next Steps",
        "",
        "1. **Test Impact**",
        "   ```bash",
        "   # Copy improved vocabulary to core terms project",
        "   cp reference_data/slot_vocabularies.json \\",
        "      /home/bguide/compositional_analysis/core_terms/icd10cm-core-terms/resources/",
        "   ",
        "   # Re-run expansion",
        "   cd /home/bguide/compositional_analysis/core_terms/icd10cm-core-terms/scripts",
        "   python3 expand_with_templates.py",
        "   ```",
        "",
        "2. **Validate Changes**",
        "   ```bash",
        "   # Re-run validation",
        "   python3 scripts/validate_vocabularies.py",
        "   ",
        "   # Compare expansion reports",
        "   diff analysis_outputs/core_terms_expansion_report.txt \\",
        "        /path/to/new/expansion_report.txt",
        "   ```",
        "",
        "3. **Export to Source Projects**",
        "   ```bash",
        "   # Copy to main project",
        "   cp reference_data/slot_vocabularies.json \\",
        "      /home/bguide/compositional_analysis/",
        "   ",
        "   # Re-run main analyzer",
        "   cd /home/bguide/compositional_analysis",
        "   python3 analyze_compositionality.py",
        "   ```",
        "",
        "4. **Commit Changes**",
        "   ```bash",
        "   git add reference_data/slot_vocabularies.json",
        "   git commit -m \"Apply vocabulary improvements: create ANATOMY_ADJECTIVE_TOKENS\"",
        "   ```",
        "",
        "---",
        "",
        "## Expected Outcomes",
        "",
        "### Core Terms Expansion",
        "- **Fewer invalid terms**: Elimination of nonsensical \"condition of adjective\" patterns",
        "- **Cleaner output**: Only valid noun anatomy forms in expansion",
        "- **Same valid term count**: No reduction in clinically valid terms",
        "",
        "### Main Compositional Analysis",
        "- **Potential coverage improvement**: More precise slot matching",
        "- **Better family assignment**: Clearer distinction between adjective/noun anatomy",
        "- **Template applicability**: New templates can leverage ANATOMY_ADJECTIVE_TOKENS",
        "",
        "---",
        "",
        "## Validation Checklist",
        "",
        "After applying changes:",
        "",
        "- [ ] No invalid terms generated (e.g., \"abscess of cardiac\")",
        "- [ ] Core terms expansion count stable or improved",
        "- [ ] Main analyzer coverage maintained or improved",
        "- [ ] All tests pass in both projects",
        "- [ ] Documentation updated with new vocabulary",
        "",
        "---",
        "",
        "**See also**:",
        "- [vocabulary_validation_report.md](vocabulary_validation_report.md) - Original validation",
        "- [vocabulary_refinement_suggestions.json](vocabulary_refinement_suggestions.json) - Suggestions",
        "- [slot_vocabularies.json](../reference_data/slot_vocabularies.json) - Updated vocabularies",
    ])

    return "\n".join(lines)

def main():
    """Main execution."""
    print("=" * 80)
    print("APPLYING VOCABULARY IMPROVEMENTS")
    print("=" * 80)
    print()

    # Load data
    print("Loading vocabularies...")
    vocabs = load_vocabularies()
    print(f"  ✓ Current: {vocabs['metadata'].get('total_slots', 0)} slots, "
          f"{vocabs['metadata'].get('total_tokens', 0)} tokens")

    print("Loading refinement suggestions...")
    suggestions = load_refinement_suggestions()
    print(f"  ✓ Tokens to reclassify: {suggestions['anatomy_tokens']['misclassified']['count']}")

    # Apply improvements
    print("\nApplying improvements...")
    updated_vocabs, stats = apply_improvements(vocabs, suggestions)
    print(f"  ✓ Moved {stats['moved_count']} tokens to ANATOMY_ADJECTIVE_TOKENS")
    print(f"  ✓ ANATOMY_TOKENS: {stats['old_anatomy_count']} → {stats['new_anatomy_count']}")
    print(f"  ✓ ANATOMY_ADJECTIVE_TOKENS: 0 → {stats['new_adjective_count']}")

    # Save updated vocabularies
    print("\nSaving updated vocabularies...")
    with open(SLOT_VOC_FILE, 'w', encoding='utf-8') as f:
        json.dump(updated_vocabs, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved: {SLOT_VOC_FILE}")

    # Generate impact report
    print("Generating impact report...")
    report = generate_impact_report(stats, updated_vocabs['metadata']['changes'])
    with open(IMPACT_REPORT, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  ✓ Saved: {IMPACT_REPORT}")

    # Summary
    print("\n" + "=" * 80)
    print("IMPROVEMENTS APPLIED SUCCESSFULLY")
    print("=" * 80)
    print(f"Version: {updated_vocabs['metadata']['version']}")
    print(f"Changes:")
    for change in updated_vocabs['metadata']['changes']:
        print(f"  • {change}")
    print()
    print(f"📊 Impact report: {IMPACT_REPORT.relative_to(BASE_DIR)}")
    print(f"📦 Updated vocabularies: {SLOT_VOC_FILE.relative_to(BASE_DIR)}")
    print()
    print("Next: Export to source projects and test impact")
    print()

if __name__ == "__main__":
    main()

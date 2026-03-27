#!/usr/bin/env python3
"""
Export slot vocabularies from analyze_compositionality.py in hierarchical format.
"""

import re
import json
from collections import OrderedDict

def extract_vocabularies_from_file():
    """Extract all vocabulary sets from analyze_compositionality.py."""

    with open('analyze_compositionality.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match TOKEN sets
    pattern = r'([A-Z_]+TOKENS)\s*=\s*\{([^}]+)\}'
    matches = re.findall(pattern, content, re.DOTALL)

    vocabularies = OrderedDict()

    for slot_name, tokens_str in matches:
        # Parse tokens from the set definition
        tokens = []

        # Match quoted strings (single or double quotes)
        quoted = re.findall(r'["\']([^"\']+)["\']', tokens_str)
        tokens.extend(quoted)

        # Remove duplicates while preserving order
        seen = set()
        unique_tokens = []
        for token in tokens:
            if token not in seen:
                seen.add(token)
                unique_tokens.append(token)

        vocabularies[slot_name] = sorted(unique_tokens)

    return vocabularies

def categorize_slots(vocabularies):
    """Organize slots into semantic categories."""

    categories = OrderedDict()

    # Core compositional slots
    categories['Core Compositional Slots'] = OrderedDict()
    core_slots = [
        'ANATOMY_TOKENS',
        'CONDITION_TOKENS',
        'INJURY_TOKENS',
        'ENCOUNTER_TOKENS',
        'QUALIFIER_TOKENS',
    ]
    for slot in core_slots:
        if slot in vocabularies:
            categories['Core Compositional Slots'][slot] = vocabularies[slot]

    # Anatomical modifiers
    categories['Anatomical Modifiers'] = OrderedDict()
    anatomical_slots = [
        'LATERALITY_TOKENS',
        'LOCATION_TOKENS',
        'LOCATION_PREFIX_TOKENS',
        'ANATOMY_PREFIX_TOKENS',
    ]
    for slot in anatomical_slots:
        if slot in vocabularies:
            categories['Anatomical Modifiers'][slot] = vocabularies[slot]

    # Clinical detail
    categories['Clinical Detail & Classification'] = OrderedDict()
    clinical_slots = [
        'SEVERITY_TOKENS',
        'DISEASE_STATE_TOKENS',
        'DIAGNOSTIC_CLASSIFIER_TOKENS',
        'DIAGNOSTIC_EVENT_TOKENS',
        'DIAGNOSTIC_CONTEXT_TOKENS',
        'FRACTURE_DETAIL_TOKENS',
        'HEALING_TOKENS',
        'MODIFIER_WITH_TOKENS',
    ]
    for slot in clinical_slots:
        if slot in vocabularies:
            categories['Clinical Detail & Classification'][slot] = vocabularies[slot]

    # Specialized domains
    categories['Specialized Domains'] = OrderedDict()
    specialized_slots = [
        'TOXIC_EVENT_TOKENS',
        'TOXIC_INTENT_TOKENS',
        'TOXIC_AGENT_TOKENS',
        'MECHANISM_TOKENS',
        'ETIOLOGY_TOKENS',
        'PROCEDURE_TOKENS',
        'COMPLICATION_TOKENS',
        'MATERNAL_CONTEXT_TOKENS',
        'DURATION_TOKENS',
        'OUTCOME_TOKENS',
        'CONSCIOUSNESS_LEVEL_TOKENS',
    ]
    for slot in specialized_slots:
        if slot in vocabularies:
            categories['Specialized Domains'][slot] = vocabularies[slot]

    # Condition variants
    categories['Condition Variants'] = OrderedDict()
    variant_slots = [
        'CONDITION_HIGH_TOKENS',
        'CONDITION_LOW_TOKENS',
        'ADJECTIVAL_CONDITION_TOKENS',
        'CONDITION_ADJECTIVE_TOKENS',
    ]
    for slot in variant_slots:
        if slot in vocabularies:
            categories['Condition Variants'][slot] = vocabularies[slot]

    return categories

def export_to_json(categories, filepath):
    """Export to JSON format."""

    output = {
        'metadata': {
            'source': 'analyze_compositionality.py',
            'description': 'Slot vocabularies for ICD-10-CM compositional analysis',
            'total_slots': sum(len(cat) for cat in categories.values()),
            'total_tokens': sum(len(tokens) for cat in categories.values()
                               for tokens in cat.values())
        },
        'categories': categories
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return output

def export_to_markdown(categories, filepath):
    """Export to hierarchical markdown format."""

    lines = []
    lines.append('# Slot Vocabularies - Hierarchical Export')
    lines.append('')
    lines.append('**Source**: analyze_compositionality.py')
    lines.append('**Date**: 2026-03-25')
    lines.append('')

    # Calculate statistics
    total_slots = sum(len(cat) for cat in categories.values())
    total_tokens = sum(len(tokens) for cat in categories.values()
                      for tokens in cat.values())

    lines.append(f'**Total Slots**: {total_slots}')
    lines.append(f'**Total Vocabulary Terms**: {total_tokens:,}')
    lines.append('')
    lines.append('---')
    lines.append('')

    for category_name, slots in categories.items():
        lines.append(f'## {category_name}')
        lines.append('')

        category_total = sum(len(tokens) for tokens in slots.values())
        lines.append(f'*Total tokens in category: {category_total:,}*')
        lines.append('')

        for slot_name, tokens in slots.items():
            # Clean up slot name for display
            display_name = slot_name.replace('_TOKENS', '').replace('_', ' ').title()

            lines.append(f'### {display_name}')
            lines.append('')
            lines.append(f'**Slot**: `{slot_name}`')
            lines.append(f'**Count**: {len(tokens)} terms')
            lines.append('')

            if tokens:
                # Group tokens for better readability (5 per line)
                lines.append('**Vocabulary**:')
                lines.append('```')
                for i in range(0, len(tokens), 5):
                    chunk = tokens[i:i+5]
                    lines.append('  ' + ', '.join(chunk))
                lines.append('```')
            else:
                lines.append('*Empty slot*')

            lines.append('')

        lines.append('---')
        lines.append('')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def main():
    print("Extracting vocabularies from analyze_compositionality.py...")
    vocabularies = extract_vocabularies_from_file()

    print(f"Found {len(vocabularies)} slot vocabularies")
    print()

    # Categorize
    print("Organizing into hierarchical categories...")
    categories = categorize_slots(vocabularies)

    print(f"Organized into {len(categories)} categories")
    print()

    # Export to JSON
    print("Exporting to JSON...")
    output = export_to_json(categories, 'slot_vocabularies.json')
    print(f"✓ Exported to: slot_vocabularies.json")
    print(f"  Total slots: {output['metadata']['total_slots']}")
    print(f"  Total tokens: {output['metadata']['total_tokens']:,}")
    print()

    # Export to Markdown
    print("Exporting to Markdown...")
    export_to_markdown(categories, 'SLOT_VOCABULARIES.md')
    print(f"✓ Exported to: SLOT_VOCABULARIES.md")
    print()

    # Print summary
    print("=" * 80)
    print("VOCABULARY EXPORT SUMMARY")
    print("=" * 80)
    print()

    for category_name, slots in categories.items():
        category_total = sum(len(tokens) for tokens in slots.values())
        print(f"{category_name}:")
        print(f"  Slots: {len(slots)}")
        print(f"  Tokens: {category_total:,}")
        print()

if __name__ == '__main__':
    main()

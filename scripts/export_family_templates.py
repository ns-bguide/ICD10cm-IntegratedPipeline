#!/usr/bin/env python3
"""
Export family templates with their slot compositions in a structured format.
"""

import re
import json
from collections import OrderedDict

def extract_family_templates():
    """Extract family template definitions from analyze_compositionality.py."""

    with open('analyze_compositionality.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find TEMPLATE_FAMILY_SPECS definition
    pattern = r'TEMPLATE_FAMILY_SPECS\s*=\s*\{'
    match = re.search(pattern, content)

    if not match:
        print("Could not find TEMPLATE_FAMILY_SPECS")
        return {}

    # Find the full dictionary by tracking braces
    start_pos = match.end() - 1  # Position of opening brace
    brace_count = 0
    in_string = False
    escape_next = False

    for i in range(start_pos, len(content)):
        char = content[i]

        if escape_next:
            escape_next = False
            continue

        if char == '\\':
            escape_next = True
            continue

        if char in ('"', "'"):
            in_string = not in_string
            continue

        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    families_str = content[start_pos+1:i]
                    break
    else:
        print("Could not parse TEMPLATE_FAMILY_SPECS")
        return {}

    # Parse family definitions
    # Pattern: "family_name": [("slot1", SLOT1_TOKENS), ("slot2", SLOT2_TOKENS), ...],
    family_pattern = r'"([^"]+)":\s*\[([^\]]+)\]'
    family_matches = re.findall(family_pattern, families_str)

    families = OrderedDict()

    for family_name, slots_str in family_matches:
        # Extract slot definitions
        slot_pattern = r'\("([^"]+)",\s*([A-Z_]+TOKENS)\)'
        slot_matches = re.findall(slot_pattern, slots_str)

        slots = []
        for slot_name, token_set in slot_matches:
            slots.append({
                'slot_name': slot_name,
                'vocabulary': token_set
            })

        families[family_name] = {
            'slots': slots,
            'slot_count': len(slots),
            'slot_names': [s['slot_name'] for s in slots],
            'vocabularies': [s['vocabulary'] for s in slots]
        }

    return families

def categorize_families(families):
    """Organize families by type/domain."""

    categories = OrderedDict()

    # Injury/fracture families
    categories['Injury & Fracture Families'] = OrderedDict()
    for name, details in families.items():
        if 'injury' in name or 'fracture' in name:
            categories['Injury & Fracture Families'][name] = details

    # Toxic/poisoning families
    categories['Toxic & Poisoning Families'] = OrderedDict()
    for name, details in families.items():
        if 'toxic' in name or 'poison' in name:
            categories['Toxic & Poisoning Families'][name] = details

    # Condition families
    categories['Condition Families'] = OrderedDict()
    for name, details in families.items():
        if 'condition' in name and name not in categories['Toxic & Poisoning Families']:
            categories['Condition Families'][name] = details

    # Mechanism/external cause families
    categories['Mechanism & External Cause Families'] = OrderedDict()
    for name, details in families.items():
        if 'mechanism' in name:
            categories['Mechanism & External Cause Families'][name] = details

    # Encounter families
    categories['Encounter-Based Families'] = OrderedDict()
    for name, details in families.items():
        if 'encounter' in name and name not in categories['Injury & Fracture Families'] \
           and name not in categories['Toxic & Poisoning Families'] \
           and name not in categories['Mechanism & External Cause Families']:
            categories['Encounter-Based Families'][name] = details

    # Auto-generated families
    categories['Auto-Generated Families'] = OrderedDict()
    for name, details in families.items():
        if name.startswith('auto_'):
            categories['Auto-Generated Families'][name] = details

    # Miscellaneous
    categories['Other Families'] = OrderedDict()
    for name, details in families.items():
        # Add if not already in any category
        found = False
        for cat_families in categories.values():
            if name in cat_families:
                found = True
                break
        if not found:
            categories['Other Families'][name] = details

    # Remove empty categories
    return OrderedDict((k, v) for k, v in categories.items() if v)

def export_templates_json(families, filepath):
    """Export templates to JSON."""

    output = {
        'metadata': {
            'source': 'analyze_compositionality.py',
            'description': 'Family template definitions for ICD-10-CM compositional analysis',
            'total_families': len(families),
            'slot_count_range': {
                'min': min(f['slot_count'] for f in families.values()) if families else 0,
                'max': max(f['slot_count'] for f in families.values()) if families else 0,
                'avg': sum(f['slot_count'] for f in families.values()) / len(families) if families else 0
            }
        },
        'families': families
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return output

def export_templates_markdown(categories, filepath):
    """Export templates to markdown."""

    lines = []
    lines.append('# Family Templates - Hierarchical Export')
    lines.append('')
    lines.append('**Source**: analyze_compositionality.py')
    lines.append('**Date**: 2026-03-25')
    lines.append('')

    # Calculate statistics
    total_families = sum(len(cat) for cat in categories.values())

    lines.append(f'**Total Families**: {total_families}')
    lines.append('')

    # Slot count distribution
    all_families = {}
    for cat in categories.values():
        all_families.update(cat)

    slot_counts = {}
    for family in all_families.values():
        count = family['slot_count']
        slot_counts[count] = slot_counts.get(count, 0) + 1

    lines.append('**Slot Count Distribution**:')
    for count in sorted(slot_counts.keys()):
        lines.append(f'- {count}-slot families: {slot_counts[count]}')
    lines.append('')
    lines.append('---')
    lines.append('')

    for category_name, families in categories.items():
        lines.append(f'## {category_name}')
        lines.append('')
        lines.append(f'*Total families in category: {len(families)}*')
        lines.append('')

        for family_name, details in families.items():
            lines.append(f'### {family_name}')
            lines.append('')
            lines.append(f'**Slot Count**: {details["slot_count"]}')
            lines.append('')
            lines.append('**Slot Composition**:')
            lines.append('')

            for i, slot in enumerate(details['slots'], 1):
                lines.append(f'{i}. **{slot["slot_name"]}** → `{slot["vocabulary"]}`')

            lines.append('')
            lines.append('**Template Pattern**:')
            lines.append('```')
            pattern = ' × '.join(details['slot_names'])
            lines.append(pattern)
            lines.append('```')
            lines.append('')

        lines.append('---')
        lines.append('')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def export_combined_reference(families_json, vocabs_json, filepath):
    """Export a combined reference that links families to vocabularies."""

    with open(vocabs_json, 'r', encoding='utf-8') as f:
        vocabularies = json.load(f)

    # Create a flat vocabulary lookup
    vocab_lookup = {}
    for category in vocabularies['categories'].values():
        for slot_name, tokens in category.items():
            vocab_lookup[slot_name] = {
                'count': len(tokens),
                'tokens': tokens[:10],  # First 10 for preview
                'total': len(tokens)
            }

    # Enhance families with vocabulary info
    combined = {
        'metadata': {
            'description': 'Combined family templates with vocabulary references',
            'total_families': len(families_json),
            'total_vocabularies': len(vocab_lookup),
        },
        'families': {}
    }

    for family_name, family_details in families_json.items():
        enhanced_slots = []

        for slot in family_details['slots']:
            vocab_name = slot['vocabulary']
            vocab_info = vocab_lookup.get(vocab_name, {'count': 0, 'tokens': [], 'total': 0})

            enhanced_slots.append({
                'slot_name': slot['slot_name'],
                'vocabulary_name': vocab_name,
                'vocabulary_size': vocab_info['total'],
                'sample_tokens': vocab_info['tokens']
            })

        # Calculate complexity score (product of vocabulary sizes)
        complexity = 1
        for slot in enhanced_slots:
            complexity *= max(1, slot['vocabulary_size'])

        combined['families'][family_name] = {
            'slots': enhanced_slots,
            'slot_count': family_details['slot_count'],
            'complexity_score': complexity,
            'template_pattern': ' × '.join(family_details['slot_names'])
        }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)

    return combined

def main():
    print("Extracting family templates from analyze_compositionality.py...")
    families = extract_family_templates()

    print(f"Found {len(families)} family templates")
    print()

    # Categorize
    print("Organizing into categories...")
    categories = categorize_families(families)

    print(f"Organized into {len(categories)} categories")
    print()

    # Export to JSON
    print("Exporting templates to JSON...")
    output = export_templates_json(families, 'family_templates.json')
    print(f"✓ Exported to: family_templates.json")
    print(f"  Total families: {output['metadata']['total_families']}")
    print(f"  Slot range: {output['metadata']['slot_count_range']['min']}-{output['metadata']['slot_count_range']['max']}")
    print()

    # Export to Markdown
    print("Exporting templates to Markdown...")
    export_templates_markdown(categories, 'FAMILY_TEMPLATES.md')
    print(f"✓ Exported to: FAMILY_TEMPLATES.md")
    print()

    # Export combined reference
    print("Creating combined vocabulary-template reference...")
    combined = export_combined_reference(families, 'slot_vocabularies.json', 'VOCABULARY_TEMPLATE_REFERENCE.json')
    print(f"✓ Exported to: VOCABULARY_TEMPLATE_REFERENCE.json")
    print()

    # Print summary
    print("=" * 80)
    print("FAMILY TEMPLATE EXPORT SUMMARY")
    print("=" * 80)
    print()

    for category_name, cat_families in categories.items():
        print(f"{category_name}:")
        print(f"  Families: {len(cat_families)}")

        # Slot count distribution in this category
        slot_dist = {}
        for family in cat_families.values():
            count = family['slot_count']
            slot_dist[count] = slot_dist.get(count, 0) + 1

        print(f"  Slot distribution: {dict(sorted(slot_dist.items()))}")
        print()

if __name__ == '__main__':
    main()

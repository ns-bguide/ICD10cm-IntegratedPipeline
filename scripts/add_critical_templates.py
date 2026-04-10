#!/usr/bin/env python3
"""
Add Critical Template Families for Unmatched Terms

Creates template families to capture common 2-word unmatched patterns:
1. anatomy_adjective_x_condition (e.g., "nasopharyngeal diphtheria")
2. condition_x_condition (e.g., "arthritis gonococcal")
3. organism_x_condition (e.g., "anthrax sepsis")
"""

import json
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_FILE = BASE_DIR / "reference_data" / "family_templates.json"
OUTPUT_FILE = BASE_DIR / "reference_data" / "family_templates.json"
BACKUP_FILE = BASE_DIR / "reference_data" / "family_templates.json.backup"

# New template families to add
NEW_TEMPLATES = {
    "anatomy_adjective_x_condition": {
        "pattern": "{ANATOMY_ADJECTIVE_TOKENS} {CONDITION_TOKENS}",
        "description": "Anatomical adjective + condition (e.g., nasopharyngeal diphtheria, cutaneous listeriosis)",
        "examples": ["nasopharyngeal diphtheria", "gastrointestinal tularemia", "cutaneous listeriosis"],
        "priority": "high",
        "rationale": "Common in 2-word unmatched terms (27.4% of unmatched)"
    },
    "condition_x_condition_high": {
        "pattern": "{CONDITION_TOKENS} {CONDITION_HIGH_TOKENS}",
        "description": "Specific condition + general condition category (e.g., arthritis gonococcal)",
        "examples": ["arthritis gonococcal", "peritonitis gonococcal", "paralytic dementia"],
        "priority": "high",
        "rationale": "Captures condition + organism-derived condition patterns"
    },
}


def load_templates():
    """Load current template families."""
    with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def add_template_family(templates, family_name, family_spec):
    """Add a new template family."""
    if family_name in templates:
        print(f"  ⚠ {family_name} already exists, skipping")
        return templates, False

    # Convert our spec format to the format used in family_templates.json
    # The actual format depends on how templates are structured in that file
    templates[family_name] = {
        "pattern": family_spec["pattern"],
        "description": family_spec["description"],
        "examples": family_spec["examples"],
        "priority": family_spec["priority"],
        "rationale": family_spec["rationale"]
    }
    print(f"  ✓ Added {family_name}")
    return templates, True


def save_templates(templates):
    """Save updated templates."""
    import shutil
    shutil.copy(TEMPLATES_FILE, BACKUP_FILE)
    print(f"\n✓ Backup saved: {BACKUP_FILE.name}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(templates, f, indent=2, ensure_ascii=False)
    print(f"✓ Updated templates saved: {OUTPUT_FILE.name}")


def main():
    print("=" * 80)
    print("ADDING CRITICAL TEMPLATE FAMILIES")
    print("=" * 80)
    print()

    print("Loading current templates...")
    templates = load_templates()
    print(f"  ✓ Loaded {len(templates)} template families")

    print("\nAdding new template families...")
    added_count = 0
    for family_name, family_spec in NEW_TEMPLATES.items():
        templates, added = add_template_family(templates, family_name, family_spec)
        if added:
            added_count += 1

    if added_count == 0:
        print("\n⚠ No templates were added (all already exist)")
        return

    print(f"\nSaving {added_count} new templates...")
    save_templates(templates)

    print("\n" + "=" * 80)
    print("TEMPLATE FAMILIES ADDED")
    print("=" * 80)
    print(f"Added: {added_count} new families")
    print(f"Total: {len(templates)} families")
    print()
    print("Templates added:")
    for family_name, family_spec in NEW_TEMPLATES.items():
        print(f"\n  {family_name}:")
        print(f"    Pattern: {family_spec['pattern']}")
        print(f"    Examples: {', '.join(family_spec['examples'][:2])}")
    print()
    print("⚠ IMPORTANT: This adds templates to the integrated pipeline.")
    print("   You need to manually add these to the main analyzer's templates.")
    print()
    print("Next:")
    print("1. Copy these template definitions to the main analyzer's template system")
    print("2. Re-run the analyzer to measure impact")
    print()


if __name__ == "__main__":
    main()

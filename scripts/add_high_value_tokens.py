#!/usr/bin/env python3
"""
Add High-Value Tokens to Vocabularies

Based on unmatched terms analysis, adds tokens with highest frequency
and clear medical relevance to appropriate vocabulary slots.

Focus: Medical terms (not abbreviations or stopwords) with frequency >100
"""

import json
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
VOCABS_FILE = BASE_DIR / "reference_data" / "slot_vocabularies.json"
OUTPUT_FILE = BASE_DIR / "reference_data" / "slot_vocabularies.json"
BACKUP_FILE = BASE_DIR / "reference_data" / "slot_vocabularies.json.backup"

# High-value tokens to add (from unmatched analysis)
TOKEN_ADDITIONS = {
    "CONDITION_TOKENS": [
        "gout",           # 1,404 occurrences
        "osteoporosis",   # 571 (appeared as "osteopor")
        "diabetes",       # 422 (appeared as "diab")
        "dementia",       # 115
        "hemiplegia",     # 115
        "thalassemia",    # 114
        "malaria",        # 103
        "mellitus",       # 162 (as in "diabetes mellitus")
        "hodgkin",        # 220 (Hodgkin lymphoma)
    ],
    "ANATOMY_TOKENS": [
        "tophus",         # 1,313 (gout deposits)
        "tophi",          # 242 (plural of tophus)
        "meniscus",       # 189 (knee cartilage)
        "adnexa",         # 217 (eye/uterine structures)
        "organ",          # 273
        "tissue",         # 193
        "vein",           # 167 (appeared as "veins")
    ],
    "QUALIFIER_TOKENS": [
        "renal",          # 405
        "diabetic",       # 171
        "macular",        # 297
        "lymphocytic",    # 173
        "postprocedural", # 157
        "paralytic",      # 105
        "mental",         # 101
        "physiological",  # 153
        "magnetic",       # 159
    ],
    "MODIFIER_WITH_TOKENS": [
        "pressure",       # 378 (pressure ulcer)
        "psychoactive",   # 306 (psychoactive substance)
        "foreign",        # 241 (foreign body)
        "bypass",         # 249
        "retained",       # 365 (retained foreign body)
        "lead",           # 244 (lead poisoning)
        "solid",          # 191 (solid organ)
    ],
}


def load_vocabularies():
    """Load current vocabularies."""
    with open(VOCABS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def add_tokens_to_vocabulary(vocabs, slot_name, tokens):
    """Add tokens to specified slot, avoiding duplicates."""
    # Find the slot in categories
    found = False
    for category, slots in vocabs['categories'].items():
        if slot_name in slots:
            existing = set(t.lower() for t in slots[slot_name])
            added_count = 0

            for token in tokens:
                if token.lower() not in existing:
                    slots[slot_name].append(token)
                    added_count += 1

            found = True
            print(f"  ✓ {slot_name}: added {added_count} tokens (skipped {len(tokens) - added_count} duplicates)")
            break

    if not found:
        print(f"  ✗ {slot_name}: slot not found in vocabularies")

    return vocabs


def update_metadata(vocabs):
    """Update version and metadata."""
    if 'metadata' not in vocabs:
        vocabs['metadata'] = {}

    vocabs['metadata']['version'] = '2026-03-27-v3'
    vocabs['metadata']['last_updated'] = '2026-03-27'

    if 'changes' not in vocabs['metadata']:
        vocabs['metadata']['changes'] = []

    vocabs['metadata']['changes'].append({
        'date': '2026-03-27',
        'version': 'v3',
        'description': 'Added high-value tokens from unmatched terms analysis',
        'details': {
            'CONDITION_TOKENS': f'+{len(TOKEN_ADDITIONS["CONDITION_TOKENS"])} tokens',
            'ANATOMY_TOKENS': f'+{len(TOKEN_ADDITIONS["ANATOMY_TOKENS"])} tokens',
            'QUALIFIER_TOKENS': f'+{len(TOKEN_ADDITIONS["QUALIFIER_TOKENS"])} tokens',
            'MODIFIER_WITH_TOKENS': f'+{len(TOKEN_ADDITIONS["MODIFIER_WITH_TOKENS"])} tokens',
        }
    })

    return vocabs


def save_vocabularies(vocabs):
    """Save updated vocabularies."""
    # Create backup
    import shutil
    shutil.copy(VOCABS_FILE, BACKUP_FILE)
    print(f"\n✓ Backup saved: {BACKUP_FILE.name}")

    # Save updated version
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(vocabs, f, indent=2, ensure_ascii=False)
    print(f"✓ Updated vocabularies saved: {OUTPUT_FILE.name}")


def main():
    print("=" * 80)
    print("ADDING HIGH-VALUE TOKENS TO VOCABULARIES")
    print("=" * 80)
    print()

    print("Loading vocabularies...")
    vocabs = load_vocabularies()
    print(f"  ✓ Loaded {len(vocabs['categories'])} categories")

    print("\nAdding tokens to slots...")
    for slot_name, tokens in TOKEN_ADDITIONS.items():
        add_tokens_to_vocabulary(vocabs, slot_name, tokens)

    print("\nUpdating metadata...")
    vocabs = update_metadata(vocabs)
    print("  ✓ Version updated to 2026-03-27-v3")

    print("\nSaving updated vocabularies...")
    save_vocabularies(vocabs)

    # Count totals
    total_tokens = 0
    total_slots = 0
    for category, slots in vocabs['categories'].items():
        for slot_name, tokens in slots.items():
            total_slots += 1
            total_tokens += len(tokens)

    print("\n" + "=" * 80)
    print("VOCABULARY UPDATE COMPLETE")
    print("=" * 80)
    print(f"Total slots: {total_slots}")
    print(f"Total tokens: {total_tokens:,}")
    print()
    print("Next steps:")
    print("1. Test impact: cd /home/bguide/compositional_analysis && python3 analyze_compositionality.py")
    print("2. Compare coverage before (55.36%) vs after")
    print("3. If successful, iterate with more tokens")
    print()


if __name__ == "__main__":
    main()

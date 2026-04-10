#!/usr/bin/env python3
"""
Add Expanded Token Forms (Phase 1B)

Adds full-word expansions of abbreviated forms found in unmatched terms.
These are high-frequency terms that appeared as abbreviations in the data.

Run after measuring v3 impact to continue coverage improvement.
"""

import json
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
VOCABS_FILE = BASE_DIR / "reference_data" / "slot_vocabularies.json"
OUTPUT_FILE = BASE_DIR / "reference_data" / "slot_vocabularies.json"
BACKUP_FILE = BASE_DIR / "reference_data" / "slot_vocabularies.json.backup-v3"

# Expanded forms of abbreviations found in unmatched terms
TOKEN_ADDITIONS = {
    "CONDITION_TOKENS": [
        "atherosclerosis",  # 224 freq (appeared as "athscl")
        "infarction",       # 203 freq (appeared as "infrc")
        "retinopathy",      # 283 freq (appeared as "rtnop")
        "hemorrhage",       # 172 freq (appeared as "hemor")
        "ulcer",            # 149 freq (appeared as "ulc")
    ],
    "ANATOMY_TOKENS": [
        "extremity",        # 229 freq (appeared as "extrm")
    ],
    "QUALIFIER_TOKENS": [
        "proliferative",    # 166 freq (appeared as "prolif")
        "chronic",          # 166 freq (appeared as "chr")
    ],
}


def load_vocabularies():
    """Load current vocabularies."""
    with open(VOCABS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def add_tokens_to_vocabulary(vocabs, slot_name, tokens):
    """Add tokens to specified slot, avoiding duplicates."""
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

    vocabs['metadata']['version'] = '2026-03-27-v4'
    vocabs['metadata']['last_updated'] = '2026-03-27'

    if 'changes' not in vocabs['metadata']:
        vocabs['metadata']['changes'] = []

    vocabs['metadata']['changes'].append({
        'date': '2026-03-27',
        'version': 'v4',
        'description': 'Added expanded forms of abbreviated tokens (Phase 1B)',
        'details': {
            'CONDITION_TOKENS': f'+{len(TOKEN_ADDITIONS["CONDITION_TOKENS"])} tokens (full forms)',
            'ANATOMY_TOKENS': f'+{len(TOKEN_ADDITIONS["ANATOMY_TOKENS"])} tokens (full forms)',
            'QUALIFIER_TOKENS': f'+{len(TOKEN_ADDITIONS["QUALIFIER_TOKENS"])} tokens (full forms)',
        }
    })

    return vocabs


def save_vocabularies(vocabs):
    """Save updated vocabularies."""
    import shutil
    shutil.copy(VOCABS_FILE, BACKUP_FILE)
    print(f"\n✓ Backup saved: {BACKUP_FILE.name}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(vocabs, f, indent=2, ensure_ascii=False)
    print(f"✓ Updated vocabularies saved: {OUTPUT_FILE.name}")


def main():
    print("=" * 80)
    print("ADDING EXPANDED TOKEN FORMS (PHASE 1B)")
    print("=" * 80)
    print()

    print("Loading vocabularies...")
    vocabs = load_vocabularies()
    current_version = vocabs.get('metadata', {}).get('version', 'unknown')
    print(f"  ✓ Current version: {current_version}")

    print("\nAdding expanded token forms...")
    total_added = 0
    for slot_name, tokens in TOKEN_ADDITIONS.items():
        add_tokens_to_vocabulary(vocabs, slot_name, tokens)
        total_added += len(tokens)

    print("\nUpdating metadata...")
    vocabs = update_metadata(vocabs)
    print("  ✓ Version updated to 2026-03-27-v4")

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
    print("EXPANDED TOKENS ADDED SUCCESSFULLY")
    print("=" * 80)
    print(f"Total tokens added: {total_added}")
    print(f"Total slots: {total_slots}")
    print(f"Total tokens: {total_tokens:,}")
    print()
    print("Tokens added:")
    for slot_name, tokens in TOKEN_ADDITIONS.items():
        print(f"  {slot_name}:")
        for token in tokens:
            print(f"    - {token}")
    print()
    print("Next: Test impact and compare with v3 coverage")
    print()


if __name__ == "__main__":
    main()

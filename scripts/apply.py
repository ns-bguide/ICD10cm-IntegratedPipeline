#!/usr/bin/env python3
"""
Vocabulary & Template Validation Pipeline — Step 3: Apply

Reads a changeset from suggest.py and applies actionable changes to
the production vocabulary and template files.

Features:
- --dry-run mode (default): shows what would change without modifying files
- Timestamped backups before mutation
- Pre-flight and post-flight structural validation
- Automatic rollback if post-flight fails
- Idempotent: skips already-applied changes

Usage:
    python3 scripts/apply.py              # dry-run (default)
    python3 scripts/apply.py --apply      # actually apply changes
"""

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
VOCAB_FILE = BASE_DIR / "reference_data" / "slot_vocabularies.json"
TEMPLATES_FILE = BASE_DIR / "reference_data" / "family_templates.json"
CHANGESET_FILE = BASE_DIR / "analysis_outputs" / "changeset.json"


# ---------------------------------------------------------------------------
# Structural validation (lightweight — just the critical checks)
# ---------------------------------------------------------------------------
def structural_check(vocab_data, tpl_data):
    """Return list of critical issues. Empty list = pass."""
    issues = []
    vocabs = {}
    for _cat, slots in vocab_data["categories"].items():
        for name, tokens in slots.items():
            vocabs[name] = tokens

    # Check template -> vocab refs
    for fam_name, fam in tpl_data["families"].items():
        for slot in fam["slots"]:
            if slot["vocabulary"] not in vocabs:
                issues.append(f"Broken ref: template '{fam_name}' -> vocab '{slot['vocabulary']}'")

    # Check for intra-vocab duplicates
    for v_name, tokens in vocabs.items():
        if len(tokens) != len(set(tokens)):
            issues.append(f"Duplicate tokens in '{v_name}'")

    return issues, vocabs


def update_metadata(vocab_data, vocabs):
    """Recalculate and update metadata counts."""
    vocab_data["metadata"]["total_slots"] = len(vocabs)
    vocab_data["metadata"]["total_tokens"] = sum(len(t) for t in vocabs.values())


def update_template_metadata(tpl_data):
    """Recalculate template metadata counts."""
    tpl_data["metadata"]["total_families"] = len(tpl_data["families"])


# ---------------------------------------------------------------------------
# Change applicators
# ---------------------------------------------------------------------------
def apply_remove_token(vocab_data, change):
    """Remove a token from a vocabulary. Returns (applied, message)."""
    vocab_name = change["vocabulary"]
    token = change["token"]

    for _cat, slots in vocab_data["categories"].items():
        if vocab_name in slots:
            if token in slots[vocab_name]:
                slots[vocab_name].remove(token)
                return True, f"Removed '{token}' from {vocab_name}"
            else:
                return False, f"SKIP: '{token}' not in {vocab_name} (already removed?)"
    return False, f"SKIP: Vocabulary '{vocab_name}' not found"


def apply_remove_duplicate(vocab_data, change):
    """Deduplicate a token in a vocabulary. Returns (applied, message)."""
    vocab_name = change["vocabulary"]
    token = change["token"]

    for _cat, slots in vocab_data["categories"].items():
        if vocab_name in slots:
            tokens = slots[vocab_name]
            count = tokens.count(token)
            if count > 1:
                while tokens.count(token) > 1:
                    tokens.remove(token)
                return True, f"Deduped '{token}' in {vocab_name} ({count} -> 1)"
            else:
                return False, f"SKIP: '{token}' not duplicated in {vocab_name}"
    return False, f"SKIP: Vocabulary '{vocab_name}' not found"


def apply_remove_template(tpl_data, change):
    """Remove a template family. Returns (applied, message)."""
    template = change["template"]
    if template in tpl_data["families"]:
        del tpl_data["families"][template]
        return True, f"Removed template '{template}'"
    return False, f"SKIP: Template '{template}' not found (already removed?)"


def apply_add_template(tpl_data, change):
    """Add a template family. Returns (applied, message)."""
    template = change["template"]
    if template in tpl_data["families"]:
        return False, f"SKIP: Template '{template}' already exists"
    slots = change["slots"]  # list of {"slot_name": ..., "vocabulary": ...}
    tpl_data["families"][template] = {
        "slots": slots,
        "slot_count": len(slots),
        "slot_names": [s["slot_name"] for s in slots],
        "vocabularies": [s["vocabulary"] for s in slots],
    }
    return True, f"Added template '{template}' ({len(slots)} slots)"


def apply_add_token(vocab_data, change):
    """Add a token to a vocabulary. Returns (applied, message)."""
    vocab_name = change["vocabulary"]
    token = change["token"]

    for _cat, slots in vocab_data["categories"].items():
        if vocab_name in slots:
            if token in slots[vocab_name]:
                return False, f"SKIP: '{token}' already in {vocab_name}"
            slots[vocab_name].append(token)
            return True, f"Added '{token}' to {vocab_name}"
    return False, f"SKIP: Vocabulary '{vocab_name}' not found"


def apply_add_vocabulary(vocab_data, change):
    """Add a new vocabulary to a category. Returns (applied, message)."""
    vocab_name = change["vocabulary"]
    category = change["category"]
    tokens = change.get("tokens", [])

    # Check if already exists
    for _cat, slots in vocab_data["categories"].items():
        if vocab_name in slots:
            return False, f"SKIP: Vocabulary '{vocab_name}' already exists"

    # Add to specified category (create category if needed)
    if category not in vocab_data["categories"]:
        vocab_data["categories"][category] = {}
    vocab_data["categories"][category][vocab_name] = tokens
    return True, f"Added vocabulary '{vocab_name}' ({len(tokens)} tokens) to '{category}'"


def apply_fix_metadata(vocab_data, tpl_data, change):
    """Fix metadata counts. Returns (applied, message)."""
    # Metadata is recalculated after all changes, so this is a no-op marker
    return True, f"Metadata '{change['field']}' will be recalculated"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Apply changeset to production files")
    parser.add_argument("--apply", action="store_true",
                        help="Actually apply changes (default is dry-run)")
    args = parser.parse_args()
    dry_run = not args.apply

    if not CHANGESET_FILE.exists():
        print(f"ERROR: Changeset not found at {CHANGESET_FILE}")
        print("Run scripts/suggest.py first.")
        return 1

    with open(CHANGESET_FILE, encoding="utf-8") as f:
        changeset = json.load(f)

    with open(VOCAB_FILE, encoding="utf-8") as f:
        vocab_data = json.load(f)

    with open(TEMPLATES_FILE, encoding="utf-8") as f:
        tpl_data = json.load(f)

    changes = changeset["changes"]
    actionable = [c for c in changes if c["type"] != "advisory"]

    if not actionable:
        print("No actionable changes in changeset. Nothing to apply.")
        return 0

    mode = "DRY RUN" if dry_run else "APPLY"
    print(f"\n{'='*70}")
    print(f"  APPLY CHANGESET — {mode}")
    print(f"  Based on vocab version: {changeset['based_on_vocab_version']}")
    print(f"  Actionable changes: {len(actionable)}")
    print(f"{'='*70}\n")

    # Pre-flight structural check
    print("Pre-flight structural check...", end=" ")
    pre_issues, _ = structural_check(vocab_data, tpl_data)
    if pre_issues:
        print("FAIL")
        for issue in pre_issues:
            print(f"  ! {issue}")
        print("\nFix structural issues before applying changes.")
        return 1
    print("PASS")

    # Apply changes
    applied_count = 0
    skipped_count = 0
    results = []

    for change in actionable:
        ctype = change["type"]
        if ctype == "remove_token":
            ok, msg = apply_remove_token(vocab_data, change)
        elif ctype == "add_token":
            ok, msg = apply_add_token(vocab_data, change)
        elif ctype == "add_vocabulary":
            ok, msg = apply_add_vocabulary(vocab_data, change)
        elif ctype == "remove_duplicate":
            ok, msg = apply_remove_duplicate(vocab_data, change)
        elif ctype == "add_template":
            ok, msg = apply_add_template(tpl_data, change)
        elif ctype == "remove_template":
            ok, msg = apply_remove_template(tpl_data, change)
        elif ctype == "fix_metadata":
            ok, msg = apply_fix_metadata(vocab_data, tpl_data, change)
        else:
            ok, msg = False, f"SKIP: Unknown change type '{ctype}'"

        results.append({"applied": ok, "message": msg})
        if ok:
            applied_count += 1
        else:
            skipped_count += 1
        prefix = "  +" if ok else "  -"
        print(f"{prefix} {msg}")

    # Recalculate metadata
    vocabs = {}
    for _cat, slots in vocab_data["categories"].items():
        for name, tokens in slots.items():
            vocabs[name] = tokens
    update_metadata(vocab_data, vocabs)
    update_template_metadata(tpl_data)

    # Update version
    now = datetime.now(timezone.utc)
    old_version = vocab_data["metadata"].get("version", "unknown")
    new_version = now.strftime("%Y-%m-%d") + "-v1"
    if new_version.rsplit("-v", 1)[0] == old_version.rsplit("-v", 1)[0]:
        # Same date — increment version number
        try:
            old_v_num = int(old_version.rsplit("-v", 1)[1])
            new_version = old_version.rsplit("-v", 1)[0] + f"-v{old_v_num + 1}"
        except (ValueError, IndexError):
            pass
    vocab_data["metadata"]["version"] = new_version

    # Add changelog entry
    changelog_entry = {
        "version": new_version,
        "date": now.strftime("%Y-%m-%d"),
        "source": "apply.py",
        "changes": f"Applied {applied_count} changes from changeset ({skipped_count} skipped)",
    }
    vocab_data["metadata"].setdefault("changelog", []).append(changelog_entry)

    print(f"\n  Applied: {applied_count}  Skipped: {skipped_count}")
    print(f"  New version: {new_version}")
    print(f"  Tokens: {vocab_data['metadata']['total_tokens']}  Slots: {vocab_data['metadata']['total_slots']}")
    print(f"  Families: {tpl_data['metadata']['total_families']}")

    if dry_run:
        print(f"\n  DRY RUN — no files modified. Use --apply to write changes.\n")
        return 0

    # Post-flight structural check (on in-memory data)
    print("\nPost-flight structural check...", end=" ")
    post_issues, _ = structural_check(vocab_data, tpl_data)
    if post_issues:
        print("FAIL — aborting, no files written")
        for issue in post_issues:
            print(f"  ! {issue}")
        return 1
    print("PASS")

    # Create timestamped backups
    ts = now.strftime("%Y%m%d-%H%M%S")
    vocab_backup = VOCAB_FILE.with_suffix(f".json.backup-{ts}")
    tpl_backup = TEMPLATES_FILE.with_suffix(f".json.backup-{ts}")
    shutil.copy2(VOCAB_FILE, vocab_backup)
    shutil.copy2(TEMPLATES_FILE, tpl_backup)
    print(f"  Backups: {vocab_backup.name}, {tpl_backup.name}")

    # Write production files
    with open(VOCAB_FILE, "w", encoding="utf-8") as f:
        json.dump(vocab_data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(TEMPLATES_FILE, "w", encoding="utf-8") as f:
        json.dump(tpl_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Final verification — reload and check
    print("Final verification...", end=" ")
    with open(VOCAB_FILE, encoding="utf-8") as f:
        final_vocab = json.load(f)
    with open(TEMPLATES_FILE, encoding="utf-8") as f:
        final_tpl = json.load(f)
    final_issues, _ = structural_check(final_vocab, final_tpl)
    if final_issues:
        print("FAIL — rolling back!")
        shutil.copy2(vocab_backup, VOCAB_FILE)
        shutil.copy2(tpl_backup, TEMPLATES_FILE)
        print("  Rolled back to backup.")
        for issue in final_issues:
            print(f"  ! {issue}")
        return 1
    print("PASS")

    print(f"\n  Changes applied successfully. Version: {new_version}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

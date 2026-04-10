# Coverage Report: ICD-10-CM Generative Grammar

**Date**: 2026-04-10
**Vocab Version**: 2026-04-10-v8
**Grammar**: 39 vocabulary slots, 1,273 tokens, 90 template families

---

## 1. How It Works

The ICD-10-CM Integrated Pipeline produces a **generative grammar** for medical terms: two JSON structures whose cross-product defines a pattern space for DLP detection.

### Vocabularies (the lexicon)

A **vocabulary** is a named set of tokens that fill a single semantic role. Each token is a word or abbreviation that appears in ICD-10-CM terms.

```
ANATOMY_TOKENS (242 tokens):
  head, chest, femur, tibia, pelvis, wrist, shoulder, vertebra, ...

CONDITION_TOKENS (205 tokens):
  fracture, infection, hemorrhage, diabetes, pneumonia, stenosis, ...

ENCOUNTER_TOKENS (19 tokens):
  initial, subsequent, sequela, encounter, ...

LATERALITY_TOKENS (6 tokens):
  left, right, bilateral, midline, contralateral, ipsilateral
```

There are **39 vocabularies** organized in 5 categories:

| Category | Vocabs | Tokens | Purpose |
|---|---|---|---|
| Core Compositional Slots | 6 | 699 | Anatomy, conditions, injuries, encounters, qualifiers, severity |
| Anatomical Modifiers | 4 | 290 | Laterality, location, prefixes, adjectives |
| Clinical Detail & Classification | 12 | 237 | Disease state, classifiers, fracture details, healing, neoplasms, seizures, etc. |
| Specialized Domains | 16 | 287 | Toxic events, mechanisms, etiology, procedures, pathogens, substances, etc. |
| ICD Abbreviations | 1 | 60 | High-frequency ICD-10-CM abbreviations (clsn, physl, femr, etc.) |

### Templates (the production rules)

A **template** is an ordered combination of vocabulary slots. It defines which slot types can appear together in a valid medical term.

```
Template: anatomy_x_condition
  Slots: [ANATOMY_TOKENS, CONDITION_TOKENS]
  Example: "femur" + "fracture" → matches "fracture of femur"
  Cross-product: 242 x 205 = 49,610 possible combinations

Template: laterality_x_anatomy_x_condition
  Slots: [LATERALITY_TOKENS, ANATOMY_TOKENS, CONDITION_TOKENS]
  Example: "left" + "femur" + "fracture" → matches "fracture of left femur"
  Cross-product: 6 x 242 x 205 = 297,660 combinations

Template: injury_x_encounter
  Slots: [INJURY_TOKENS, ENCOUNTER_TOKENS]
  Example: "fracture" + "initial" → matches "initial encounter for fracture"
  Cross-product: 37 x 19 = 703 combinations
```

### Matching

A template **matches** an ICD-10-CM term when all slot tokens co-occur in that term. The grammar doesn't require exact word order or adjacency --- it checks that every token from every slot appears somewhere in the term. This captures the compositional structure of ICD-10-CM terms, which use consistent vocabulary but vary in word order and connecting words.

**Example**: ICD term "displaced fracture of shaft of left femur, initial encounter for closed fracture"
- Matches `anatomy_x_injury_x_encounter` with anatomy="femur", injury="fracture", encounter="initial"
- Also matches `laterality_x_anatomy_x_injury_x_encounter` with laterality="left", anatomy="femur", injury="fracture", encounter="initial"
- The connecting words ("of", "for", "closed") are not slot tokens --- they're structural glue

---

## 2. Current Coverage

### Overall

| Metric | Value |
|---|---|
| Total ICD-10-CM terms | 335,538 |
| Matched by grammar | 311,048 |
| **Coverage** | **92.70%** |
| Unmatched | 24,490 |

### Coverage by Template (top 20)

| Template | Matches | Slots |
|---|---|---|
| anatomy_x_condition | 189,496 | 2 |
| encounter_x_condition | 182,084 | 2 |
| injury_x_encounter | 167,761 | 2 |
| anatomy_x_encounter | 154,022 | 2 |
| anatomy_x_injury_x_encounter | 141,388 | 3 |
| qualifier_x_condition | 137,491 | 2 |
| anatomy_x_qualifier | 119,134 | 2 |
| anatomy_x_laterality_x_condition | 105,648 | 3 |
| qualifier_x_anatomy_x_condition | 103,845 | 3 |
| condition_x_diagnostic_classifier | 91,892 | 2 |
| anatomy_x_laterality_x_injury_x_encounter | 89,555 | 4 |
| encounter_x_qualifier_x_injury | 87,261 | 3 |
| anatomy_x_diagnostic_classifier_x_injury | 77,547 | 3 |
| qualifier_x_anatomy_x_injury_x_encounter | 74,616 | 4 |
| diagnostic_classifier_x_anatomy_x_injury_x_encounter | 72,695 | 4 |
| icd_abbreviation_x_encounter | 66,170 | 2 |
| diagnostic_classifier_x_qualifier | 61,920 | 2 |
| encounter_x_injury_x_fracture_detail | 60,788 | 3 |
| anatomy_x_injury_x_fracture_detail_x_encounter | 59,145 | 4 |
| anatomy_x_laterality_x_qualifier | 47,780 | 3 |

The top 5 templates cover ~80% of all matched terms. The 2-slot templates are the workhorses, with new templates like `anatomy_x_encounter` and `condition_x_diagnostic_classifier` adding significant coverage.

### Ground-Truth Hit Rates by Slot Count

"Hit rate" = fraction of token combinations that co-occur in at least one ICD term.

| Slot Count | Templates | Avg Hit Rate | Best Template |
|---|---|---|---|
| 2-slot | 35 | 13.3% | injury_x_encounter (58.3%) |
| 3-slot | 28 | 3.0% | toxic_event_x_intent_x_encounter (18.9%) |
| 4-slot | 15 | 0.6% | toxic_event_x_agent_x_intent_x_encounter (4.4%) |
| 5-slot | 6 | 0.0% | laterality_x_anatomy_x_injury_x_fracture_detail (0.2%) |
| 6+ slot | 6 | 0.0% | --- |

Higher-arity templates have exponentially larger cross-products but most combinations don't correspond to real terms. This is expected --- the grammar is designed for **recall** (covering real terms) not for every combination to be a real term.

### Precision & DLP Safety

| Metric | Value |
|---|---|
| High-specificity tokens (medical-only words) | 1,169 (91.8%) |
| Medium-specificity tokens | 28 (2.2%) |
| Low-specificity tokens (common English) | 76 (6.0%) |
| HIGH FP-risk templates | **0** |
| MEDIUM FP-risk templates | 21 |
| LOW FP-risk templates | 69 |

No template has a high probability of generating patterns composed entirely of common English words. The grammar is safe for DLP --- false positives from common-word patterns are minimal.

---

## 3. Gap Analysis

### What's Remaining

The 24,490 unmatched terms (7.3% of total) consist of:

| Category | Estimated Count | Description |
|---|---|---|
| Named diseases & syndromes | ~5,000 | Wilson disease, Kawasaki syndrome, etc. — proper nouns not in vocab |
| Heavily abbreviated terms | ~8,000 | Terms with rare ICD abbreviations beyond the top 60 |
| Rare/specialized vocabulary | ~6,000 | Specialized pathology, genetics, rare anatomical terms |
| Single-word or no-vocab terms | ~5,490 | Terms with 0-1 known tokens, requiring domain-specific vocabs |

### What Was Addressed (Phase 6)

The following gaps were closed, improving coverage from 84.37% to 92.70%:

1. **ICD Abbreviation Vocabulary** (+60 tokens): Added `ICD_ABBREVIATION_TOKENS` with high-frequency abbreviations (clsn, physl, femr, displ, etc.) — each appearing in 1,500-16,000 ICD terms
2. **Orphaned Vocab Templates** (+24 templates): Wired 14 previously orphaned vocabularies (148 tokens) into templates — pathogen_x_condition, neoplasm_x_anatomy, seizure_x_condition, etc.
3. **Missing Template Combinations** (+12 templates): Added top missing combos — encounter_x_mechanism, anatomy_x_qualifier, condition_x_diagnostic_classifier, etc.
4. **FP Risk Cleanup**: Removed 2 HIGH FP-risk templates (anatomy_x_laterality, ulcer_x_anatomy) — cost only 0.93% coverage

### Remaining Opportunities

| Opportunity | Estimated Impact | Complexity |
|---|---|---|
| Additional ICD abbreviations (~100 more rare abbrevs) | +1-2% | Low |
| Named disease vocabulary | +0.5-1% | Medium (risk of overfitting) |
| Anatomical sub-specialties (muscles, vessels, nerves) | +0.5-1% | Low |
| Transport/external cause expansion | +0.5% | Low |
| Theoretical ceiling | ~95-96% | — |

---

## 4. Coverage History

| Version | Coverage | Terms Matched | Templates | Tokens | Key Change |
|---|---|---|---|---|---|
| v1 (baseline) | 84.37% | 283,081 | 56 | 1,018 | Initial pipeline validation |
| v5 (pre-expansion) | 84.37% | 283,081 | 56 | 1,213 | Collision fixes + reconciliation |
| v6 (+abbreviations) | ~86% | ~288,000 | 56 | 1,273 | Added ICD_ABBREVIATION_TOKENS (60 tokens) |
| v7 (+36 templates) | 93.63% | 314,171 | 92 | 1,273 | Added 36 new templates (orphaned vocabs + missing combos) |
| **v8 (current)** | **92.70%** | **311,048** | **90** | **1,273** | Removed 2 HIGH FP-risk templates |

### Path to 95%

| Opportunity | Estimated Impact | Risk |
|---|---|---|
| Additional ICD abbreviations | +1-2% | Low |
| Anatomical sub-specialties | +0.5-1% | Low |
| Named disease vocabulary | +0.5-1% | Medium (FP risk) |
| Theoretical ceiling | ~95-96% | — |

The remaining ~7% consists of named diseases (Wilson disease, Kawasaki syndrome), heavily abbreviated codes, and terms requiring specialized vocabulary that would increase FP risk.

---

## 5. Pipeline Tools

| Script | Purpose | Output |
|---|---|---|
| `scripts/validate.py` | Structural + ground-truth validation | `validation_report.json` |
| `scripts/suggest.py` | Gap analysis, proposes changesets | `changeset.json` |
| `scripts/apply.py` | Safe changeset application (--dry-run default) | Modified production files |
| `scripts/precision.py` | Token specificity + FP risk scoring | `precision_report.json` |
| `scripts/reconcile.py` | JSON vs analyzer Python diff | `reconciliation_report.json` |

All scripts are stdlib-only Python, read-only by default, and output machine-readable JSON + human summary to stdout.

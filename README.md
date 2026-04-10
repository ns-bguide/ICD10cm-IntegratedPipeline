# ICD-10-CM Integrated Pipeline

A generative grammar for ICD-10-CM medical terminology, producing two data products for DLP pattern detection: **slot vocabularies** (the lexicon) and **template families** (the production rules).

## How It Works

The pipeline builds a **compositional grammar** whose cross-product defines a pattern space for detecting medical terms in text.

### Vocabularies (the lexicon)

A **vocabulary** is a named set of tokens that fill a single semantic role:

```
ANATOMY_TOKENS (241 tokens):   head, chest, femur, tibia, pelvis, wrist, ...
CONDITION_TOKENS (205 tokens): fracture, infection, hemorrhage, diabetes, ...
ENCOUNTER_TOKENS (19 tokens):  initial, subsequent, sequela, ...
LATERALITY_TOKENS (6 tokens):  left, right, bilateral, midline, ...
```

**39 vocabularies**, 1,273 tokens, organized in 5 categories (core slots, anatomical modifiers, clinical classifiers, specialized domains, ICD abbreviations).

### Templates (the production rules)

A **template** is an ordered combination of vocabulary slots defining which token types can co-occur in a valid medical term:

```
anatomy_x_condition:              ANATOMY x CONDITION         -> "femur fracture"
injury_x_encounter:               INJURY x ENCOUNTER          -> "fracture initial encounter"
laterality_x_anatomy_x_condition: LATERALITY x ANATOMY x CONDITION -> "left femur fracture"
```

**90 templates** from 2-slot (workhorses) to 9-slot (highly specific).

### Matching

A template **matches** an ICD-10-CM term when all slot tokens co-occur in that term (order-independent). Example:

> ICD term: *"displaced fracture of shaft of left femur, initial encounter for closed fracture"*
>
> Matches `anatomy_x_injury_x_encounter` with anatomy="femur", injury="fracture", encounter="initial"

## Coverage

| Metric | Value |
|---|---|
| Total ICD-10-CM terms | 335,538 |
| Matched by grammar | 311,048 |
| **Coverage** | **92.70%** |
| HIGH FP-risk templates | **0** |
| Token specificity (medical-only) | 91.8% |

See [docs/coverage_report.md](docs/coverage_report.md) for full coverage analysis, gap breakdown, and history.

## Project Structure

```
ICD10cm-IntegratedPipeline/
├── reference_data/                # Production data (input + output)
│   ├── slot_vocabularies.json     # 39 vocabularies, 1,273 tokens
│   ├── family_templates.json      # 90 template families
│   ├── medical_conditions.xml     # DLP condition patterns
│   └── icd10cm_core_terms.txt     # Validated core terms
├── scripts/                       # Pipeline tools (stdlib-only Python)
│   ├── validate.py                # Structural + ground-truth validation
│   ├── suggest.py                 # Gap analysis, proposes changesets
│   ├── apply.py                   # Safe changeset application (--dry-run default)
│   ├── precision.py               # Token specificity + FP risk scoring
│   ├── reconcile.py               # JSON vs analyzer Python diff
│   └── analyze_unmatched_terms.py # Coverage gap deep-dive
├── docs/                          # Documentation
│   ├── coverage_report.md         # Full coverage & precision report
│   ├── SLOT_VOCABULARIES.md       # Vocabulary reference
│   ├── FAMILY_TEMPLATES.md        # Template reference
│   └── CORE_TERMS_INTEGRATION.md  # Core terms integration guide
└── README.md
```

## Pipeline Usage

All scripts are **stdlib-only Python 3.9+**, read-only by default, and output machine-readable JSON + human summary to stdout.

```bash
# 1. Validate structural integrity + ground-truth co-occurrence
python3 scripts/validate.py

# 2. Generate improvement suggestions (changeset.json)
python3 scripts/suggest.py

# 3. Preview changes (dry-run, default)
python3 scripts/apply.py

# 4. Apply changes to production files
python3 scripts/apply.py --apply

# 5. Score token specificity + template FP risk
python3 scripts/precision.py

# 6. Compare JSON vocabs with analyzer Python sets
python3 scripts/reconcile.py
```

### Environment

The validation and precision scripts need the ICD-10-CM source CSV:

```bash
export ICD10CM_CSV=/path/to/icd10cm_terms_2026.csv
```

If unset, scripts default to `~/compositional_analysis/icd10cm_terms_2026.csv`.

## Data Products

| File | Format | Purpose |
|---|---|---|
| `slot_vocabularies.json` | JSON | Token sets for DLP pattern generation |
| `family_templates.json` | JSON | Slot combinations defining valid patterns |
| `medical_conditions.xml` | XML | DLP-ready condition patterns |
| `icd10cm_core_terms.txt` | Text | Validated ICD-10-CM core terms |

All production data is version-tracked. Current version: `2026-04-10-v8`.

## Coverage History

| Version | Coverage | Templates | Tokens | Key Change |
|---|---|---|---|---|
| Baseline | 84.37% | 56 | 1,018 | Initial pipeline validation |
| v6 | ~86% | 56 | 1,273 | Added ICD abbreviation vocabulary |
| v7 | 93.63% | 92 | 1,273 | Added 36 templates (orphaned vocabs + missing combos) |
| **v8** | **92.70%** | **90** | **1,273** | Removed 2 HIGH FP-risk templates |

## Roadmap

### Done

- Structural validation pipeline (validate, suggest, apply, precision, reconcile)
- Cross-slot collision resolution and duplicate cleanup
- JSON/Python analyzer reconciliation
- ICD abbreviation vocabulary (60 tokens)
- Templates for all orphaned vocabularies
- Missing template combinations from gap analysis
- FP-risk analysis and HIGH-risk template removal

### Next

- **Additional ICD abbreviations** (~100 rare abbreviations) — est. +1-2% coverage
- **Anatomical sub-specialties** (muscles, vessels, nerves as distinct vocabs) — est. +0.5-1%
- **UMLS/CHV integration** — expand beyond ICD-10-CM to Consumer Health Vocabulary and UMLS Metathesaurus terms
- **Named disease vocabulary** — proper nouns (Wilson disease, Kawasaki syndrome) — est. +0.5-1%, medium FP risk
- **Theoretical ceiling**: ~95-96% of ICD-10-CM terms

## License

[Add license information]

# Core Terms Integration Guide

## Overview

The **Core Terms Extraction Pipeline** is a downstream consumer of the compositional analysis artifacts. It uses slot vocabularies and family templates to extract, validate, and expand medical terminology suitable for Data Loss Prevention (DLP) regex patterns.

This document explains the integration between the two projects and how insights flow bidirectionally.

---

## What Core Terms Does

The core terms pipeline transforms ICD-10-CM codes into DLP-ready term lists through 4 stages:

### Pipeline Stages

```
ICD-10-CM FY2026 Tabular
        ↓
    [1] Extract Core Terms
        ├─ Strip qualifiers (laterality, severity, encounter types)
        ├─ Use LATERALITY_TOKENS from slot_vocabularies.json
        └─ Filter with AI quality checkpoint
        ↓
    [2] Expand with Templates
        ├─ Use family_templates.json (71 families)
        ├─ Use slot_vocabularies.json (ANATOMY, CONDITION tokens)
        └─ Generate missing anatomy × condition combinations
        ↓
    [3] Generate Variations
        ├─ Use ANATOMY_TOKENS for safe word reordering
        ├─ Add plurals, synonyms, US/UK spelling
        └─ Generate anatomical substitutions
        ↓
    [4] Mark Ambiguous
        └─ Flag high false-positive risk terms
        ↓
    Output: core_terms_variations.txt
```

---

## Integration Points

### 1. Slot Vocabularies (`slot_vocabularies.json`)

**Source**: Main compositional analysis project
**Usage in Core Terms**:

| Slot | Used By | Purpose |
|------|---------|---------|
| `LATERALITY_TOKENS` | extract_core_terms.py | Strip "left/right/bilateral" prefixes |
| `ANATOMY_TOKENS` | expand_with_templates.py | Noun anatomy universe for expansion |
| `ANATOMY_TOKENS` | generate_variations.py | Gate safe word reordering |
| `CONDITION_TOKENS` | expand_with_templates.py | Conditions suitable for expansion |

**Critical Dependency**: Core terms relies on accurate token classification. Misclassified tokens (e.g., adjectives in ANATOMY_TOKENS) cause invalid term generation.

### 2. Family Templates (`family_templates.json`)

**Source**: Main compositional analysis project
**Usage in Core Terms**:

The expansion script focuses on **anatomy-bearing templates**:
- `anatomy_x_condition` → "abscess of liver", "liver abscess"
- `anatomy_x_injury` → "fracture of femur", "femur fracture"

**Current Usage**: 38 of 71 templates have empirical evidence in production.

---

## Empirical Validation

Core terms provides **empirical validation** of vocabularies and templates:

### Vocabulary Validation

From `expansion_report.txt`:

```
Slot vocabularies used:
  ANATOMY_TOKENS   : 232 tokens
  CONDITION_TOKENS : 201 tokens

Empirical pairs extracted from existing 11157 core terms:
  Conditions with anatomy variants      : 92
  Noun anatomy tokens (of-position)     : 141
```

**Key Insight**: Only **141 of 232 ANATOMY_TOKENS** (60.8%) are empirically attested as noun forms in "condition of anatomy" patterns. The remaining 91 tokens may be:
- Purely adjectival (e.g., "cardiac", "pulmonary")
- Rarely used anatomical regions
- Misclassified tokens

### Template Validation

From `expansion_report.txt` (lines 18-56):

**38 anatomy-bearing templates validated** in production:
- `anatomy_x_condition`
- `anatomy_x_injury_x_encounter`
- `laterality_x_anatomy_x_condition`
- ... (35 more)

**33 templates unused** in core term generation:
- Templates without anatomy slots
- Templates with no empirical attestations
- Templates for specialized domains (toxic events, maternal care)

### Condition Productivity

Top conditions by expansion potential:

| Condition | New Variants | Attested | Productivity Ratio |
|-----------|--------------|----------|-------------------|
| thrombosis | +122 | 3 | 40.7x |
| hernia | +121 | 3 | 40.3x |
| ischemia | +121 | 3 | 40.3x |
| lesion | +121 | 3 | 40.3x |
| anomaly | +120 | 3 | 40.0x |
| edema | +119 | 8 | 14.9x |
| failure | +120 | 6 | 20.0x |

**Insight**: High-productivity conditions (40x expansion) are candidates for priority inclusion in CONDITION_TOKENS.

---

## Data Flow: Main → Core Terms

### Export Process

When vocabularies or templates are updated in the main project:

1. **Export artifacts**:
   ```bash
   # From main project
   python export_vocabularies.py
   python export_family_templates.py
   ```

2. **Copy to core terms**:
   ```bash
   cp slot_vocabularies.json ../core_terms/icd10cm-core-terms/resources/
   cp family_templates.json ../core_terms/icd10cm-core-terms/resources/
   ```

3. **Re-run core terms pipeline**:
   ```bash
   cd ../core_terms/icd10cm-core-terms/scripts
   python extract_core_terms.py
   python expand_with_templates.py
   python generate_variations.py
   python mark_ambiguous.py
   ```

4. **Review impact**:
   - Check `expansion_report.txt` for new term counts
   - Verify no unexpected terms generated
   - Review coverage delta

---

## Feedback Loop: Core Terms → Main

### Insights for Vocabulary Refinement

Core terms empirical evidence informs main project improvements:

#### 1. **Unused Token Identification**
Tokens in vocabulary but never used in production → candidates for review:
```
ANATOMY_TOKENS with 0 attestations (91 tokens)
→ Review: Are these valid? Misclassified? Too rare?
```

#### 2. **Missing Token Discovery**
High-frequency tokens missing from vocabulary:
```
Frequent anatomy patterns not in ANATOMY_TOKENS
→ Add to vocabulary for improved coverage
```

#### 3. **Misclassification Detection**
ADJECTIVAL_ANATOMY list validation:
```python
# From expand_with_templates.py
ADJECTIVAL_ANATOMY = {
    "abdominal", "aortic", "cardiac", "cerebral", ...
}

# Cross-check: Are these in ANATOMY_TOKENS?
# Should they be in separate ANATOMY_ADJECTIVE_TOKENS?
```

#### 4. **Condition Priority Ranking**
Productivity metrics guide CONDITION_TOKENS curation:
```
High-productivity conditions (30+ expansions) → Priority tokens
Low-productivity conditions (<5 expansions) → Review necessity
```

### Integration Tool: Vocabulary Validator

The integrated pipeline provides `validate_vocabularies.py`:

```bash
python scripts/validate_vocabularies.py

# Output:
# - vocabulary_validation_report.md
# - vocabulary_refinement_suggestions.json
```

**Reports include**:
- Unused tokens with 0 attestations
- Missing high-frequency tokens
- Misclassification candidates
- Condition productivity rankings

---

## Version Management

### Current Status
- **Vocabularies**: Manually synced (no version tracking)
- **Templates**: Manually synced (no version tracking)
- **Risk**: Vocabularies can drift between projects

### Recommended Approach

Add version metadata to JSON files:

```json
{
  "metadata": {
    "version": "2026-03-27-v1",
    "source_commit": "5a372dc",
    "source_project": "compositional_analysis",
    "last_sync": "2026-03-27T10:00:00Z",
    "total_slots": 26,
    "total_tokens": 1065
  },
  "categories": { ... }
}
```

Use sync tool:
```bash
# Check if vocabularies are in sync
python scripts/sync_vocabularies.py --diff

# Export from main → core terms with versioning
python scripts/sync_vocabularies.py --export
```

---

## Interpreting Expansion Reports

### Sample Report Section

```
Top expanded conditions (most new anatomy variants):
  thrombosis               : +122 new  (3 attested)
  hernia                   : +121 new  (3 attested)
```

**Interpretation**:
- **+122 new**: 122 new terms generated (e.g., "thrombosis of kidney", "thrombosis of lung")
- **(3 attested)**: Only 3 anatomy variants seen in original ICD terms
- **Ratio 40.7x**: High expansion ratio indicates productive pattern

**Action Items**:
1. Review generated terms for clinical validity
2. Verify no nonsensical combinations (e.g., "thrombosis of nail")
3. Consider adding anatomical constraints if needed

### Family Templates with Anatomy×Condition Slots

```
Family templates with anatomy×condition/injury slots (38):
  anatomy_x_condition
  anatomy_x_injury_x_encounter
  laterality_x_anatomy_x_condition
  ...
```

**Interpretation**:
- **38 templates**: Empirically validated in production
- **33 templates unused**: No attestations in core terms generation

**Action Items**:
1. Prioritize developing/testing the 38 validated templates
2. Review unused templates for applicability
3. Consider archiving templates with 0 production evidence

---

## Testing Vocabulary Changes

Before applying vocabulary changes to main project:

```bash
# Test impact of adding a token
python scripts/test_vocabulary_change.py \
  --add ANATOMY_TOKENS:prostate

# Output:
# Main analyzer coverage: 55.36% → 55.89% (+0.53%)
# Core terms: 17,671 → 17,798 (+127 terms)
# Impact: Positive
```

### Validation Checklist

Before merging vocabulary changes:

- [ ] Token appears in 3+ empirical patterns
- [ ] Coverage improvement ≥0.1%
- [ ] No false positive terms generated
- [ ] Token correctly classified (anatomy vs condition vs qualifier)
- [ ] Core terms pipeline runs successfully
- [ ] Expansion report shows expected new terms

---

## Troubleshooting

### Issue: Core terms generates nonsensical combinations

**Example**: "abscess of corneal" (adjective, not noun)

**Cause**: Adjective in ANATOMY_TOKENS used in "of anatomy" position

**Fix**:
1. Add to ADJECTIVAL_ANATOMY exclusion list in `expand_with_templates.py`
2. Consider moving to separate ANATOMY_ADJECTIVE_TOKENS vocabulary
3. Re-run expansion to verify fix

### Issue: Vocabulary drift detected

**Symptom**: Core terms using outdated vocabularies

**Cause**: Manual copy-paste, no version tracking

**Fix**:
```bash
# Sync vocabularies with version metadata
python scripts/sync_vocabularies.py --export
```

### Issue: Low coverage improvement after vocabulary addition

**Symptom**: Added 10 tokens, coverage only +0.05%

**Cause**: Rare tokens, or tokens already implicitly matched by fuzzy matching

**Analysis**:
```bash
# Check actual token usage
python scripts/validate_vocabularies.py
grep "newly_added_token" analysis_outputs/vocabulary_validation_report.md
```

---

## Future Enhancements

1. **Automated Sync**: Git hooks to prevent vocabulary drift
2. **Coverage Tracking**: Historical coverage metrics over time
3. **Token Frequency Analysis**: Data-driven vocabulary prioritization
4. **Template Recommendation**: Suggest new templates based on unmatched patterns
5. **Quality Metrics**: Precision/recall for generated terms

---

## References

- Main Project: `/home/bguide/compositional_analysis`
- Core Terms: `/home/bguide/compositional_analysis/core_terms/icd10cm-core-terms`
- Integration Tools: `/home/bguide/ICD10cm-IntegratedPipeline`

## See Also

- [VOCABULARY_CURATION_GUIDE.md](VOCABULARY_CURATION_GUIDE.md) - Workflow for vocabulary updates
- [PROJECT_PLAN.md](../PROJECT_PLAN.md) - Implementation roadmap
- [README.md](../README.md) - Project overview

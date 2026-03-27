# Changelog

All notable changes to the ICD-10-CM Integrated Pipeline project.

## [v2026-03-27-v2] - 2026-03-27

### Added - Vocabulary Improvements
- **Created ANATOMY_ADJECTIVE_TOKENS vocabulary** (30 tokens)
  - New vocabulary slot for adjectival anatomy forms
  - Proper separation from noun forms in ANATOMY_TOKENS

- **Applied evidence-based vocabulary refinement**
  - Moved 30 adjectival tokens from ANATOMY_TOKENS to ANATOMY_ADJECTIVE_TOKENS
  - Examples: cardiac, pulmonary, cerebral, myocardial, etc.

- **New scripts**
  - `scripts/apply_vocabulary_improvements.py` - Automated vocabulary refinement
  - `scripts/validate_vocabularies.py` - Validation and analysis tool

- **Comprehensive documentation**
  - `docs/FAMILY_TEMPLATES.md` - Family template reference
  - `docs/SLOT_VOCABULARIES.md` - Slot vocabulary reference
  - `docs/CORE_TERMS_INTEGRATION.md` - Integration guide
  - `reference_data/VOCABULARY_TEMPLATE_REFERENCE.json` - Combined reference

### Changed
- **ANATOMY_TOKENS**: 232 → 202 tokens (-30 adjectival forms moved)
- **Total vocabulary slots**: 26 → 27 (+1 new ANATOMY_ADJECTIVE_TOKENS)
- **slot_vocabularies.json** updated to version 2026-03-27-v2

### Impact on Core Terms Expansion

#### Before (v1)
- ANATOMY_TOKENS: 232 tokens
- Empirical noun anatomy: 141 tokens
- Generated terms: 6,514
- Total core terms: 17,671

#### After (v2)
- ANATOMY_TOKENS: 202 tokens (cleaner noun vocabulary)
- Empirical noun anatomy: 122 tokens (accurate count)
- Generated terms: 5,549 (-965 invalid terms eliminated ✅)
- Total core terms: 16,706 (higher quality output ✅)

### Quality Improvements
- ✅ **Eliminated ~965 invalid term patterns**
  - Prevented generation of nonsensical terms like "abscess of cardiac"
  - Only valid noun forms used in "condition of anatomy" patterns

- ✅ **Improved semantic accuracy**
  - Clear distinction between adjectival and noun anatomy tokens
  - Proper grammatical structure in all generated terms

- ✅ **Enhanced template development foundation**
  - ANATOMY_ADJECTIVE_TOKENS available for future adjective-based templates
  - Better token type boundaries improve maintainability

### Main Compositional Analysis Impact
- **Coverage: 55.36% MAINTAINED** (218,028 / 393,844 terms)
- No regression from vocabulary improvements
- Cleaner vocabulary classification benefits future template development

---

## [v2026-03-27-v1] - 2026-03-27

### Added - Initial Release
- Project structure (scripts, analysis_outputs, reference_data, docs)
- Reference data from source projects
  - `slot_vocabularies.json` (26 slots, 1,065 tokens)
  - `family_templates.json` (71 families)
  - `icd10cm_core_terms.txt` (17,671 terms)
  - `core_terms_expansion_report.txt`

- **Vocabulary validation tooling**
  - `scripts/validate_vocabularies.py`
  - Empirical analysis: 60.8% anatomy token usage rate
  - Identified 30 misclassified adjectival tokens
  - Validated 9 high-productivity conditions

- **Documentation**
  - `README.md` - Project overview
  - `PROJECT_PLAN.md` - 5-phase implementation strategy
  - `docs/CORE_TERMS_INTEGRATION.md` - Integration guide

### Initial Findings
- ANATOMY_TOKENS: 232 defined, 141 empirically attested (60.8% usage)
- Misclassified tokens: 30 (adjectival forms in noun vocabulary)
- High-productivity conditions: 9 with ratio >30x
- All high-productivity conditions already in CONDITION_TOKENS ✓

---

## Future Roadmap

### Phase 3: Sync & Version Management System
- Build `scripts/sync_vocabularies.py`
- Implement `--export`, `--diff`, `--validate` commands
- Add version metadata to JSON files
- Optional git pre-commit hooks

### Phase 4: Template Utilization Analysis
- Build `scripts/analyze_template_usage.py`
- Augment `family_templates.json` with usage metadata
- Generate template utilization reports
- Categorize templates (high/low/unused usage)

### Phase 5: Curation Workflow Documentation
- Create `docs/VOCABULARY_CURATION_GUIDE.md`
- Build `scripts/test_vocabulary_change.py`
- Create `docs/VOCABULARY_REVIEW_CHECKLIST.md`
- Document end-to-end curation process

---

## Version Numbering

Format: `v{YYYY-MM-DD}-v{INCREMENT}`

- **Date component**: Date of release
- **Increment**: Version number within that date (v1, v2, v3, ...)

Example: `v2026-03-27-v2` = Second version released on March 27, 2026

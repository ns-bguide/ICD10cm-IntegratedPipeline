# ICD-10-CM Integrated Pipeline - Implementation Plan

## Context

This project creates bidirectional flow between compositional analysis and core terms extraction to improve vocabulary quality and template curation.

**Source Projects**:
- Main: `/home/bguide/compositional_analysis`
- Core Terms: `/home/bguide/compositional_analysis/core_terms/icd10cm-core-terms`

**Current Metrics**:
- Main project coverage: 55.36% (218,028 / 393,844 terms)
- Core terms: 17,671 (11,157 ICD + 6,514 template-expanded)
- Empirical validation: 141 anatomy tokens, 38 templates

## Implementation Phases

### Phase 1: Documentation & Data Sharing (Quick Win)
**Estimated Time**: 1-2 hours
**Status**: In Progress

#### Tasks
- [x] Create project structure
- [ ] Copy reference data from source projects
  - [ ] `slot_vocabularies.json` → `reference_data/`
  - [ ] `family_templates.json` → `reference_data/`
  - [ ] `core_terms.txt` → `reference_data/icd10cm_core_terms.txt`
  - [ ] `expansion_report.txt` → `analysis_outputs/core_terms_expansion_report.txt`
- [ ] Create `docs/CORE_TERMS_INTEGRATION.md`
- [ ] Update cross-references in source projects
- [ ] Initial git commit

**Value**: Immediate discoverability, no code changes required

---

### Phase 2: Vocabulary Validation Tool (High Value)
**Estimated Time**: 2-3 hours
**Status**: Not Started

#### Tasks
- [ ] Create `scripts/validate_vocabularies.py`
  - [ ] Parse expansion report for empirical tokens
  - [ ] Compare against slot_vocabularies.json
  - [ ] Identify unused tokens
  - [ ] Identify missing high-frequency tokens
  - [ ] Validate ADJECTIVAL_ANATOMY classification
- [ ] Generate `analysis_outputs/vocabulary_validation_report.md`
- [ ] Generate `analysis_outputs/vocabulary_refinement_suggestions.json`
- [ ] Test validation script

**Value**: Actionable insights for vocabulary improvement

---

### Phase 3: Sync Infrastructure
**Estimated Time**: 2-3 hours
**Status**: Not Started

#### Tasks
- [ ] Create `scripts/sync_vocabularies.py`
  - [ ] Implement `--export` command
  - [ ] Implement `--diff` command
  - [ ] Implement `--validate` command
- [ ] Add version metadata to JSON files
  - [ ] Update `reference_data/slot_vocabularies.json`
  - [ ] Update `reference_data/family_templates.json`
- [ ] Test sync operations
- [ ] (Optional) Create pre-commit hook

**Value**: Prevents vocabulary drift, enables confident updates

---

### Phase 4: Template Utilization Analysis
**Estimated Time**: 1-2 hours
**Status**: Not Started

#### Tasks
- [ ] Create `scripts/analyze_template_usage.py`
  - [ ] Parse expansion report for template usage
  - [ ] Cross-reference with family_templates.json
  - [ ] Calculate productivity metrics
  - [ ] Categorize templates (high/low/unused)
- [ ] Augment `reference_data/family_templates.json` with metadata
- [ ] Generate `analysis_outputs/template_utilization_report.md`
- [ ] Test analysis script

**Value**: Evidence-based template curation

---

### Phase 5: Curation Workflow Documentation
**Estimated Time**: 2-3 hours
**Status**: Not Started

#### Tasks
- [ ] Create `docs/VOCABULARY_CURATION_GUIDE.md`
  - [ ] Document vocabulary flow
  - [ ] Define update triggers
  - [ ] Document validation process
  - [ ] Define approval workflow
- [ ] Create `scripts/test_vocabulary_change.py`
  - [ ] Implement change proposal parser
  - [ ] Run main analyzer with changes
  - [ ] Run core terms with changes
  - [ ] Generate impact report
- [ ] Create `docs/VOCABULARY_REVIEW_CHECKLIST.md`
- [ ] Test workflow end-to-end

**Value**: Sustainable long-term maintenance

---

## Total Estimated Effort

**8-13 hours** across 5 phases

## Verification Plan

### Per-Phase Testing
1. **Phase 1**: Verify files copied correctly, documentation accessible
2. **Phase 2**: Run validation script, check reports generated
3. **Phase 3**: Test sync commands, verify no drift
4. **Phase 4**: Run template analysis, check metadata added
5. **Phase 5**: Execute end-to-end workflow test

### End-to-End Integration Test
1. Run main analyzer → baseline coverage
2. Run validation → get suggestions
3. Apply vocabulary change
4. Re-run analyzer → verify coverage increase
5. Export to core terms
6. Run core terms → verify updated vocabularies used

## Dependencies

- Python 3.9+
- json, pathlib (stdlib)
- No external dependencies required

## Success Criteria

- [ ] All 5 phases implemented and tested
- [ ] Vocabulary validation identifies actionable improvements
- [ ] Sync tool maintains consistency across projects
- [ ] Template utilization provides evidence-based rankings
- [ ] Curation workflow is documented and executable
- [ ] Coverage improvement measurable (target: +2-5%)

## Next Actions

1. Complete Phase 1 data copying
2. Create integration documentation
3. Begin Phase 2 validation tool development

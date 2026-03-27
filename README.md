# ICD-10-CM Integrated Pipeline

An integrated analysis pipeline that combines compositional analysis insights with core term extraction to improve medical terminology vocabularies and template families.

## Project Overview

This project creates a **bidirectional feedback loop** between:
- **Compositional Analysis**: Slot-based template matching across ICD-10-CM terms
- **Core Terms Extraction**: DLP-focused term extraction and expansion

### Key Goals

1. **Vocabulary Validation**: Use empirical evidence from core terms to validate and refine slot vocabularies
2. **Template Utilization**: Identify production-ready templates vs theoretical ones
3. **Sync Management**: Maintain version consistency across projects
4. **Curation Workflow**: Document and automate vocabulary improvement cycles

## Current Status

- **Main Project Coverage**: 55.36% (218,028 / 393,844 terms)
- **Core Terms Generated**: 17,671 (from 11,157 ICD-derived + 6,514 template-expanded)
- **Empirical Validation**: 141 anatomy tokens, 38 anatomy-bearing templates validated

## Project Structure

```
ICD10cm-IntegratedPipeline/
├── scripts/                      # Analysis and sync tools
│   ├── validate_vocabularies.py  # Vocabulary validation tool
│   ├── analyze_template_usage.py # Template utilization analysis
│   ├── sync_vocabularies.py      # Sync tool for vocabulary management
│   └── test_vocabulary_change.py # Impact testing for vocabulary changes
├── analysis_outputs/             # Generated reports and findings
├── reference_data/               # Shared data products
│   ├── slot_vocabularies.json    # Master vocabulary definitions
│   ├── family_templates.json     # Master template definitions
│   └── icd10cm_core_terms.txt    # Validated core terms
├── docs/                         # Documentation
│   ├── CORE_TERMS_INTEGRATION.md
│   ├── VOCABULARY_CURATION_GUIDE.md
│   └── VOCABULARY_REVIEW_CHECKLIST.md
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.9+
- Access to source projects:
  - Main compositional analysis project
  - Core terms extraction project

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ICD10cm-IntegratedPipeline.git
cd ICD10cm-IntegratedPipeline

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (if any are added)
# pip install -r requirements.txt
```

### Basic Usage

```bash
# Validate vocabularies against empirical evidence
python scripts/validate_vocabularies.py

# Analyze template utilization
python scripts/analyze_template_usage.py

# Check vocabulary sync status
python scripts/sync_vocabularies.py --diff

# Test impact of vocabulary changes
python scripts/test_vocabulary_change.py --add ANATOMY_TOKENS:example
```

## Implementation Roadmap

### Phase 1: Documentation & Data Sharing ✓ (In Progress)
- [x] Project structure setup
- [ ] Copy reference data from source projects
- [ ] Create integration documentation
- [ ] Update cross-references

### Phase 2: Vocabulary Validation
- [ ] Build validation script
- [ ] Generate validation reports
- [ ] Create refinement suggestions

### Phase 3: Sync Infrastructure
- [ ] Build sync tool
- [ ] Add version metadata
- [ ] Optional git hooks

### Phase 4: Template Analysis
- [ ] Build utilization analyzer
- [ ] Augment template metadata
- [ ] Generate utilization reports

### Phase 5: Curation Workflow
- [ ] Document workflow
- [ ] Build testing tools
- [ ] Create review checklist

## Contributing

This is an integration project that pulls insights from:
- [compositional_analysis](../compositional_analysis) - Main analysis pipeline
- [compositional_analysis/core_terms/icd10cm-core-terms](../compositional_analysis/core_terms/icd10cm-core-terms) - Core terms pipeline

See [docs/VOCABULARY_CURATION_GUIDE.md](docs/VOCABULARY_CURATION_GUIDE.md) for contribution guidelines.

## Key Insights

From empirical validation:
- **141 noun anatomy tokens** validated (vs 232 defined)
- **38 anatomy-bearing templates** production-ready (of 71 total)
- **92 conditions** suitable for expansion (≥3 attestations)
- **Top productive conditions**: thrombosis (+122), hernia (+121), ischemia (+121)

## Source Projects

- **Compositional Analysis**: `/home/bguide/compositional_analysis`
- **Core Terms**: `/home/bguide/compositional_analysis/core_terms/icd10cm-core-terms`

## License

[Add license information]

## Contact

[Add contact information]

# [In Progress] ICD-10-CM TITLES (US-ENG)

**Overall Status:** WORK IN PROGRESS
**Jira ticket link:** ENG-772513: [Frigate] R&D for the Replacement Diagnostic Classifications Entity (ICD-10) IN PROGRESS
**Google Drive Link:** Sign in to access Google Drive Folder

### Sources

- [ICD-10 | CMS](https://www.cms.gov/medicare/coding/icd10)
- [ICD-10-CM](https://www.cdc.gov/nchs/icd/icd-10-cm.htm)
- [Medical Coding ICD-10-CM Chapters](https://www.aapc.com/icd-10/icd-10-cm-codes/)
- [Structure of an ICD-10-CM Code | SEER Training](https://training.seer.cancer.gov/icd10cm/structure/)
- [CMS ICD-10 Overview Slides](https://www.cms.gov/medicare/coding/icd10/downloads/032310_icd10_slides.pdf)
- [ICD-10 Code Structure](https://www.healthnetworksolutions.net/index.php/understanding-the-icd-10-code-structure)
- [CDC ICD-10-CM Search Tool (FY2026)](https://icd10cmtool.cdc.gov/?fy=FY2026)
- [UMLS - Unified Medical Language System](https://www.nlm.nih.gov/research/umls/index.html)
- [Consumer Health Vocabulary (CHV)](https://biomedinfo.smhs.gwu.edu/chv-files)
- [SNOMED CT](https://www.nlm.nih.gov/healthit/snomedct/index.html)

### Scope of Research

- **Target Region:** United States (the CM, or Clinical Modification, is developed by CMS for US healthcare data).
- **Language:** English.
- **Data Characteristics:** The terminology consists of official medical conditions, administrative context phrases, and specific modifiers (such as laterality and encounter types).
- **Ambiguity:** ICD-10-CM codes are designed to map to single clinical concepts, making them generally less ambiguous by design. However, certain generated short terms (under 6 characters) were noted to concentrate acronyms and "trash".
- **Formatting/Affixing Notes:** The language relies heavily on hyphenations, apostrophes, and standard clinical abbreviations. Abbreviations in the official CMS source typically only occur when strictly necessary.

---

## Pipeline Overview

This report documents the end-to-end pipeline for building a high-precision DLP detection grammar from ICD-10-CM medical terminology. The pipeline follows six stages:

```
  STAGE 1               STAGE 2                STAGE 3                  STAGE 4
  Data Gathering  --->  Normalization &  --->  Generative Grammar --->  Validation
  (ICD-10-CM,           Enrichment             (Vocabularies,           (Structural,
   UMLS, CHV,           (98K -> 335K           Templates,               Precision,
   SNOMED CT)            entries)               Core Terms)              Ground-truth)
                                                     |
                                                     v
                                               STAGE 5                  STAGE 6
                                               Coverage Testing  --->   Next Steps
                                               & Improvement
                                               (84% -> 93%)
```

### Current Results Summary

| Metric | Value |
|---|---|
| ICD-10-CM terms matched | **311,048 of 335,538 (92.70%)** |
| HIGH false-positive-risk templates | **0** |
| Token medical specificity | **91.8%** (1,169 of 1,273 tokens are medical-only) |
| Vocabulary slots | 39 (1,273 tokens) |
| Template families | 90 |

The pipeline's design goal is **high precision**: match as much of the enriched ICD-10-CM corpus as possible **without generating false positives** in DLP detection. Coverage was deliberately reduced from 93.63% to 92.70% by removing 2 templates that carried unacceptable false-positive risk.

---

## Stage 1: Data Gathering

### ICD-10-CM

The ICD-10-CM (International Classification of Diseases, Tenth Revision, Clinical Modification) is a standardized system used by healthcare providers to classify diagnoses and medical conditions for morbidity reporting. While it is derived from the World Health Organization's (WHO) core ICD-10 framework, the "Clinical Modification" is specifically tailored for the United States. Under authorization from the WHO, the National Center for Health Statistics (NCHS) -- a division of the CDC -- develops and maintains these U.S.-specific extensions. This ensures that while the codes meet domestic clinical needs, they remain strictly consistent with the global structures and conventions established by the WHO.

#### ICD-10-CM Code Structure

ICD-10-CM codes follow a hierarchical classification structure. Codes are organized into chapters, where each chapter corresponds to a specific body system, disease category, or external cause. For example, Chapter A00-B99 covers Certain Infectious and Parasitic Diseases.

Each ICD-10-CM entry contains several fields that describe the coded condition. These typically include an index identifier, the ICD-10-CM code, a flag value, a short description, and a long description.

For example:

```
1  00084  A081  0  Acute gastrent d/t Norwalk agent and oth small round vir
```

In this example, `A081` is the ICD-10-CM code. The short description provides a condensed form, while the long description provides the fully expanded medical terminology associated with the diagnosis.

#### ICD-10-CM 2026 Dataset

The ICD-10-CM 2026 dataset contains **98,186 diagnosis entries**, each represented as a textual description.

| Statistic | Value |
|---|---|
| Count | 98,186 |
| Mean words per entry | 9.66 |
| Std | 4.71 |
| Min | 1 |
| 25% | 6 |
| 50% (Median) | 9 |
| 75% | 13 |
| Max | 31 |

Most ICD-10-CM descriptions are brief but sufficiently descriptive for clinical specificity.

### External Medical Databases

Term enrichment is necessary because medical language is highly specialized and often expressed through multiple parallel vocabularies. The same medical concept may appear in formal scientific terminology, clinical abbreviations, or everyday language used by patients and healthcare staff.

Capturing these alternative expressions is essential for robust detection. For example, while "myocardial infarction" is the formal diagnostic term used in medical classification systems, the same condition is commonly referred to as "heart attack" in clinical notes, patient communication, or informal documentation.

If detection relies solely on canonical ICD terminology, many valid references to medical conditions may be missed. In the context of Data Loss Prevention (DLP) systems, this limitation could allow sensitive Protected Health Information (PHI) to escape detection. Expanding the terminology set with synonymous expressions and lexical variants therefore improves recall and increases the overall effectiveness of PHI detection.

#### UMLS Integration

The Unified Medical Language System (UMLS) integrates multiple biomedical vocabularies, including 74 English datasets and 71 datasets in other languages.

UMLS links synonymous terms using a shared Concept Unique Identifier (CUI). For each CUI, the API can return multiple atoms, where each atom represents a term variant from a specific source vocabulary.

Example:

| Query Term | CUI | Source Vocabulary | AUI | Term String |
|---|---|---|---|---|
| cholera due to vibrio cholerae 01, biovar cholerae | C0494021 | ICPC2ICD10DUT | A5068103 | Vibrio cholerae 01; biovar cholerae |

Each atom's term string can be added as a lexical variant in the enriched terminology list.

#### CHV Integration

The Consumer Health Vocabulary (CHV) focuses on expressions commonly used by healthcare consumers, including colloquial terms, ambiguous phrases, slang, and misspellings. During integration, most CHV terms were already present through UMLS or existing enrichment rules. Out of approximately 158,000 CHV terms, only 620 new variants were added after deduplication.

#### SNOMED CT Integration

SNOMED CT is a comprehensive clinical terminology system used for electronic health information exchange. SNOMED CT data has been downloaded and integrated into the enrichment pipeline. Overlap with UMLS-derived terms was evaluated to determine additional variants contributed by this source.

---

## Stage 2: Normalization, Data Wrangling, and Enrichment

Starting from the initial dataset of **98,186 leaf node entries**, the terms are processed through normalization and enrichment rules to generate an expanded list of over **335,538 entries**. This expanded corpus serves as both the training ground and the test set for the generative grammar.

### Normalization

- **Canonical Formatting:** Official terms are standardized by converting to lowercase, trimming white spaces, and eliminating final punctuation.

### Rule-Based Enrichment

- **Simple Modifications:** Applied rules to remove or collapse hyphenation (e.g., `non-hodgkin` -> `non hodgkin` / `nonhodgkin`), remove apostrophes, and replace "&" with "and".
- **Abbreviations:** Added common clinical abbreviations (e.g., `syndrome` -> `synd`, `chronic` -> `chr`, `acute` -> `acu`, `left`/`right` -> `lt`/`rt`).
- **Synonym Expansion:** Standardized replaceable relational patterns, such as mapping "due to" to "because of" or "caused by".

### Linguistic Analysis

The dataset was analyzed using `spaCy` for word frequency and part-of-speech (POS) tagging. From this analysis, two frequency-based vocabularies were constructed:

- **Function words**: `of`, `with`, `for`, `and`, `or`, `in`, `to`, `by`, `at`, `without`
- **High-frequency modifiers**: `unspecified`, `subsequent`, `other`, `right`, `initial`, `left`, `open`, `lower`, `nondisplaced`, `closed`

These frequency lists informed the initial construction of vocabulary slots in Stage 3.

---

## Stage 3: Generative Grammar -- Vocabularies, Templates, and Core Terms

The central methodology of this project is a **generative grammar** for medical terminology. Rather than maintaining a flat list of terms, the system produces two structured data products whose **cross-product** defines the pattern space for DLP detection:

1. **Slot Vocabularies** (the lexicon) -- curated sets of tokens organized by semantic role
2. **Family Templates** (the production rules) -- ordered combinations of vocabulary slots defining which token types can co-occur in a valid medical term

The key insight is that ICD-10-CM terms are **compositional**: they are constructed from a small set of recurring components (anatomy, conditions, qualifiers, laterality, encounter types) combined according to predictable structural patterns. By decomposing terms into their constituent slots and learning the valid combinations, the grammar can match terms it has never explicitly seen -- as long as the component tokens and their combination pattern are known.

### Why a Generative Grammar?

A flat term list (even an enriched one with 335K+ entries) has fundamental limitations for DLP:
- **Brittle matching:** If a term appears with slightly different phrasing, it may be missed.
- **Maintenance burden:** Adding coverage requires manually adding each new term.
- **No compositionality:** The list doesn't "understand" that "fracture of left femur" and "fracture of right tibia" share the same structural pattern.

The generative grammar addresses all three:
- **Flexible matching:** Token co-occurrence is order-independent, naturally handling word-order variations.
- **Scalable coverage:** Adding one anatomy token to a vocabulary can instantly cover hundreds of new term combinations across all templates that use that vocabulary.
- **Compositional understanding:** The grammar encodes the structure of medical terminology, not just individual terms.

### 3a. Vocabularies (The Lexicon)

A **vocabulary** (or "slot") is a named set of tokens that fill a single semantic role in medical terminology. Each token is a word or abbreviation that appears in ICD-10-CM terms.

**Current statistics:** 39 vocabulary slots, 1,273 tokens, organized in 4 categories.

| Category | Vocabs | Tokens | Purpose |
|---|---|---|---|
| Core Compositional Slots | 7 | 683 | Anatomy, conditions, injuries, encounters, qualifiers, severity, ICD abbreviations |
| Anatomical Modifiers | 4 | 89 | Laterality, location, prefixes, adjectives |
| Clinical Detail & Classification | 14 | 224 | Disease state, classifiers, fracture details, healing, neoplasms, seizures, etc. |
| Specialized Domains | 14 | 277 | Toxic events, mechanisms, etiology, procedures, pathogens, substances, etc. |

#### Core Compositional Slots

These are the workhorse vocabularies that appear in the majority of templates:

**ANATOMY_TOKENS** (241 tokens) -- Body parts, organs, and anatomical structures:
```
head, chest, femur, tibia, pelvis, wrist, shoulder, vertebra, kidney, liver,
lung, heart, brain, spine, retina, colon, pancreas, bladder, ovary, prostate,
aorta, esophagus, larynx, trachea, bronchus, sternum, clavicle, scapula, ...
```

**CONDITION_TOKENS** (205 tokens) -- Diseases, disorders, and clinical conditions:
```
fracture, infection, hemorrhage, diabetes, pneumonia, stenosis, thrombosis,
aneurysm, abscess, hernia, edema, fibrosis, necrosis, obstruction, embolism,
carcinoma, melanoma, arthritis, osteoporosis, dementia, epilepsy, asthma, ...
```

**INJURY_TOKENS** (37 tokens) -- Specific injury types:
```
fracture, dislocation, sprain, strain, laceration, contusion, abrasion,
puncture, avulsion, amputation, subluxation, crush, bite, burn, corrosion, ...
```

**ENCOUNTER_TOKENS** (19 tokens) -- Clinical encounter context:
```
initial, subsequent, sequela, encounter, routine, screening, examination,
surveillance, aftercare, follow-up, prophylactic, counseling, ...
```

**QUALIFIER_TOKENS** (113 tokens) -- Descriptive modifiers:
```
unspecified, displaced, nondisplaced, open, closed, chronic, acute, primary,
secondary, recurrent, bilateral, malignant, benign, idiopathic, congenital, ...
```

**SEVERITY_TOKENS** (8 tokens):
```
mild, moderate, severe, stage, grade, type, degree, level
```

**ICD_ABBREVIATION_TOKENS** (60 tokens) -- High-frequency abbreviations specific to ICD-10-CM descriptions. Each abbreviation appears in 1,500-16,000 ICD terms:
```
clsn    (collision)        physl   (physical)       femr    (femur)
displ   (displaced)        fx      (fracture)       w/      (with)
unspcf  (unspecified)      trmt    (treatment)      subseq  (subsequent)
oth     (other)            preg    (pregnancy)      intl    (initial)
```

These abbreviations are unique to CMS coding conventions and do not overlap with common English.

#### Anatomical Modifiers

**LATERALITY_TOKENS** (6 tokens):
```
left, right, bilateral, midline, contralateral, ipsilateral
```

**ANATOMY_ADJECTIVE_TOKENS** (42 tokens) -- Adjectival forms of anatomy, separated from noun forms to prevent grammatically invalid term generation:
```
cardiac, pulmonary, cerebral, myocardial, renal, hepatic, thoracic, cervical,
abdominal, spinal, retinal, corneal, peritoneal, intestinal, cutaneous, ...
```

> **Key Design Decision:** Adjectival anatomy tokens are maintained in a separate vocabulary from noun anatomy tokens. This prevents the grammar from generating invalid terms like "abscess of cardiac" (adjective in noun position). Only noun forms appear in templates using the `of [anatomy]` pattern, producing valid terms like "abscess of heart". This separation eliminated **965 previously invalid term patterns**.

**LOCATION_PREFIX_TOKENS** (26 tokens):
```
para, peri, supra, infra, retro, sub, trans, epi, ...
```

#### Specialized Domain Vocabularies

**TOXIC_EVENT_TOKENS** (13 tokens): `poisoning, adverse, underdosing, toxic, effect, ...`

**TOXIC_AGENT_TOKENS** (38 tokens): `drug, medication, substance, chemical, alcohol, pesticide, venom, gas, ...`

**INTENT_TOKENS** (6 tokens): `accidental, intentional, assault, undetermined, therapeutic, ...`

**PATHOGEN_TOKENS** (12 tokens): `streptococcal, staphylococcal, gonococcal, pneumococcal, meningococcal, ...`

### 3b. Templates (The Production Rules)

A **template** (or "family") is an ordered combination of vocabulary slots. It defines which slot types can appear together in a valid medical term.

**Current statistics:** 90 template families, ranging from 2-slot (simplest) to 9-slot (most specific), averaging 3.6 slots.

| Slot Count | Templates |
|---|---|
| 2-slot (workhorses) | 35 |
| 3-slot | 28 |
| 4-slot | 15 |
| 5-slot | 6 |
| 6-9 slot | 6 |

#### How Templates Work

A template **matches** an ICD-10-CM term when **all slot tokens co-occur** in that term. The matching is **order-independent** -- it checks that every token from every slot appears somewhere in the term, regardless of position. This captures the compositional structure of ICD-10-CM terms, which use consistent vocabulary but vary in word order and connecting words ("of", "with", "for").

#### Concrete Examples

**2-slot templates** (highest coverage, simplest patterns):

```
Template: anatomy_x_condition
  Slots:   [ANATOMY_TOKENS, CONDITION_TOKENS]
  Matches: 189,496 ICD terms

  Examples:
    "femur" + "fracture"    -> matches "fracture of femur"
    "kidney" + "infection"  -> matches "infection of kidney"
    "liver" + "abscess"     -> matches "abscess of liver"
    "lung" + "carcinoma"    -> matches "carcinoma of lung"
```

```
Template: encounter_x_condition
  Slots:   [ENCOUNTER_TOKENS, CONDITION_TOKENS]
  Matches: 182,084 ICD terms

  Examples:
    "initial" + "fracture"     -> matches "fracture, initial encounter"
    "subsequent" + "burn"      -> matches "burn, subsequent encounter"
```

```
Template: injury_x_encounter
  Slots:   [INJURY_TOKENS, ENCOUNTER_TOKENS]
  Matches: 167,761 ICD terms

  Examples:
    "fracture" + "initial"     -> matches "initial encounter for closed fracture"
    "dislocation" + "sequela"  -> matches "dislocation of shoulder, sequela"
```

**3-slot templates** (add specificity with a third dimension):

```
Template: anatomy_x_laterality_x_condition
  Slots:   [ANATOMY_TOKENS, LATERALITY_TOKENS, CONDITION_TOKENS]
  Matches: 105,648 ICD terms

  Examples:
    "femur" + "left" + "fracture"
      -> matches "displaced fracture of shaft of left femur"

    "kidney" + "bilateral" + "stenosis"
      -> matches "bilateral renal artery stenosis"
```

```
Template: qualifier_x_anatomy_x_condition
  Slots:   [QUALIFIER_TOKENS, ANATOMY_TOKENS, CONDITION_TOKENS]
  Matches: 103,845 ICD terms

  Examples:
    "chronic" + "liver" + "failure"     -> matches "chronic liver failure"
    "displaced" + "femur" + "fracture"  -> matches "displaced fracture of shaft of femur"
```

**4-slot templates** (highly specific):

```
Template: anatomy_x_laterality_x_injury_x_encounter
  Slots:   [ANATOMY_TOKENS, LATERALITY_TOKENS, INJURY_TOKENS, ENCOUNTER_TOKENS]
  Matches: 89,555 ICD terms

  Example:
    "femur" + "left" + "fracture" + "initial"
      -> matches "displaced fracture of shaft of left femur, initial encounter
                  for closed fracture"
```

```
Template: toxic_event_x_agent_x_intent_x_encounter
  Slots:   [TOXIC_EVENT_TOKENS, TOXIC_AGENT_TOKENS, INTENT_TOKENS, ENCOUNTER_TOKENS]

  Example:
    "poisoning" + "drug" + "accidental" + "initial"
      -> matches "poisoning by unspecified drug, accidental, initial encounter"
```

**5+ slot templates** (very specific, capture complex multi-dimensional terms):

```
Template: laterality_x_anatomy_x_injury_x_fracture_detail_x_encounter
  Slots:   [LATERALITY, ANATOMY, INJURY, FRACTURE_DETAIL, ENCOUNTER]

  Example:
    "left" + "femur" + "fracture" + "displaced" + "subsequent"
      -> matches "displaced fracture of shaft of left femur,
                  subsequent encounter for closed fracture with routine healing"
```

#### Top 20 Templates by Coverage

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

The top 5 templates cover ~80% of all matched terms. The 2-slot templates are the workhorses of the grammar. Note that a single ICD term may be matched by multiple templates (e.g., "displaced fracture of shaft of left femur, initial encounter" matches `anatomy_x_condition`, `injury_x_encounter`, `anatomy_x_laterality_x_injury_x_encounter`, and more). A term is counted as "covered" if it matches **at least one** template.

### 3c. Core Term Extraction

To complement the grammar-based matching, **core terms** (anchors) are extracted from ICD-10-CM titles. A core term represents the most essential concept within a diagnosis description. Once identified, these core terms are expanded into multiple lexical variations to improve matching robustness.

For example, given the description "Patient's noncompliance with other medical treatment and regimen due to unspecified reason," the extracted core term is `patient's noncompliance`. From this anchor, variations such as `pt noncompliance` and other common abbreviations can be generated.

#### Core Terms Pipeline

```
icd10cm_order_2026.txt
    + ai_extraction_checkpoint.jsonl
    + slot_vocabularies.json
    |
    v
extract_core_terms.py   ->  core_terms.txt          (11,157 ICD-derived)
    |
    v
expand_with_templates.py ->  core_terms.txt          (+ 5,549 template-expanded)
(uses slot_vocabularies.json + family_templates.json)
    |
    v
generate_variations.py  ->  core_terms_variations.txt (clean)
(uses slot_vocabularies.json)
    |
    v
mark_ambiguous.py       ->  core_terms_variations.txt (with * flags)
```

| Output File | Description |
|---|---|
| `core_terms.txt` | 16,706 cleaned core medical terms, one per line |
| `core_terms_variations.txt` | Same terms with all variations on one line, separated by `;` |

Lines prefixed with `*` are flagged as ambiguous (high false-positive risk). 20 of 16,706 terms (0.1%) are flagged.

> **Quality Note:** An earlier version generated 17,671 terms, including 965 invalid patterns from using adjectival anatomy forms in noun positions (e.g., "abscess of cardiac"). After the adjective/noun vocabulary separation, the output was reduced to 16,706 terms -- all grammatically valid.

#### Step 1: Extract Core Terms (`extract_core_terms.py`)

Reads the fixed-width ICD-10-CM order file and strips qualifiers, encounter types, laterality prefixes, severity/stage markers, and specificity suffixes. Filters out terms starting with digits, terms over 6 words, and single generic words.

After extraction, cross-references `ai_extraction_checkpoint.jsonl` (AI quality review): terms the AI rejected are dropped, terms the AI approved use the AI's canonical form, and AI-approved terms not reachable by the regex path are added as bonus coverage.

**Elements stripped:**

| Element Category | Examples |
|---|---|
| Etiologic qualifiers | `due to`, `caused by`, `secondary to`, `following`, `complicating` |
| Encounter types | `initial encounter`, `subsequent encounter`, `sequela` |
| Laterality prefixes | `left`, `right`, `bilateral` (driven by `LATERALITY_TOKENS` from `slot_vocabularies.json`) |
| Disease episode qualifiers | `in relapse`, `in remission`, `not having achieved remission` |
| Severity/stage | `mild`, `moderate`, `severe`, `stage`, `grade` |
| Specificity suffixes | `unspecified`, `NEC`, `NOS` |
| Prefixes | `Other`, `Unspecified`, `Encounter for` |

**Example:** `bilateral inguinal hernia` -> `inguinal hernia` (laterality stripped)

#### Step 2: Expand with Templates (`expand_with_templates.py`)

Uses `family_templates.json` and `slot_vocabularies.json` to generate anatomically-varied forms not present in ICD.

For each condition token with >=3 attested anatomy variants, generates the missing `condition of anatomy` combinations -- producing clinically valid terms like `carcinoma of thyroid`, `tuberculosis of knee`, `thrombosis of aorta` that are absent from ICD under that exact form.

| Parameter | Default | Effect |
|---|---|---|
| `MIN_ATTESTATIONS` | 3 | Minimum attested anatomy variants before expanding a condition |
| `SKIP_CONDITIONS` | see file | Conditions too generic to expand safely |
| `ADJECTIVAL_ANATOMY` | see file | Anatomy tokens that are adjectives, excluded from `of [anatomy]` position |

**Top productive conditions:** thrombosis (+122 terms), hernia (+121), ischemia (+121)

#### Step 3: Generate Variations (`generate_variations.py`)

For each core term generates:

- **Plural forms** -- rule-based, handles Latin/Greek irregular plurals (`calculus` -> `calculi`, `diagnosis` -> `diagnoses`)
- **Word-order reordering** -- "disorder of heart" <-> "heart disorder" -- gated on `ANATOMY_TOKENS`
- **Abbreviations & synonyms** -- ~120 common conditions (`hypertension` -> `HTN`, `high blood pressure`)
- **Anatomical substitutions** -- `cardiac` -> `heart`, `renal` -> `kidney`, `hepatic` -> `liver`, etc.
- **US/UK spelling variants** -- `anemia` <-> `anaemia`, `edema` <-> `oedema`, `hemorrhage` <-> `haemorrhage`, etc.
- **Bracketed abbreviations from source** -- `[ECG]`, `[EKG]`, `[EOG]` extracted as separate variations

#### Step 4: Flag Ambiguous Terms (`mark_ambiguous.py`)

Prepends `*` to terms that are ambiguous in a DLP context:

| Category | Examples |
|---|---|
| Environmental / external-cause codes | `bathroom`, `earthquake`, `tornado`, `motorcycle` |
| Generic clinical descriptors | `conditions`, `diseases`, `aftercare`, `onset`, `subacute` |
| Common words with non-medical uses | `stress`, `stroke`, `depression`, `shock`, `headache` |
| Medical terms that double as everyday words | `allergy`, `amnesia`, `jaundice`, `tremor`, `polyp` |

---

## Stage 4: Validation

The pipeline includes automated validation tools to ensure structural integrity, measure precision, and identify improvements. All scripts are **stdlib-only Python 3.9+**, read-only by default, and output machine-readable JSON + human summary to stdout.

### Validation Pipeline

```
    slot_vocabularies.json ----+---- family_templates.json
                               |
    ICD-10-CM Source CSV ------+
                               |
         +---------------------+---------------------+
         |                     |                     |
         v                     v                     v
    validate.py          precision.py          reconcile.py
    (structural +        (token specificity +  (JSON vs Python
     ground-truth)        FP risk scoring)      analyzer diff)
         |                     |                     |
         v                     v                     v
    validation_           precision_            reconciliation_
    report.json           report.json           report.json
         |
         v
    suggest.py  -->  changeset.json  -->  apply.py  -->  Updated production files
```

### Structural Validation (`validate.py`)

Performs four categories of checks:

**Structural sanity:**
- Validates that all template vocabulary references point to existing vocabularies
- Detects intra-vocabulary duplicate tokens
- Verifies metadata counts (slots, tokens, families) match actual data

**Token health:**
- Identifies zero-hit tokens (tokens that don't appear in any ICD-10-CM term)
- Categorizes zero-hit tokens: British spellings (kept intentionally), location prefixes (kept), or problematic (flagged for removal)
- Detects cross-slot overlap (same token in multiple vocabularies -- can cause ambiguous matching)

**Template health:**
- Identifies orphaned vocabularies (defined but not referenced by any template -- dead weight)
- Detects order-variant template groups (same vocabulary slots in different order -- redundant)

**Ground-truth co-occurrence:**
- For each template, checks whether token combinations from its slots actually co-occur in real ICD-10-CM terms
- Templates with smaller cross-products (<= 50,000 combos) are checked exhaustively; larger ones are sampled (500 random combinations)
- This is an internal diagnostic metric used to identify templates that may be too specific or misconfigured -- it does NOT measure the grammar's coverage or precision (those are measured in Stage 5)

Example output:
```
  VALIDATION REPORT -- PASS
  Vocab version: 2026-04-10-v8

  Structural:
    Broken vocab refs:    0
    Intra-vocab dupes:    0
    Metadata slots:       39 OK
    Metadata tokens:      1273 OK
    Metadata families:    90 OK

  Token health:
    Zero-hit tokens:      105
    Cross-slot overlaps:  15
```

### Precision Analysis (`precision.py`)

Scores every token for **medical specificity** and every template for **DLP false-positive risk**. This is the core safety check for the grammar.

**Token specificity scoring:**

Each of the 1,273 tokens is classified:
- **HIGH** (medical-specific): Appears in ICD-10-CM and is NOT a common English word. Examples: `fracture`, `hemorrhage`, `femur`, `pneumonia`, `stenosis`, `thrombosis`
- **MEDIUM**: Not common English, but also not found in ICD (e.g., British spelling variants like `anaemia`, `oedema`)
- **LOW** (common English): Appears in everyday non-medical text. Examples: `head`, `back`, `left`, `right`, `stress`, `depression`, `burn`

| Specificity | Count | Percentage |
|---|---|---|
| HIGH (medical-only) | 1,169 | 91.8% |
| MEDIUM | 28 | 2.2% |
| LOW (common English) | 76 | 6.0% |

**Template FP risk scoring:**

For each template, the analysis computes the probability that a random token combination from its cross-product would consist **entirely** of common English words (i.e., would match non-medical text):

- **HIGH risk**: P(all slots use low-specificity tokens) > 1%. These templates are dangerous for DLP because they can generate patterns like "left back pain" that would match everyday English.
- **MEDIUM risk**: P(all low) between 0.1%-1%, or template has cross-slot token collisions.
- **LOW risk**: Minimal chance of generating common-English-only patterns.

| FP Risk Level | Templates | Action |
|---|---|---|
| **HIGH** | **0** | None needed -- all high-risk templates have been removed |
| MEDIUM | 21 | Monitored, acceptable |
| LOW | 69 | Safe |

**Cross-slot collision detection** also identifies templates where two vocabulary slots share tokens. For example, if "fracture" appears in both `INJURY_TOKENS` and `CONDITION_TOKENS`, a template using both slots could match the same word twice, inflating apparent coverage.

### Changeset Pipeline (`suggest.py` + `apply.py`)

**suggest.py** reads the validation report and proposes a concrete, machine-readable changeset of modifications:
- Suggests removing problematic zero-hit tokens
- Flags cross-slot overlaps requiring human judgment
- Proposes templates for orphaned vocabularies or their removal
- Suggests consolidating order-variant template duplicates
- Corrects metadata mismatches

**apply.py** applies the changeset to production files with safety guarantees:
- **Dry-run mode** (default): Shows what would change without writing
- **Timestamped backups** before any mutation
- **Pre-flight and post-flight structural checks**
- **Automatic rollback** if post-flight validation fails
- **Idempotent**: Skips already-applied changes

Example:
```bash
# Preview changes (safe, default)
python3 scripts/apply.py

# Actually apply
python3 scripts/apply.py --apply

# Output:
#   Pre-flight structural check... PASS
#   + Removed 'neosplasm' from DIAGNOSTIC_CLASSIFIER_TOKENS
#   + Added 'subluxation' to INJURY_TOKENS
#   + Added template 'pathogen_x_condition' (2 slots)
#   Post-flight structural check... PASS
#   Final verification... PASS
#   Changes applied successfully. Version: 2026-04-10-v8
```

### Reconciliation (`reconcile.py`)

Compares the validated JSON vocabularies with the legacy analyzer's hardcoded Python sets:

- **Identical:** Vocabulary matches exactly between JSON and Python
- **Diverged:** Same vocabulary exists in both but with different tokens
- **JSON-only:** Vocabulary exists in JSON but not in the Python analyzer
- **Python-only:** Vocabulary exists in the Python analyzer but not in JSON

> **Critical Finding:** The main analyzer (`analyze_compositionality.py`) historically used **hardcoded Python sets**, not `slot_vocabularies.json`. This meant vocabulary improvements to the JSON files had no effect on the analyzer's coverage metrics. This finding led to the architectural decision to reconcile the two sources and ensure the JSON files serve as the single source of truth.

---

## Stage 5: Coverage Testing and Model Improvement

This stage measures the grammar's actual performance against the enriched ICD-10-CM corpus and documents the improvement cycle that brought coverage from 84.37% to 92.70%.

### How Coverage Is Measured

A term is **covered** if at least one template matches it -- meaning all of that template's slot tokens co-occur in the term. Coverage is the fraction of the 335,538 enriched ICD-10-CM terms matched by the grammar.

```
                                         +---------+
335,538 ICD-10-CM terms  ------------>   | Grammar |  ----> 311,048 matched (92.70%)
(enriched corpus from Stage 2)           | (39 vocabs, |       24,490 unmatched (7.30%)
                                         |  90 templates)|
                                         +---------+
```

### Current Coverage

| Metric | Value |
|---|---|
| Total ICD-10-CM terms (enriched) | 335,538 |
| Matched by grammar | 311,048 |
| **Coverage** | **92.70%** |
| Unmatched | 24,490 |
| HIGH FP-risk templates | **0** |
| Token specificity (medical-only) | 91.8% |

### Coverage History

| Version | Coverage | Terms Matched | Templates | Tokens | Key Change |
|---|---|---|---|---|---|
| v1 (baseline) | 84.37% | 283,081 | 56 | 1,018 | Initial pipeline validation |
| v5 (pre-expansion) | 84.37% | 283,081 | 56 | 1,213 | Collision fixes + reconciliation |
| v6 (+abbreviations) | ~86% | ~288,000 | 56 | 1,273 | Added ICD_ABBREVIATION_TOKENS (60 tokens) |
| v7 (+36 templates) | 93.63% | 314,171 | 92 | 1,273 | Added 36 new templates |
| **v8 (current)** | **92.70%** | **311,048** | **90** | **1,273** | Removed 2 HIGH FP-risk templates |

### Key Improvement Actions

The following improvements drove coverage from **84.37% to 92.70%**:

**1. ICD Abbreviation Vocabulary (+60 tokens, ~+2% coverage)**

Created `ICD_ABBREVIATION_TOKENS` with high-frequency CMS-specific abbreviations (`clsn`, `physl`, `femr`, `displ`, etc.) -- each appearing in 1,500-16,000 ICD terms. These abbreviations are unique to CMS coding conventions and do not overlap with common English, making them precision-safe.

**2. Orphaned Vocabulary Templates (+24 templates, ~+5% coverage)**

Fourteen vocabulary slots (148 tokens) had been defined but were not referenced by any template, meaning they contributed nothing to coverage. New templates were created to wire them in: `pathogen_x_condition`, `neoplasm_x_anatomy`, `seizure_x_condition`, `diagnostic_event_x_injury`, etc.

**3. Missing Template Combinations (+12 templates, ~+4% coverage)**

Gap analysis identified high-value slot combinations that had no template: `encounter_x_mechanism`, `anatomy_x_qualifier`, `condition_x_diagnostic_classifier`, etc. These captured common ICD patterns that fell through the gaps.

**4. FP Risk Cleanup (-2 templates, -0.93% coverage)**

Removed 2 templates (`anatomy_x_laterality` and `ulcer_x_anatomy`) that the precision analysis flagged as HIGH FP-risk. These templates could generate patterns composed entirely of common English words (e.g., "left back", "right arm"). The deliberate trade of **-0.93% coverage for zero HIGH FP-risk templates** reflects the pipeline's priority: **precision over recall**.

**5. Vocabulary Quality Fixes**

Removed misspelled tokens (`neosplasm`), reclassified tokens across slots (`subluxation` moved from CONDITION to INJURY where it semantically belongs), and resolved cross-slot collisions.

**6. Adjective/Noun Separation**

Created `ANATOMY_ADJECTIVE_TOKENS` (42 tokens) and removed adjectival forms from `ANATOMY_TOKENS`. This eliminated 965 invalid generated patterns in the core terms pipeline (e.g., "abscess of cardiac" -> "abscess of heart").

### Critical Discovery: Templates Are the Bottleneck

A key finding during improvement: adding 29 vocabulary tokens had **zero impact** on coverage because no templates existed to use them. Vocabulary and templates must be co-developed.

Evidence: From v5 to v7, **zero new tokens were added** but 36 new templates were created. Coverage jumped from **84.37% to 93.63%** (+9.26%). Template gaps have roughly **10x more impact** than vocabulary gaps.

### Gap Analysis -- What Remains

The 24,490 unmatched terms (7.3% of total) consist of:

| Category | Estimated Count | Description |
|---|---|---|
| Named diseases & syndromes | ~5,000 | Wilson disease, Kawasaki syndrome, etc. -- proper nouns not in vocabulary |
| Heavily abbreviated terms | ~8,000 | Terms with rare ICD abbreviations beyond the top 60 |
| Rare/specialized vocabulary | ~6,000 | Specialized pathology, genetics, rare anatomical terms |
| Single-word / no-vocab terms | ~5,490 | Terms with 0-1 known tokens, requiring domain-specific vocabularies |

---

## Stage 6: Next Steps

### Remaining Opportunities

| Opportunity | Estimated Impact | Complexity | FP Risk |
|---|---|---|---|
| Additional ICD abbreviations (~100 rare abbrevs) | +1-2% | Low | Low |
| Anatomical sub-specialties (muscles, vessels, nerves) | +0.5-1% | Low | Low |
| Named disease vocabulary (proper nouns) | +0.5-1% | Medium | Medium |
| Transport/external cause expansion | +0.5% | Low | Low |
| UMLS/CHV cross-vocabulary integration | TBD | Medium | Low |
| **Theoretical ceiling** | **~95-96%** | -- | -- |

### Guiding Principles

1. **Precision over recall.** Every addition must pass FP-risk analysis. Coverage was already reduced from 93.63% to 92.70% to eliminate high-risk templates. Further coverage gains must not compromise this.
2. **Templates and vocabularies together.** New vocabulary tokens are useless without corresponding templates. Every vocabulary addition must include template wiring.
3. **Empirical validation.** All changes are tested against the full enriched ICD-10-CM corpus. Token health, structural integrity, and FP-risk are checked before and after every change.
4. **Quality over quantity.** Smaller, cleaner vocabularies outperform larger, noisier ones. The removal of 965 invalid core term patterns demonstrated that fewer, more precise entries improve the overall system.

---

## Data Products

| File | Format | Description |
|---|---|---|
| `slot_vocabularies.json` | JSON | 39 vocabulary slots, 1,273 tokens -- the lexicon |
| `family_templates.json` | JSON | 90 template families -- the production rules |
| `medical_conditions.xml` | XML | DLP-ready medical condition patterns (prefixes, roots, entities) |
| `icd10cm_core_terms.txt` | Text | 11,157 validated ICD-10-CM core terms for regex anchors |

All production data is version-tracked. Current version: `2026-04-10-v8`.

### Pipeline Usage

```bash
# 1. Validate structural integrity + ground-truth
python3 scripts/validate.py

# 2. Generate improvement suggestions
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

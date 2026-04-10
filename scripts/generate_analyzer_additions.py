#!/usr/bin/env python3
"""
Generate Code Snippets for analyze_compositionality.py

Creates ready-to-paste code snippets to add critical vocabularies and templates.
"""

print("=" * 80)
print("CODE ADDITIONS FOR analyze_compositionality.py")
print("=" * 80)
print()

print("# STEP 1: Add ANATOMY_ADJECTIVE_TOKENS constant")
print("# Location: After ANATOMY_TOKENS definition (around line 450)")
print("#" * 80)
print()
print("ANATOMY_ADJECTIVE_TOKENS = {")
tokens = [
    "abdominal", "aortic", "cardiac", "cerebral", "cervical",
    "conjunctival", "corneal", "cutaneous", "fascicular", "intestinal",
    "myocardial", "orbital", "peritoneal", "pulmonary", "retinal",
    "spinal", "thoracic", "tibial", "urethral", "urinary",
    "uterine", "ventricular", "chorioretinal", "dental",
    "intracerebral", "intracranial", "labial", "lacrimal",
    "ulnohumeral", "umbilical", "nasopharyngeal", "gastrointestinal",
    "renal", "macular", "lymphocytic", "diabetic", "postprocedural",
    "paralytic", "mental", "physiological", "magnetic"
]
for i, token in enumerate(sorted(tokens)):
    if i < len(tokens) - 1:
        print(f'    "{token}",')
    else:
        print(f'    "{token}"')
print("}")
print()

print()
print("# STEP 2: Add tokens to CONDITION_TOKENS")
print("# Location: Inside CONDITION_TOKENS set definition")
print("#" * 80)
print()
condition_tokens = [
    "gout", "osteoporosis", "diabetes", "dementia",
    "hemiplegia", "thalassemia", "malaria"
]
for token in sorted(condition_tokens):
    print(f'    "{token}",')
print()

print()
print("# STEP 3: Add tokens to ANATOMY_TOKENS")
print("# Location: Inside ANATOMY_TOKENS set definition")
print("#" * 80)
print()
anatomy_tokens = [
    "tophus", "tophi", "meniscus", "adnexa", "organ", "tissue"
]
for token in sorted(anatomy_tokens):
    print(f'    "{token}",')
print()

print()
print("# STEP 4: Add tokens to MODIFIER_WITH_TOKENS")
print("# Location: Inside MODIFIER_WITH_TOKENS set definition")
print("#" * 80)
print()
modifier_tokens = [
    "pressure", "retained", "psychoactive", "bypass",
    "lead", "foreign", "solid"
]
for token in sorted(modifier_tokens):
    print(f'    "{token}",')
print()

print()
print("# STEP 5: Add critical template families")
print("# Location: Inside EXPLICIT_TEMPLATE_FAMILIES dict (around line 1471)")
print("#" * 80)
print()
print("""    # CRITICAL TEMPLATES FOR COVERAGE IMPROVEMENT (2026-03-27)
    # Expected impact: +6-8% coverage (~25,000 terms)
    "anatomy_adjective_x_condition": [
        ("anatomy_adjective", ANATOMY_ADJECTIVE_TOKENS),
        ("condition", CONDITION_TOKENS)
    ],
    "qualifier_x_anatomy_adjective_x_condition": [
        ("qualifier", QUALIFIER_TOKENS),
        ("anatomy_adjective", ANATOMY_ADJECTIVE_TOKENS),
        ("condition", CONDITION_TOKENS)
    ],
    "anatomy_adjective_x_condition_high": [
        ("anatomy_adjective", ANATOMY_ADJECTIVE_TOKENS),
        ("condition_high", CONDITION_HIGH_TOKENS)
    ],
    "laterality_x_anatomy_adjective_x_condition": [
        ("laterality", LATERALITY_TOKENS),
        ("anatomy_adjective", ANATOMY_ADJECTIVE_TOKENS),
        ("condition", CONDITION_TOKENS)
    ],
""")

print()
print("=" * 80)
print("TESTING INSTRUCTIONS")
print("=" * 80)
print()
print("After adding the code above:")
print()
print("1. Save analyze_compositionality.py")
print("2. Run the analyzer:")
print("   cd /home/bguide/compositional_analysis")
print("   python3 analyze_compositionality.py")
print()
print("3. Check coverage in analysis_outputs/summary.md")
print("   Expected: Coverage increases from 55.36% to ~61-63%")
print()
print("4. If successful, add more templates iteratively:")
print("   - anatomy_adjective_x_condition_x_modifier_with")
print("   - anatomy_adjective_x_condition_low")
print("   - etc.")
print()
print("=" * 80)
print("EXPECTED MATCHES")
print("=" * 80)
print()
print("Sample terms that should now match:")
print("  - nasopharyngeal diphtheria (anatomy_adjective_x_condition)")
print("  - cutaneous listeriosis (anatomy_adjective_x_condition)")
print("  - gastrointestinal tularemia (anatomy_adjective_x_condition)")
print("  - acute renal disease (qualifier_x_anatomy_adjective_x_condition)")
print("  - chronic pulmonary disorder (qualifier_x_anatomy_adjective_x_condition_high)")
print("  - left cerebral infarction (laterality_x_anatomy_adjective_x_condition)")
print()
print("Estimated new matches: 23,600-31,500 terms (+6-8% coverage)")
print()

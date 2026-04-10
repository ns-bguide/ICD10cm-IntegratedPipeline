#!/usr/bin/env python3
"""
Analyze Unmatched Terms to Identify Coverage Gaps

Systematically analyzes unmatched terms to identify:
1. Missing vocabulary tokens (frequent words not in vocabularies)
2. Missing template patterns (structural gaps)
3. Vocabulary quality issues (noise, stopwords)
4. Prioritized improvements by impact
"""

import json
import re
from pathlib import Path
from collections import Counter, defaultdict

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MAIN_PROJECT = Path("/home/bguide/compositional_analysis")
INPUT_FILE = MAIN_PROJECT / "icd10cm_terms_2026_full_with_chv_core.csv"
ASSIGNMENTS_FILE = MAIN_PROJECT / "analysis_outputs" / "term_family_assignments.csv"
SLOT_VOC_FILE = BASE_DIR / "reference_data" / "slot_vocabularies.json"
OUTPUT_REPORT = BASE_DIR / "analysis_outputs" / "unmatched_analysis_report.md"
OUTPUT_JSON = BASE_DIR / "analysis_outputs" / "coverage_improvement_plan.json"

def load_vocabularies():
    """Load slot vocabularies."""
    with open(SLOT_VOC_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    vocabs = {}
    for category, slots in data['categories'].items():
        for slot_name, tokens in slots.items():
            vocabs[slot_name] = set(t.lower() for t in tokens)

    return vocabs

def load_unmatched_terms(limit=50000):
    """Load sample of unmatched terms by comparing input vs matched."""
    import csv

    # Load matched terms into a set
    print("  Loading matched terms...")
    matched_terms = set()
    with open(ASSIGNMENTS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            term = row['term'].lower()
            matched_terms.add(term)
    print(f"  Loaded {len(matched_terms):,} matched terms")

    # Load all terms and filter for unmatched
    print("  Loading all terms and filtering for unmatched...")
    unmatched = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            term = row['Term']
            if term.lower() not in matched_terms:
                unmatched.append(term)
                if len(unmatched) >= limit:
                    break

    return unmatched

def tokenize_term(term):
    """Extract meaningful words from term."""
    # Remove parenthetical content
    term = re.sub(r'\([^)]*\)', '', term)
    # Split into words
    words = re.findall(r'\b[a-z]{3,}\b', term.lower())
    return words

def analyze_word_frequency(terms, vocabs):
    """Analyze frequency of words in unmatched terms."""
    all_vocab_tokens = set()
    for vocab in vocabs.values():
        all_vocab_tokens.update(vocab)

    word_freq = Counter()
    missing_words = Counter()

    for term in terms:
        words = tokenize_term(term)
        for word in words:
            word_freq[word] += 1
            if word not in all_vocab_tokens:
                missing_words[word] += 1

    return word_freq, missing_words

def categorize_missing_words(missing_words, threshold=100):
    """Categorize high-frequency missing words."""
    # Common stopwords that shouldn't be in vocabularies
    stopwords = {
        'the', 'and', 'or', 'with', 'without', 'for', 'from', 'into', 'onto',
        'during', 'after', 'before', 'under', 'over', 'between', 'through',
        'not', 'nos', 'nec', 'other', 'specified', 'unspecified', 'type',
        'code', 'codes', 'affecting', 'involving', 'associated', 'related'
    }

    high_freq = []
    potential_anatomy = []
    potential_condition = []
    potential_qualifier = []

    for word, count in missing_words.most_common(200):
        if count < threshold:
            break

        if word in stopwords:
            continue

        # Heuristic categorization
        if word.endswith(('itis', 'osis', 'oma', 'pathy', 'ia', 'ism')):
            potential_condition.append((word, count))
        elif word.endswith(('al', 'ic', 'ous', 'ary')):
            potential_qualifier.append((word, count))
        else:
            # Could be anatomy or condition
            high_freq.append((word, count))

    return {
        'high_frequency': high_freq[:50],
        'potential_conditions': potential_condition[:30],
        'potential_qualifiers': potential_qualifier[:30]
    }

def analyze_term_patterns(terms, limit=1000):
    """Analyze structural patterns in unmatched terms."""
    length_dist = Counter()
    word_count_dist = Counter()
    pattern_examples = defaultdict(list)

    for term in terms[:limit]:
        words = tokenize_term(term)
        word_count = len(words)

        word_count_dist[word_count] += 1
        length_dist[len(term)] += 1

        # Capture pattern examples
        if word_count <= 3 and len(pattern_examples[word_count]) < 5:
            pattern_examples[word_count].append(term)

    return {
        'word_count_distribution': dict(word_count_dist.most_common(10)),
        'pattern_examples': dict(pattern_examples)
    }

def identify_coverage_gaps(vocabs, missing_categorized):
    """Identify specific vocabulary gaps."""
    gaps = {
        'anatomy': [],
        'condition': [],
        'qualifier': []
    }

    # Analyze potential additions
    for word, count in missing_categorized['high_frequency']:
        # Simple heuristics - would need domain expert review
        if count > 500:
            if any(word in known for known in ['organ', 'body', 'part', 'area', 'region']):
                gaps['anatomy'].append({'word': word, 'frequency': count, 'confidence': 'medium'})
            else:
                gaps['condition'].append({'word': word, 'frequency': count, 'confidence': 'low'})

    for word, count in missing_categorized['potential_conditions']:
        gaps['condition'].append({'word': word, 'frequency': count, 'confidence': 'high'})

    for word, count in missing_categorized['potential_qualifiers']:
        gaps['qualifier'].append({'word': word, 'frequency': count, 'confidence': 'medium'})

    return gaps

def estimate_coverage_impact(missing_words, total_unmatched):
    """Estimate potential coverage gain from adding tokens."""
    # Top 50 missing words
    top_missing = missing_words.most_common(50)
    total_occurrences = sum(count for _, count in top_missing)

    # Rough estimate: each occurrence might help match a term
    # Conservative: assume only 30% of terms with that word will match
    estimated_terms_helped = int(total_occurrences * 0.3)
    estimated_coverage_gain = (estimated_terms_helped / total_unmatched) * 100

    return {
        'top_50_words_occurrences': total_occurrences,
        'estimated_terms_matchable': estimated_terms_helped,
        'estimated_coverage_gain_pct': round(estimated_coverage_gain, 2)
    }

def generate_report(analysis):
    """Generate markdown report."""
    lines = [
        "# Unmatched Terms Analysis - Coverage Improvement Plan",
        "",
        f"**Goal**: Increase coverage from 55.36% to 70%+ (need +14.64% = ~57,700 additional terms)",
        f"**Unmatched terms analyzed**: {analysis['unmatched_count']:,}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"- **Total unique words in unmatched terms**: {analysis['total_unique_words']:,}",
        f"- **High-frequency missing words** (>100 occurrences): {len(analysis['missing_categorized']['high_frequency'])}",
        f"- **Potential condition tokens**: {len(analysis['missing_categorized']['potential_conditions'])}",
        f"- **Potential qualifier tokens**: {len(analysis['missing_categorized']['potential_qualifiers'])}",
        "",
        "### Estimated Impact",
        "",
        f"Adding top 50 missing words could:",
        f"- Help match **~{analysis['impact']['estimated_terms_matchable']:,} terms**",
        f"- Increase coverage by **~{analysis['impact']['estimated_coverage_gain_pct']}%**",
        f"- New estimated coverage: **~{55.36 + analysis['impact']['estimated_coverage_gain_pct']:.2f}%**",
        "",
        "---",
        "",
        "## 1. Word Frequency Analysis",
        "",
        "### Top 50 High-Frequency Missing Words",
        "",
        "Words appearing >100 times in unmatched terms but NOT in any vocabulary:",
        "",
        "| Rank | Word | Frequency | Suggested Slot |",
        "|------|------|-----------|----------------|",
    ]

    for i, (word, count) in enumerate(analysis['missing_categorized']['high_frequency'], 1):
        lines.append(f"| {i} | `{word}` | {count:,} | TBD |")

    lines.extend([
        "",
        "### Potential Condition Tokens",
        "",
        "Words with medical condition suffixes (-itis, -osis, -oma, -pathy, -ia):",
        "",
        "| Word | Frequency | Confidence |",
        "|------|-----------|------------|",
    ])

    for word, count in analysis['missing_categorized']['potential_conditions']:
        lines.append(f"| `{word}` | {count:,} | High |")

    lines.extend([
        "",
        "### Potential Qualifier Tokens",
        "",
        "Words with adjectival suffixes (-al, -ic, -ous, -ary):",
        "",
        "| Word | Frequency | Confidence |",
        "|------|-----------|------------|",
    ])

    for word, count in analysis['missing_categorized']['potential_qualifiers']:
        lines.append(f"| `{word}` | {count:,} | Medium |")

    lines.extend([
        "",
        "---",
        "",
        "## 2. Structural Pattern Analysis",
        "",
        "### Word Count Distribution in Unmatched Terms",
        "",
        "| Words per Term | Count | Pattern Examples |",
        "|----------------|-------|------------------|",
    ])

    for word_count, count in sorted(analysis['patterns']['word_count_distribution'].items()):
        examples = analysis['patterns']['pattern_examples'].get(word_count, [])
        example_str = "; ".join(examples[:2]) if examples else "-"
        lines.append(f"| {word_count} | {count:,} | {example_str} |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Coverage Improvement Strategy",
        "",
        "### Phase 1: Quick Wins (Target: +5-8% coverage)",
        "",
        "**Action**: Add high-confidence missing tokens to existing vocabularies",
        "",
        "1. **CONDITION_TOKENS additions** (~20 tokens)",
        "   - Medical condition suffixes identified",
        "   - Frequency >200 in unmatched terms",
        "   - Example: conditions ending in -itis, -osis, -oma",
        "",
        "2. **QUALIFIER_TOKENS additions** (~15 tokens)",
        "   - Adjectival forms frequently appearing",
        "   - Frequency >150 in unmatched terms",
        "",
        "3. **ANATOMY_TOKENS additions** (~10 tokens)",
        "   - Body parts/regions not currently captured",
        "   - Frequency >100 in unmatched terms",
        "",
        "**Estimated impact**: +20,000-30,000 terms matched (5-8% coverage gain)",
        "",
        "### Phase 2: Template Expansion (Target: +4-6% coverage)",
        "",
        "**Action**: Create new template families for unmatched patterns",
        "",
        "Based on word count analysis:",
        "- 2-word terms: Check for missing simple templates",
        "- 3-word terms: Analyze for common structures",
        "- 4+ word terms: Identify complex patterns needing new templates",
        "",
        "**Estimated impact**: +15,000-25,000 terms matched (4-6% coverage gain)",
        "",
        "### Phase 3: Specialized Vocabularies (Target: +3-5% coverage)",
        "",
        "**Action**: Create domain-specific slot vocabularies",
        "",
        "Potential new slots:",
        "- `PROCEDURE_DETAIL_TOKENS` - surgical/procedure specifics",
        "- `TEMPORAL_TOKENS` - time-related qualifiers",
        "- `CAUSATION_TOKENS` - cause/effect relationships",
        "- `NEGATION_TOKENS` - negative/absence indicators",
        "",
        "**Estimated impact**: +12,000-20,000 terms matched (3-5% coverage gain)",
        "",
        "---",
        "",
        "## 4. Immediate Action Items",
        "",
        "### Priority 1: Add Top Condition Tokens",
        "",
        "Review and add these to CONDITION_TOKENS:",
    ])

    for word, count in analysis['missing_categorized']['potential_conditions'][:10]:
        lines.append(f"- [ ] `{word}` (frequency: {count:,})")

    lines.extend([
        "",
        "### Priority 2: Add Top Qualifier Tokens",
        "",
        "Review and add these to QUALIFIER_TOKENS:",
    ])

    for word, count in analysis['missing_categorized']['potential_qualifiers'][:10]:
        lines.append(f"- [ ] `{word}` (frequency: {count:,})")

    lines.extend([
        "",
        "### Priority 3: Manual Review Required",
        "",
        "High-frequency words needing domain expert classification:",
    ])

    for word, count in analysis['missing_categorized']['high_frequency'][:20]:
        lines.append(f"- [ ] `{word}` (frequency: {count:,}) → Which slot?")

    lines.extend([
        "",
        "---",
        "",
        "## 5. Testing Plan",
        "",
        "After each phase:",
        "",
        "1. **Add tokens** to vocabularies",
        "2. **Export** improved vocabularies",
        "3. **Re-run** main analyzer",
        "4. **Measure** coverage delta",
        "5. **Validate** no regressions",
        "6. **Document** changes",
        "",
        "**Target progression**:",
        "- Baseline: 55.36%",
        "- After Phase 1: ~60-63%",
        "- After Phase 2: ~65-68%",
        "- After Phase 3: ~70%+",
        "",
        "---",
        "",
        "## Next Steps",
        "",
        "1. **Review this report** with domain experts",
        "2. **Classify high-frequency missing words** into appropriate slots",
        "3. **Start with Phase 1** (quick wins - vocabulary additions)",
        "4. **Measure impact** after each addition",
        "5. **Iterate** until 70% coverage achieved",
        "",
        "---",
        "",
        "**Generated by**: `analyze_unmatched_terms.py`",
        f"**Unmatched terms sampled**: {analysis['unmatched_count']:,}",
        "**Recommended**: Review top 50 missing words with medical terminology expert",
    ])

    return "\n".join(lines)

def main():
    print("=" * 80)
    print("ANALYZING UNMATCHED TERMS FOR COVERAGE IMPROVEMENT")
    print("=" * 80)
    print()

    print("Loading vocabularies...")
    vocabs = load_vocabularies()
    print(f"  ✓ Loaded {len(vocabs)} vocabulary slots")

    print("Loading unmatched terms...")
    unmatched = load_unmatched_terms(limit=50000)
    print(f"  ✓ Loaded {len(unmatched):,} unmatched terms")

    print("\nAnalyzing word frequencies...")
    word_freq, missing_words = analyze_word_frequency(unmatched, vocabs)
    print(f"  ✓ Total unique words: {len(word_freq):,}")
    print(f"  ✓ Missing words (not in vocab): {len(missing_words):,}")

    print("Categorizing missing words...")
    missing_categorized = categorize_missing_words(missing_words)
    print(f"  ✓ High-frequency missing: {len(missing_categorized['high_frequency'])}")
    print(f"  ✓ Potential conditions: {len(missing_categorized['potential_conditions'])}")
    print(f"  ✓ Potential qualifiers: {len(missing_categorized['potential_qualifiers'])}")

    print("Analyzing term patterns...")
    patterns = analyze_term_patterns(unmatched)
    print(f"  ✓ Word count distribution captured")

    print("Estimating coverage impact...")
    total_unmatched = 175816  # From latest run
    impact = estimate_coverage_impact(missing_words, total_unmatched)
    print(f"  ✓ Estimated coverage gain: ~{impact['estimated_coverage_gain_pct']}%")

    # Compile analysis
    analysis = {
        'unmatched_count': len(unmatched),
        'total_unique_words': len(word_freq),
        'missing_words_count': len(missing_words),
        'missing_categorized': missing_categorized,
        'patterns': patterns,
        'impact': impact
    }

    print("\nGenerating report...")
    report = generate_report(analysis)
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  ✓ Saved: {OUTPUT_REPORT}")

    print("Generating coverage improvement plan...")
    improvement_plan = {
        'current_coverage': 55.36,
        'target_coverage': 70.0,
        'coverage_gap': 14.64,
        'terms_needed': 57700,
        'phases': [
            {
                'phase': 1,
                'name': 'Vocabulary Additions',
                'target_gain': '5-8%',
                'actions': [
                    f'Add {len(missing_categorized["potential_conditions"][:20])} condition tokens',
                    f'Add {len(missing_categorized["potential_qualifiers"][:15])} qualifier tokens',
                    'Review and classify top 50 high-frequency words'
                ]
            },
            {
                'phase': 2,
                'name': 'Template Expansion',
                'target_gain': '4-6%',
                'actions': [
                    'Analyze 2-3 word unmatched patterns',
                    'Create missing template families',
                    'Test new templates'
                ]
            },
            {
                'phase': 3,
                'name': 'Specialized Vocabularies',
                'target_gain': '3-5%',
                'actions': [
                    'Create procedure detail vocabulary',
                    'Add temporal/causation slots',
                    'Build negation patterns'
                ]
            }
        ],
        'top_missing_words': [
            {'word': word, 'frequency': count}
            for word, count in missing_words.most_common(100)
        ]
    }

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(improvement_plan, f, indent=2)
    print(f"  ✓ Saved: {OUTPUT_JSON}")

    # Summary
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Top missing words: {len(missing_words.most_common(50))}")
    print(f"Potential conditions: {len(missing_categorized['potential_conditions'])}")
    print(f"Estimated coverage gain potential: ~{impact['estimated_coverage_gain_pct']}%")
    print()
    print(f"📊 Full report: {OUTPUT_REPORT.relative_to(BASE_DIR)}")
    print(f"📋 Improvement plan: {OUTPUT_JSON.relative_to(BASE_DIR)}")
    print()
    print("Next: Review top missing words and classify into appropriate vocabularies")
    print()

if __name__ == "__main__":
    main()

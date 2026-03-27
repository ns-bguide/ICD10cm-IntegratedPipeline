# Family Templates - Hierarchical Export

**Source**: analyze_compositionality.py
**Date**: 2026-03-25

**Total Families**: 76

**Slot Count Distribution**:
- 2-slot families: 21
- 3-slot families: 22
- 4-slot families: 16
- 5-slot families: 6
- 6-slot families: 1
- 7-slot families: 3
- 8-slot families: 1
- 9-slot families: 1

---

## Injury & Fracture Families

*Total families in category: 36*

### diagnostic_classifier_x_anatomy_x_injury_x_diagnostic_event

**Slot Count**: 4

**Slot Composition**:

1. **diagnostic_classifier** → `DIAGNOSTIC_CLASSIFIER_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **injury** → `INJURY_TOKENS`
4. **diagnostic_event** → `DIAGNOSTIC_EVENT_TOKENS`

**Template Pattern**:
```
diagnostic_classifier × anatomy × injury × diagnostic_event
```

### anatomy_x_injury_x_diagnostic_event

**Slot Count**: 3

**Slot Composition**:

1. **anatomy** → `ANATOMY_TOKENS`
2. **injury** → `INJURY_TOKENS`
3. **diagnostic_event** → `DIAGNOSTIC_EVENT_TOKENS`

**Template Pattern**:
```
anatomy × injury × diagnostic_event
```

### injury_x_healing_x_diagnostic_event

**Slot Count**: 3

**Slot Composition**:

1. **injury** → `INJURY_TOKENS`
2. **healing** → `HEALING_TOKENS`
3. **diagnostic_event** → `DIAGNOSTIC_EVENT_TOKENS`

**Template Pattern**:
```
injury × healing × diagnostic_event
```

### diagnostic_event_x_injury

**Slot Count**: 2

**Slot Composition**:

1. **diagnostic_event** → `DIAGNOSTIC_EVENT_TOKENS`
2. **injury** → `INJURY_TOKENS`

**Template Pattern**:
```
diagnostic_event × injury
```

### qualifier_x_anatomy_x_injury_x_encounter

**Slot Count**: 4

**Slot Composition**:

1. **qualifier** → `QUALIFIER_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **injury** → `INJURY_TOKENS`
4. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
qualifier × anatomy × injury × encounter
```

### qualifier_x_injury_x_encounter

**Slot Count**: 3

**Slot Composition**:

1. **qualifier** → `QUALIFIER_TOKENS`
2. **injury** → `INJURY_TOKENS`
3. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
qualifier × injury × encounter
```

### anatomy_x_injury_x_fracture_detail_x_healing_x_encounter

**Slot Count**: 5

**Slot Composition**:

1. **anatomy** → `ANATOMY_TOKENS`
2. **injury** → `INJURY_TOKENS`
3. **fracture_detail** → `FRACTURE_DETAIL_TOKENS`
4. **healing** → `HEALING_TOKENS`
5. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
anatomy × injury × fracture_detail × healing × encounter
```

### anatomy_x_injury_x_fracture_detail_x_encounter

**Slot Count**: 4

**Slot Composition**:

1. **anatomy** → `ANATOMY_TOKENS`
2. **injury** → `INJURY_TOKENS`
3. **fracture_detail** → `FRACTURE_DETAIL_TOKENS`
4. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
anatomy × injury × fracture_detail × encounter
```

### anatomy_x_injury_x_healing_x_encounter

**Slot Count**: 4

**Slot Composition**:

1. **anatomy** → `ANATOMY_TOKENS`
2. **injury** → `INJURY_TOKENS`
3. **healing** → `HEALING_TOKENS`
4. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
anatomy × injury × healing × encounter
```

### anatomy_x_injury_x_encounter

**Slot Count**: 3

**Slot Composition**:

1. **anatomy** → `ANATOMY_TOKENS`
2. **injury** → `INJURY_TOKENS`
3. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
anatomy × injury × encounter
```

### injury_x_encounter

**Slot Count**: 2

**Slot Composition**:

1. **injury** → `INJURY_TOKENS`
2. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
injury × encounter
```

### mechanism_x_injury_x_encounter

**Slot Count**: 3

**Slot Composition**:

1. **mechanism** → `MECHANISM_TOKENS`
2. **injury** → `INJURY_TOKENS`
3. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
mechanism × injury × encounter
```

### mechanism_x_anatomy_x_injury

**Slot Count**: 3

**Slot Composition**:

1. **mechanism** → `MECHANISM_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **injury** → `INJURY_TOKENS`

**Template Pattern**:
```
mechanism × anatomy × injury
```

### diagnostic_classifier_x_anatomy_x_injury_x_encounter

**Slot Count**: 4

**Slot Composition**:

1. **diagnostic_classifier** → `DIAGNOSTIC_CLASSIFIER_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **injury** → `INJURY_TOKENS`
4. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
diagnostic_classifier × anatomy × injury × encounter
```

### mechanism_x_anatomy_x_injury_x_encounter

**Slot Count**: 4

**Slot Composition**:

1. **mechanism** → `MECHANISM_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **injury** → `INJURY_TOKENS`
4. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
mechanism × anatomy × injury × encounter
```

### mechanism_x_injury

**Slot Count**: 2

**Slot Composition**:

1. **mechanism** → `MECHANISM_TOKENS`
2. **injury** → `INJURY_TOKENS`

**Template Pattern**:
```
mechanism × injury
```

### anatomy_x_injury_x_modifier_with_x_encounter

**Slot Count**: 4

**Slot Composition**:

1. **anatomy** → `ANATOMY_TOKENS`
2. **injury** → `INJURY_TOKENS`
3. **modifier_with** → `MODIFIER_WITH_TOKENS`
4. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
anatomy × injury × modifier_with × encounter
```

### anatomy_x_injury_x_fracture_detail_x_modifier_with_x_encounter

**Slot Count**: 5

**Slot Composition**:

1. **anatomy** → `ANATOMY_TOKENS`
2. **injury** → `INJURY_TOKENS`
3. **fracture_detail** → `FRACTURE_DETAIL_TOKENS`
4. **modifier_with** → `MODIFIER_WITH_TOKENS`
5. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
anatomy × injury × fracture_detail × modifier_with × encounter
```

### injury_x_modifier_with_x_encounter

**Slot Count**: 3

**Slot Composition**:

1. **injury** → `INJURY_TOKENS`
2. **modifier_with** → `MODIFIER_WITH_TOKENS`
3. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
injury × modifier_with × encounter
```

### laterality_x_anatomy_x_injury_x_modifier_with_x_encounter

**Slot Count**: 5

**Slot Composition**:

1. **laterality** → `LATERALITY_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **injury** → `INJURY_TOKENS`
4. **modifier_with** → `MODIFIER_WITH_TOKENS`
5. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
laterality × anatomy × injury × modifier_with × encounter
```

### anatomy_x_injury_x_healing_x_modifier_with_x_encounter

**Slot Count**: 5

**Slot Composition**:

1. **anatomy** → `ANATOMY_TOKENS`
2. **injury** → `INJURY_TOKENS`
3. **healing** → `HEALING_TOKENS`
4. **modifier_with** → `MODIFIER_WITH_TOKENS`
5. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
anatomy × injury × healing × modifier_with × encounter
```

### diagnostic_classifier_x_anatomy_x_injury_x_modifier_with_x_encounter

**Slot Count**: 5

**Slot Composition**:

1. **diagnostic_classifier** → `DIAGNOSTIC_CLASSIFIER_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **injury** → `INJURY_TOKENS`
4. **modifier_with** → `MODIFIER_WITH_TOKENS`
5. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
diagnostic_classifier × anatomy × injury × modifier_with × encounter
```

### laterality_x_anatomy_x_injury_x_encounter

**Slot Count**: 4

**Slot Composition**:

1. **laterality** → `LATERALITY_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **injury** → `INJURY_TOKENS`
4. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
laterality × anatomy × injury × encounter
```

### anatomy_x_laterality_x_injury_x_encounter

**Slot Count**: 4

**Slot Composition**:

1. **anatomy** → `ANATOMY_TOKENS`
2. **laterality** → `LATERALITY_TOKENS`
3. **injury** → `INJURY_TOKENS`
4. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
anatomy × laterality × injury × encounter
```

### injury_x_laterality_x_anatomy_x_encounter

**Slot Count**: 4

**Slot Composition**:

1. **injury** → `INJURY_TOKENS`
2. **laterality** → `LATERALITY_TOKENS`
3. **anatomy** → `ANATOMY_TOKENS`
4. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
injury × laterality × anatomy × encounter
```

### laterality_x_anatomy_x_injury_x_fracture_detail_x_encounter

**Slot Count**: 5

**Slot Composition**:

1. **laterality** → `LATERALITY_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **injury** → `INJURY_TOKENS`
4. **fracture_detail** → `FRACTURE_DETAIL_TOKENS`
5. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
laterality × anatomy × injury × fracture_detail × encounter
```

### encounter_x_injury_x_anatomy

**Slot Count**: 3

**Slot Composition**:

1. **encounter** → `ENCOUNTER_TOKENS`
2. **injury** → `INJURY_TOKENS`
3. **anatomy** → `ANATOMY_TOKENS`

**Template Pattern**:
```
encounter × injury × anatomy
```

### encounter_x_injury_x_fracture_detail

**Slot Count**: 3

**Slot Composition**:

1. **encounter** → `ENCOUNTER_TOKENS`
2. **injury** → `INJURY_TOKENS`
3. **fracture_detail** → `FRACTURE_DETAIL_TOKENS`

**Template Pattern**:
```
encounter × injury × fracture_detail
```

### encounter_x_anatomy_x_injury_x_healing

**Slot Count**: 4

**Slot Composition**:

1. **encounter** → `ENCOUNTER_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **injury** → `INJURY_TOKENS`
4. **healing** → `HEALING_TOKENS`

**Template Pattern**:
```
encounter × anatomy × injury × healing
```

### encounter_x_qualifier_x_injury

**Slot Count**: 3

**Slot Composition**:

1. **encounter** → `ENCOUNTER_TOKENS`
2. **qualifier** → `QUALIFIER_TOKENS`
3. **injury** → `INJURY_TOKENS`

**Template Pattern**:
```
encounter × qualifier × injury
```

### qualifier_x_laterality_x_anatomy_x_location_x_injury_x_modifier_with_x_duration_x_outcome_x_encounter

**Slot Count**: 9

**Slot Composition**:

1. **qualifier** → `QUALIFIER_TOKENS`
2. **laterality** → `LATERALITY_TOKENS`
3. **anatomy** → `ANATOMY_TOKENS`
4. **location** → `LOCATION_TOKENS`
5. **injury** → `INJURY_TOKENS`
6. **modifier_with** → `MODIFIER_WITH_TOKENS`
7. **duration** → `DURATION_TOKENS`
8. **outcome** → `OUTCOME_TOKENS`
9. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
qualifier × laterality × anatomy × location × injury × modifier_with × duration × outcome × encounter
```

### qualifier_x_laterality_x_anatomy_x_injury_x_modifier_with_x_outcome_x_encounter

**Slot Count**: 7

**Slot Composition**:

1. **qualifier** → `QUALIFIER_TOKENS`
2. **laterality** → `LATERALITY_TOKENS`
3. **anatomy** → `ANATOMY_TOKENS`
4. **injury** → `INJURY_TOKENS`
5. **modifier_with** → `MODIFIER_WITH_TOKENS`
6. **outcome** → `OUTCOME_TOKENS`
7. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
qualifier × laterality × anatomy × injury × modifier_with × outcome × encounter
```

### qualifier_x_laterality_x_anatomy_x_location_x_injury_x_modifier_with_x_duration_x_encounter

**Slot Count**: 8

**Slot Composition**:

1. **qualifier** → `QUALIFIER_TOKENS`
2. **laterality** → `LATERALITY_TOKENS`
3. **anatomy** → `ANATOMY_TOKENS`
4. **location** → `LOCATION_TOKENS`
5. **injury** → `INJURY_TOKENS`
6. **modifier_with** → `MODIFIER_WITH_TOKENS`
7. **duration** → `DURATION_TOKENS`
8. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
qualifier × laterality × anatomy × location × injury × modifier_with × duration × encounter
```

### qualifier_x_laterality_x_anatomy_x_injury_x_modifier_with_x_duration_x_encounter

**Slot Count**: 7

**Slot Composition**:

1. **qualifier** → `QUALIFIER_TOKENS`
2. **laterality** → `LATERALITY_TOKENS`
3. **anatomy** → `ANATOMY_TOKENS`
4. **injury** → `INJURY_TOKENS`
5. **modifier_with** → `MODIFIER_WITH_TOKENS`
6. **duration** → `DURATION_TOKENS`
7. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
qualifier × laterality × anatomy × injury × modifier_with × duration × encounter
```

### laterality_x_anatomy_x_injury_x_modifier_with_x_duration_x_outcome_x_encounter

**Slot Count**: 7

**Slot Composition**:

1. **laterality** → `LATERALITY_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **injury** → `INJURY_TOKENS`
4. **modifier_with** → `MODIFIER_WITH_TOKENS`
5. **duration** → `DURATION_TOKENS`
6. **outcome** → `OUTCOME_TOKENS`
7. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
laterality × anatomy × injury × modifier_with × duration × outcome × encounter
```

### laterality_x_anatomy_x_injury_x_modifier_with_x_outcome_x_encounter

**Slot Count**: 6

**Slot Composition**:

1. **laterality** → `LATERALITY_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **injury** → `INJURY_TOKENS`
4. **modifier_with** → `MODIFIER_WITH_TOKENS`
5. **outcome** → `OUTCOME_TOKENS`
6. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
laterality × anatomy × injury × modifier_with × outcome × encounter
```

---

## Toxic & Poisoning Families

*Total families in category: 5*

### toxic_event_x_agent_x_intent_x_encounter

**Slot Count**: 4

**Slot Composition**:

1. **toxic_event** → `TOXIC_EVENT_TOKENS`
2. **toxic_agent** → `TOXIC_AGENT_TOKENS`
3. **toxic_intent** → `TOXIC_INTENT_TOKENS`
4. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
toxic_event × toxic_agent × toxic_intent × encounter
```

### toxic_event_x_intent_x_encounter

**Slot Count**: 3

**Slot Composition**:

1. **toxic_event** → `TOXIC_EVENT_TOKENS`
2. **toxic_intent** → `TOXIC_INTENT_TOKENS`
3. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
toxic_event × toxic_intent × encounter
```

### toxic_event_x_agent_x_encounter

**Slot Count**: 3

**Slot Composition**:

1. **toxic_event** → `TOXIC_EVENT_TOKENS`
2. **toxic_agent** → `TOXIC_AGENT_TOKENS`
3. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
toxic_event × toxic_agent × encounter
```

### qualifier_x_toxic_event_x_intent_x_encounter

**Slot Count**: 4

**Slot Composition**:

1. **qualifier** → `QUALIFIER_TOKENS`
2. **toxic_event** → `TOXIC_EVENT_TOKENS`
3. **toxic_intent** → `TOXIC_INTENT_TOKENS`
4. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
qualifier × toxic_event × toxic_intent × encounter
```

### toxic_event_x_encounter

**Slot Count**: 2

**Slot Composition**:

1. **toxic_event** → `TOXIC_EVENT_TOKENS`
2. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
toxic_event × encounter
```

---

## Condition Families

*Total families in category: 27*

### diagnostic_event_x_condition_x_diagnostic_context

**Slot Count**: 3

**Slot Composition**:

1. **diagnostic_event** → `DIAGNOSTIC_EVENT_TOKENS`
2. **condition** → `CONDITION_TOKENS`
3. **diagnostic_context** → `DIAGNOSTIC_CONTEXT_TOKENS`

**Template Pattern**:
```
diagnostic_event × condition × diagnostic_context
```

### qualifier_x_diagnostic_event_x_condition_x_diagnostic_context

**Slot Count**: 4

**Slot Composition**:

1. **qualifier** → `QUALIFIER_TOKENS`
2. **diagnostic_event** → `DIAGNOSTIC_EVENT_TOKENS`
3. **condition** → `CONDITION_TOKENS`
4. **diagnostic_context** → `DIAGNOSTIC_CONTEXT_TOKENS`

**Template Pattern**:
```
qualifier × diagnostic_event × condition × diagnostic_context
```

### anatomy_x_condition_x_diagnostic_event

**Slot Count**: 3

**Slot Composition**:

1. **anatomy** → `ANATOMY_TOKENS`
2. **condition** → `CONDITION_TOKENS`
3. **diagnostic_event** → `DIAGNOSTIC_EVENT_TOKENS`

**Template Pattern**:
```
anatomy × condition × diagnostic_event
```

### diagnostic_event_x_condition

**Slot Count**: 2

**Slot Composition**:

1. **diagnostic_event** → `DIAGNOSTIC_EVENT_TOKENS`
2. **condition** → `CONDITION_TOKENS`

**Template Pattern**:
```
diagnostic_event × condition
```

### qualifier_x_anatomy_x_condition

**Slot Count**: 3

**Slot Composition**:

1. **qualifier** → `QUALIFIER_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **condition** → `CONDITION_TOKENS`

**Template Pattern**:
```
qualifier × anatomy × condition
```

### qualifier_x_condition

**Slot Count**: 2

**Slot Composition**:

1. **qualifier** → `QUALIFIER_TOKENS`
2. **condition** → `CONDITION_TOKENS`

**Template Pattern**:
```
qualifier × condition
```

### etiology_x_condition

**Slot Count**: 2

**Slot Composition**:

1. **etiology** → `ETIOLOGY_TOKENS`
2. **condition** → `CONDITION_TOKENS`

**Template Pattern**:
```
etiology × condition
```

### anatomy_x_condition

**Slot Count**: 2

**Slot Composition**:

1. **anatomy** → `ANATOMY_TOKENS`
2. **condition** → `CONDITION_TOKENS`

**Template Pattern**:
```
anatomy × condition
```

### anatomy_x_condition_low

**Slot Count**: 2

**Slot Composition**:

1. **anatomy** → `ANATOMY_TOKENS`
2. **condition_low** → `CONDITION_LOW_TOKENS`

**Template Pattern**:
```
anatomy × condition_low
```

### condition_adjective_x_condition_high

**Slot Count**: 2

**Slot Composition**:

1. **condition_adjective** → `CONDITION_ADJECTIVE_TOKENS`
2. **condition_high** → `CONDITION_HIGH_TOKENS`

**Template Pattern**:
```
condition_adjective × condition_high
```

### anatomy_x_adjectival_condition

**Slot Count**: 2

**Slot Composition**:

1. **anatomy** → `ANATOMY_TOKENS`
2. **adjectival_condition** → `ADJECTIVAL_CONDITION_TOKENS`

**Template Pattern**:
```
anatomy × adjectival_condition
```

### location_x_anatomy_x_condition

**Slot Count**: 3

**Slot Composition**:

1. **location** → `LOCATION_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **condition** → `CONDITION_TOKENS`

**Template Pattern**:
```
location × anatomy × condition
```

### anatomy_prefix_x_condition

**Slot Count**: 2

**Slot Composition**:

1. **anatomy_prefix** → `ANATOMY_PREFIX_TOKENS`
2. **condition** → `CONDITION_TOKENS`

**Template Pattern**:
```
anatomy_prefix × condition
```

### condition_x_modifier_with

**Slot Count**: 2

**Slot Composition**:

1. **condition** → `CONDITION_TOKENS`
2. **modifier_with** → `MODIFIER_WITH_TOKENS`

**Template Pattern**:
```
condition × modifier_with
```

### anatomy_x_condition_x_modifier_with

**Slot Count**: 3

**Slot Composition**:

1. **anatomy** → `ANATOMY_TOKENS`
2. **condition** → `CONDITION_TOKENS`
3. **modifier_with** → `MODIFIER_WITH_TOKENS`

**Template Pattern**:
```
anatomy × condition × modifier_with
```

### qualifier_x_condition_x_modifier_with

**Slot Count**: 3

**Slot Composition**:

1. **qualifier** → `QUALIFIER_TOKENS`
2. **condition** → `CONDITION_TOKENS`
3. **modifier_with** → `MODIFIER_WITH_TOKENS`

**Template Pattern**:
```
qualifier × condition × modifier_with
```

### laterality_x_anatomy_x_condition_x_modifier_with

**Slot Count**: 4

**Slot Composition**:

1. **laterality** → `LATERALITY_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **condition** → `CONDITION_TOKENS`
4. **modifier_with** → `MODIFIER_WITH_TOKENS`

**Template Pattern**:
```
laterality × anatomy × condition × modifier_with
```

### qualifier_x_anatomy_x_condition_x_modifier_with

**Slot Count**: 4

**Slot Composition**:

1. **qualifier** → `QUALIFIER_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **condition** → `CONDITION_TOKENS`
4. **modifier_with** → `MODIFIER_WITH_TOKENS`

**Template Pattern**:
```
qualifier × anatomy × condition × modifier_with
```

### laterality_x_anatomy_x_condition

**Slot Count**: 3

**Slot Composition**:

1. **laterality** → `LATERALITY_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **condition** → `CONDITION_TOKENS`

**Template Pattern**:
```
laterality × anatomy × condition
```

### anatomy_x_laterality_x_condition

**Slot Count**: 3

**Slot Composition**:

1. **anatomy** → `ANATOMY_TOKENS`
2. **laterality** → `LATERALITY_TOKENS`
3. **condition** → `CONDITION_TOKENS`

**Template Pattern**:
```
anatomy × laterality × condition
```

### condition_x_laterality_x_anatomy

**Slot Count**: 3

**Slot Composition**:

1. **condition** → `CONDITION_TOKENS`
2. **laterality** → `LATERALITY_TOKENS`
3. **anatomy** → `ANATOMY_TOKENS`

**Template Pattern**:
```
condition × laterality × anatomy
```

### encounter_x_condition

**Slot Count**: 2

**Slot Composition**:

1. **encounter** → `ENCOUNTER_TOKENS`
2. **condition** → `CONDITION_TOKENS`

**Template Pattern**:
```
encounter × condition
```

### disease_state_x_condition

**Slot Count**: 2

**Slot Composition**:

1. **disease_state** → `DISEASE_STATE_TOKENS`
2. **condition** → `CONDITION_TOKENS`

**Template Pattern**:
```
disease_state × condition
```

### disease_state_x_anatomy_x_condition

**Slot Count**: 3

**Slot Composition**:

1. **disease_state** → `DISEASE_STATE_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **condition** → `CONDITION_TOKENS`

**Template Pattern**:
```
disease_state × anatomy × condition
```

### condition_x_disease_state

**Slot Count**: 2

**Slot Composition**:

1. **condition** → `CONDITION_TOKENS`
2. **disease_state** → `DISEASE_STATE_TOKENS`

**Template Pattern**:
```
condition × disease_state
```

### maternal_context_x_condition

**Slot Count**: 2

**Slot Composition**:

1. **maternal_context** → `MATERNAL_CONTEXT_TOKENS`
2. **condition** → `CONDITION_TOKENS`

**Template Pattern**:
```
maternal_context × condition
```

### condition_x_maternal_context

**Slot Count**: 2

**Slot Composition**:

1. **condition** → `CONDITION_TOKENS`
2. **maternal_context** → `MATERNAL_CONTEXT_TOKENS`

**Template Pattern**:
```
condition × maternal_context
```

---

## Mechanism & External Cause Families

*Total families in category: 4*

### mechanism_x_injury_x_encounter

**Slot Count**: 3

**Slot Composition**:

1. **mechanism** → `MECHANISM_TOKENS`
2. **injury** → `INJURY_TOKENS`
3. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
mechanism × injury × encounter
```

### mechanism_x_anatomy_x_injury

**Slot Count**: 3

**Slot Composition**:

1. **mechanism** → `MECHANISM_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **injury** → `INJURY_TOKENS`

**Template Pattern**:
```
mechanism × anatomy × injury
```

### mechanism_x_anatomy_x_injury_x_encounter

**Slot Count**: 4

**Slot Composition**:

1. **mechanism** → `MECHANISM_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`
3. **injury** → `INJURY_TOKENS`
4. **encounter** → `ENCOUNTER_TOKENS`

**Template Pattern**:
```
mechanism × anatomy × injury × encounter
```

### mechanism_x_injury

**Slot Count**: 2

**Slot Composition**:

1. **mechanism** → `MECHANISM_TOKENS`
2. **injury** → `INJURY_TOKENS`

**Template Pattern**:
```
mechanism × injury
```

---

## Encounter-Based Families

*Total families in category: 1*

### encounter_x_condition

**Slot Count**: 2

**Slot Composition**:

1. **encounter** → `ENCOUNTER_TOKENS`
2. **condition** → `CONDITION_TOKENS`

**Template Pattern**:
```
encounter × condition
```

---

## Other Families

*Total families in category: 3*

### procedure_x_complication

**Slot Count**: 2

**Slot Composition**:

1. **procedure** → `PROCEDURE_TOKENS`
2. **complication** → `COMPLICATION_TOKENS`

**Template Pattern**:
```
procedure × complication
```

### maternal_context_x_complication

**Slot Count**: 2

**Slot Composition**:

1. **maternal_context** → `MATERNAL_CONTEXT_TOKENS`
2. **complication** → `COMPLICATION_TOKENS`

**Template Pattern**:
```
maternal_context × complication
```

### maternal_context_x_anatomy

**Slot Count**: 2

**Slot Composition**:

1. **maternal_context** → `MATERNAL_CONTEXT_TOKENS`
2. **anatomy** → `ANATOMY_TOKENS`

**Template Pattern**:
```
maternal_context × anatomy
```

---

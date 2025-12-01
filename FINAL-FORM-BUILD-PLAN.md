# FINAL-FORM Build Plan

**Version:** 0.2.0
**Status:** Ready for Implementation

---

## 1. Objective

Build the **final-form** semantic processing engine that transforms canonical JSON input into **immutable MeasurementEvent objects** with full provenance, scoring, and interpretation.

This build plan follows a **registry-first** approach: define specs before writing code.

---

## 2. Scope (v0.1)

### Included

- **Registry Setup:** Instrument registry + Form registry + Finalization registry
- **Instruments:** PHQ-9, GAD-7 (with architecture supporting ~13)
- **Full Pipeline:** Binding → Mapping → Recoding → Scoring → Interpretation → Emission
- **Output Model:** MeasurementEvent + Observations (FHIR-aligned)
- **CLI:** Batch processing with explicit binding spec
- **Diagnostics:** Errors, warnings, quality metrics
- **JSON-only:** All specs in JSON, SemVer'd

### Excluded

- Dataset adapters (pandas/arrow) — downstream concern
- SDK layering
- Vectorization
- Arch-gov integration
- Authoring tools (fuzzy matching for binding generation)

These come later.

---

## 3. Deliverables

### 3.1 Registries

| Registry | Contents | Location |
|----------|----------|----------|
| **instrument-registry** | PHQ-9, GAD-7 definitions | `instrument-registry/instruments/` |
| **form-binding-registry** | Example binding specs | `form-binding-registry/bindings/` |
| **schemas** | JSON Schemas for all spec types | `schemas/` |

### 3.2 Python Package

```
final_form/
├── __init__.py
├── registry/
│   ├── __init__.py
│   ├── instruments.py      # Load instrument specs
│   ├── bindings.py         # Load form binding specs
│   └── models.py           # Pydantic models for specs
├── mapping/
│   └── mapper.py           # Form item → instrument item
├── recoding/
│   └── recoder.py          # Text → numeric conversion
├── validation/
│   └── checks.py           # Range checks, completeness
├── scoring/
│   └── engine.py           # Generic scoring engine
├── interpretation/
│   └── interpreter.py      # Severity bands, labels
├── emitters/
│   └── measurement.py      # MeasurementEvent builder
├── diagnostics/
│   └── collector.py        # Error/warning collection
├── cli/
│   └── run.py              # Typer CLI
└── schemas/
    └── *.json              # JSON Schema files
```

### 3.3 CLI

```bash
final-form run \
  --in forms.jsonl \
  --out measurements.jsonl \
  --binding intake_v1 \
  --instrument-registry ./instrument-registry \
  --form-binding-registry ./form-binding-registry
```

### 3.4 Test Suite

- Golden tests for PHQ-9, GAD-7
- Edge cases (missing items, out-of-range, text anchors)
- Determinism verification
- Integration with canonical form responses

---

## 4. Work Breakdown Structure

### Phase 1: Registry & Schema Foundation

**Objective:** Define all JSON schemas and create initial registry structure.

**Artifacts:**

```
schemas/
├── instrument_spec.schema.json
├── form_binding_spec.schema.json
├── finalform_spec.schema.json
├── measurement_event.schema.json
└── observation.schema.json

instrument-registry/
├── instruments/
│   ├── phq9/1-0-0.json
│   └── gad7/1-0-0.json
└── README.md

form-binding-registry/
├── bindings/
│   └── example_intake_v1/1-0-0.json
└── README.md
```

**Key Points:**
- JSON only (no YAML)
- All specs SemVer'd
- Schemas validate specs

---

### Phase 2: Package Foundation

**Objective:** Create package scaffold with registry loaders.

**Artifacts:**

```
final_form/
├── __init__.py
├── registry/
│   ├── __init__.py
│   ├── instruments.py
│   ├── bindings.py
│   └── models.py
├── io.py
└── cli.py

pyproject.toml
tests/
├── test_registry.py
└── conftest.py
```

**Registry loader behavior:**
- Load instrument specs from `instrument-registry/instruments/<id>/<version>.json`
- Load binding specs from `form-binding-registry/bindings/<id>/<version>.json`
- Validate against JSON schemas
- Provide lookup by ID and version

---

### Phase 3: Mapping & Recoding

**Objective:** Implement form item → instrument item mapping with value recoding.

**Artifacts:**

```
final_form/
├── mapping/
│   └── mapper.py
└── recoding/
    └── recoder.py

tests/
├── test_mapper.py
└── test_recoder.py
```

**Mapping logic:**
1. Load binding spec
2. For each form item, lookup by `field_key` or `position`
3. Map to `instrument_item_id`
4. **Error if not found** (no fallbacks)

**Recoding logic:**
1. If value is numeric: validate range, pass through
2. If value is text: lookup in instrument's `response_map`
3. If text has alias: resolve alias first
4. **Error if not mappable** (no fuzzy matching)

---

### Phase 4: Validation & Quality Checks

**Objective:** Light validation layer after mapping.

**Artifacts:**

```
final_form/
└── validation/
    └── checks.py

tests/
└── test_validation.py
```

**Validation checks:**
- All required items present (per binding spec)
- All values in valid range (per instrument spec)
- Flag missing items with count
- Flag out-of-range values

**Output:** Validation result with issues list.

---

### Phase 5: Generic Scoring Engine

**Objective:** Single scoring engine that interprets instrument specs.

**Artifacts:**

```
final_form/
└── scoring/
    ├── __init__.py
    ├── engine.py
    ├── methods.py
    └── reverse.py

tests/
├── test_scoring_engine.py
├── test_phq9_scoring.py
└── test_gad7_scoring.py
```

**Scoring engine behavior:**
1. Load instrument spec
2. For each scale in instrument:
   - Get item values
   - Apply reverse scoring for `reversed_items`
   - Compute score using `method` (sum, average, sum_then_double)
   - Handle missing items per `missing_allowed` threshold
3. Return scale scores

**No per-questionnaire code.** The engine reads scoring rules from the spec.

---

### Phase 6: Interpretation Layer

**Objective:** Apply severity bands and add interpretation labels.

**Artifacts:**

```
final_form/
└── interpretation/
    └── interpreter.py

tests/
└── test_interpretation.py
```

**Interpretation logic:**
1. For each scale score:
   - Find matching range in `interpretations` (min <= score <= max)
   - Add `label` (e.g., "Moderate")
   - Add any additional metadata (severity level, description)
2. Handle edge cases (score exactly at boundary)

---

### Phase 7: MeasurementEvent Emitter

**Objective:** Build final output objects.

**Artifacts:**

```
final_form/
└── emitters/
    └── measurement.py

tests/
└── test_emitters.py
```

**MeasurementEvent structure:**
```json
{
  "schema": "com.lifeos.measurement_event.v1",
  "measurement_event_id": "uuid",
  "instrument_id": "phq9",
  "instrument_version": "1.0.0",
  "subject_id": "contact::<uuid>",
  "timestamp": "ISO8601",
  "source": {
    "form_id": "googleforms::<id>",
    "form_submission_id": "subm::<id>",
    "form_correlation_id": "...",
    "binding_id": "intake_v1",
    "binding_version": "1.0.0"
  },
  "observations": [...],
  "telemetry": {
    "processed_at": "ISO8601",
    "final_form_version": "0.1.0",
    "instrument_spec": "phq9@1.0.0",
    "form_binding_spec": "intake_v1@1.0.0"
  }
}
```

**Observation structure:**
```json
{
  "schema": "com.lifeos.observation.v1",
  "observation_id": "uuid",
  "instrument_id": "phq9",
  "code": "phq9_item1",
  "kind": "item",
  "value": 2,
  "value_type": "integer"
}
```

---

### Phase 8: Diagnostics

**Objective:** Collect and emit processing diagnostics.

**Artifacts:**

```
final_form/
└── diagnostics/
    ├── __init__.py
    ├── collector.py
    └── models.py

tests/
└── test_diagnostics.py
```

**Diagnostic object:**
```json
{
  "form_submission_id": "...",
  "status": "success|partial|failed",
  "errors": [...],
  "warnings": [...],
  "quality": {
    "completeness": 0.89,
    "missing_items": ["phq9_item3"],
    "out_of_range_items": []
  }
}
```

---

### Phase 9: CLI Integration

**Objective:** Wire everything into the CLI pipeline.

**Artifacts:**

```
final_form/
├── cli/
│   └── run.py
└── pipeline/
    └── orchestrator.py

tests/
├── test_cli.py
└── integration/
    └── test_pipeline.py
```

**Pipeline flow:**
1. Load binding spec (from `--binding`)
2. Load instrument specs (for instruments in binding)
3. Read input JSONL
4. For each record:
   - Map items using binding
   - Recode values using instrument response_map
   - Validate completeness and ranges
   - Score using generic engine
   - Interpret using severity bands
   - Emit MeasurementEvent(s)
   - Collect diagnostics
5. Write output JSONL
6. Write diagnostics (if `--diagnostics` specified)

---

### Phase 10: Golden Tests & CI

**Objective:** Comprehensive test coverage with determinism verification.

**Artifacts:**

```
tests/
├── fixtures/
│   ├── canonical/
│   │   ├── phq9_complete.json
│   │   ├── phq9_partial.json
│   │   ├── gad7_complete.json
│   │   └── multi_instrument.json
│   └── bindings/
│       └── test_binding.json
├── golden/
│   ├── phq9_complete_expected.json
│   ├── phq9_partial_expected.json
│   └── gad7_complete_expected.json
├── test_determinism.py
└── integration/
    └── test_end_to_end.py

.github/workflows/ci.yml
```

**Golden test approach:**
1. Input: canonical form response + binding spec
2. Expected: exact MeasurementEvent output
3. Assert byte-for-byte equality (determinism)

**Determinism test:**
```python
for _ in range(5):
    result = process(input)
    assert result == expected  # Same every time
```

---

## 5. Processing Flow Diagram

```
canonical form_response (JSONL)
         │
         ▼
┌─────────────────────┐
│  Load Binding Spec  │ ← form-registry
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ For each section:   │
│   Load Instrument   │ ← instrument-registry
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   Map Form Items    │  field_key/position → instrument_item_id
│   to Instrument     │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   Recode Values     │  text → numeric using response_map
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   Validate          │  completeness, ranges
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   Score             │  generic engine, reads from spec
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   Interpret         │  severity bands, labels
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   Emit              │  MeasurementEvent + Observations
└─────────────────────┘
         │
         ▼
MeasurementEvents (JSONL) + Diagnostics
```

---

## 6. Success Criteria

| Criterion | Measure |
|-----------|---------|
| **Determinism** | Same input → same output, verified by repeated runs |
| **Scoring accuracy** | Golden tests pass for PHQ-9, GAD-7 |
| **No inference** | All mappings explicit, errors on missing bindings |
| **Full provenance** | Every output includes telemetry with all spec versions |
| **Test coverage** | 80% overall, 95% for scoring engine |
| **CI green** | Lint + unit tests + integration tests pass |

---

## 7. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Registry not set up before code | Phase 1 is registry-only, blocks Phase 2 |
| Scoring drift | Registry is source of truth, no hardcoded rules |
| Missing bindings at runtime | Fail loudly with clear error messages |
| Schema evolution | SemVer all specs, telemetry tracks versions |

---

## 8. Dependencies

**External:**
- Canonical form responses from canonizer
- JSON Schemas for validation

**Internal:**
- instrument-registry must exist before scoring
- form-binding-registry must have binding for each form processed

---

## 9. Future Versions

| Version | Scope |
|---------|-------|
| **v0.2** | ~13 instruments, enhanced diagnostics |
| **v0.3** | correlation_id support, batch correlation |
| **v1.0** | Stable API, plugin architecture |
| **v2.0** | Authoring tools (fuzzy matching for binding generation) |
| **v3.0** | Cross-domain expansion (labs, vitals, wearables) |

---

## 10. Summary

This build plan follows three principles:

1. **Registry-first:** Define specs in JSON before writing code
2. **No inference:** All mappings explicit, errors on ambiguity
3. **FHIR-aligned output:** MeasurementEvents + Observations, ready for healthcare interop

The result is a deterministic, reproducible semantic processing engine that transforms canonical form responses into research-ready measure instances.

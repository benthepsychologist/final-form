---
version: "0.1"
tier: B
title: Final Form v0.1.0 - Semantic Processing Engine with FHIR-Aligned Output
owner: benthepsychologist
goal: Build the final-form semantic processing engine that transforms canonical JSON input into immutable MeasurementEvent objects with full provenance, scoring, and interpretation
labels: [questionnaires, scoring, semantic-processing, fhir, measurement-events, v0]
project_slug: final-form
spec_version: 2.0.0
created: 2025-11-17T14:53:29.020741+00:00
updated: 2025-12-01T00:00:00.000000+00:00
orchestrator_contract: "standard"
repo:
  working_branch: "feat/final-form-v0"
---

# Final Form v0.1.0 - Semantic Processing Engine

## Objective

Build the **final-form** semantic processing engine that transforms canonical JSON input into **immutable MeasurementEvent objects** with full provenance, scoring, and interpretation.

final-form is the authoritative semantic data engine sitting between canonizer and downstream consumers. It performs deterministic, domain-aware processing including mapping, recoding, scoring, interpretation, and validation. Once data passes through final-form, no further cleaning or scoring occurs downstream.

**Key Principles:**
- **No runtime inference** — final-form never guesses which questionnaire is present
- **Explicit bindings** — all mappings are authored upfront, not detected at runtime
- **FHIR-aligned output** — MeasurementEvents + Observations for healthcare interop
- **Registry-driven** — all semantic knowledge lives in JSON specs, not code

**v0.1.0 Scope:**
- **Registry Setup:** instrument-registry, form-binding-registry, JSON schemas
- **Instruments:** PHQ-9, GAD-7 (architecture supports ~13)
- **Full Pipeline:** Binding → Mapping → Recoding → Scoring → Interpretation → Emission
- **Output Model:** MeasurementEvent + Observations (FHIR-aligned)
- **CLI:** Batch processing with explicit binding spec
- **Diagnostics:** Errors, warnings, quality metrics

## Acceptance Criteria

### Registry & Schema
- [ ] JSON Schema created for `instrument_spec`
- [ ] JSON Schema created for `form_binding_spec`
- [ ] JSON Schema created for `measurement_event`
- [ ] JSON Schema created for `observation`
- [ ] PHQ-9 instrument spec created and validates against schema
- [ ] GAD-7 instrument spec created and validates against schema
- [ ] Example form binding spec created

### No Inference Policy
- [ ] Mapper requires explicit binding spec (no auto-detection)
- [ ] Mapper errors on missing field_key/position (no fallbacks)
- [ ] Recoder errors on unmapped text values (no fuzzy matching)
- [ ] CLI requires `--binding` flag (not optional)

### Output Model (FHIR-Aligned)
- [ ] Output is MeasurementEvent with embedded Observations
- [ ] Each instrument in a form produces one MeasurementEvent
- [ ] Observations include both item values and scale scores
- [ ] Full telemetry with all spec versions used

### Scoring Engine
- [ ] Generic scoring engine interprets instrument specs
- [ ] Supports scoring methods: sum, average, sum_then_double
- [ ] Reverse scoring handled via `reversed_items` array
- [ ] Interpretation bands applied from spec
- [ ] No per-questionnaire code

### Pipeline & CLI
- [ ] CLI command: `final-form run --in forms.jsonl --out measurements.jsonl --binding <id>`
- [ ] Processes JSONL batch inputs
- [ ] Outputs JSONL MeasurementEvents
- [ ] Optional `--diagnostics` for error/warning output

### Quality & Testing
- [ ] Golden tests pass for PHQ-9, GAD-7
- [ ] Determinism verified (same input → same output, every time)
- [ ] 80% test coverage overall, 95% for scoring engine
- [ ] CI green (lint + unit tests + integration tests)

## Context

### Background

The research pipeline currently lacks a deterministic, version-controlled semantic processing layer. Data flows from canonizer (structural normalization) with no consistent way to:
- Map platform-specific form fields to canonical instrument items
- Recode text responses to numeric values
- Score instruments according to validated rules
- Produce immutable, provenance-tracked measurement records

final-form fills this gap by providing:
- **Deterministic processing:** Replayable, diffable transformations across versions
- **Semantic authority:** Single source of truth for scoring and interpretation
- **FHIR-aligned outputs:** MeasurementEvents + Observations ready for healthcare interop
- **No inference:** All mappings explicit, authored at design-time

### Architecture: Three-Layer Separation

| Layer | Content | Owner |
|-------|---------|-------|
| **Canonical Form Response** | Shape only: `field_key`, `position`, `raw_answer`. No semantics. | canonizer |
| **Form Binding Spec** | "For form X version Y, field Z maps to instrument W item N" | form-binding-registry |
| **Instrument Spec** | What is PHQ-9? Items, anchors, scoring rules, interpretation bands | instrument-registry |

**Canonizer does NOT know about PHQ-9, GAD-7, etc.** It just produces reliable, versioned shapes with stable `field_key` and `position` values.

**Final-form does NOT infer questionnaires.** It is handed explicit binding specs that map form fields to instrument items.

### Why No Inference?

In the real world, a "form" is a big messy Google Form with multiple instruments woven together at various positions with platform-specific IDs like `entry.123456`. Runtime guessing loses rigor.

**Fuzzy matching / wording banks belong in authoring tools**, not runtime:
- **Runtime (final-form):** Uses explicit bindings only. Fails if missing. Deterministic.
- **Authoring (separate tool):** Proposes mappings based on text similarity. Human approves. Writes binding spec.

### Output Model: FHIR-Aligned

| Our Term | FHIR Equivalent | Meaning |
|----------|-----------------|---------|
| **Measure** (Instrument) | `Questionnaire` | Definition of PHQ-9, GAD-7, etc. |
| **MeasurementEvent** | `QuestionnaireResponse` | One administration instance |
| **Observation** | `Observation` | Item value, scale score, interpretation |

Final-form outputs **MeasurementEvents**, not datasets. Datasets are downstream projections.

### Constraints

- Must use explicit binding specs (no auto-detection)
- Must error on missing/unmapped items (no silent fallbacks)
- Must produce deterministic output (same input → same output)
- Must include full telemetry (all spec versions used)
- All specs in JSON only (no YAML for machine-consumed files)
- All specs SemVer'd independently

## Plan

### Step 1: Create JSON Schemas [G0: Plan Approval]

**Objective:** Define all JSON schemas for specs and outputs.

**Prompt:**

Create the following JSON Schema files in `schemas/`:

1. **`instrument_spec.schema.json`** — validates instrument definitions
   - Required: `type`, `instrument_id`, `version`, `name`, `kind`, `items`, `scales`
   - Items: array with `item_id`, `position`, `text`, `response_map`
   - Scales: array with `scale_id`, `name`, `items`, `method`, `interpretations`

2. **`form_binding_spec.schema.json`** — validates form bindings
   - Required: `type`, `form_id`, `binding_id`, `version`, `sections`
   - Sections: array with `instrument_id`, `instrument_version`, `bindings`
   - Bindings: array with `item_id`, `by` (field_key|position), `value`

3. **`measurement_event.schema.json`** — validates output events
   - Required: `schema`, `measurement_event_id`, `instrument_id`, `subject_id`, `timestamp`, `source`, `observations`, `telemetry`

4. **`observation.schema.json`** — validates individual observations
   - Required: `schema`, `observation_id`, `instrument_id`, `code`, `kind`, `value`, `value_type`

Use JSON Schema draft-07. Include `$id` and `$schema` fields.

**Outputs:**

- `schemas/instrument_spec.schema.json`
- `schemas/form_binding_spec.schema.json`
- `schemas/measurement_event.schema.json`
- `schemas/observation.schema.json`

---

### Step 2: Create Instrument Registry with PHQ-9 and GAD-7 [G0: Plan Approval]

**Objective:** Create instrument-registry with PHQ-9 and GAD-7 definitions.

**Prompt:**

Create the instrument registry structure:

```
instrument-registry/
├── README.md
└── instruments/
    ├── phq9/
    │   └── 1-0-0.json
    └── gad7/
        └── 1-0-0.json
```

**PHQ-9 spec (`instruments/phq9/1-0-0.json`):**

```json
{
  "type": "instrument_spec",
  "instrument_id": "phq9",
  "version": "1.0.0",
  "name": "Patient Health Questionnaire-9",
  "kind": "questionnaire",
  "locale": "en-US",
  "aliases": ["PHQ-9", "PHQ9", "PHQ 9"],
  "items": [
    {
      "item_id": "phq9_item1",
      "position": 1,
      "text": "Little interest or pleasure in doing things",
      "response_map": {
        "not at all": 0,
        "several days": 1,
        "more than half the days": 2,
        "nearly every day": 3
      },
      "aliases": {
        "more than half of the days": "more than half the days"
      }
    }
    // ... items 2-9
  ],
  "scales": [
    {
      "scale_id": "phq9_total",
      "name": "PHQ-9 Total Score",
      "items": ["phq9_item1", "phq9_item2", "phq9_item3", "phq9_item4", "phq9_item5", "phq9_item6", "phq9_item7", "phq9_item8", "phq9_item9"],
      "method": "sum",
      "reversed_items": [],
      "min": 0,
      "max": 27,
      "missing_allowed": 1,
      "interpretations": [
        { "min": 0, "max": 4, "label": "Minimal" },
        { "min": 5, "max": 9, "label": "Mild" },
        { "min": 10, "max": 14, "label": "Moderate" },
        { "min": 15, "max": 19, "label": "Moderately severe" },
        { "min": 20, "max": 27, "label": "Severe" }
      ]
    }
  ]
}
```

Similarly create GAD-7 spec with 7 items and appropriate interpretations.

Validate both specs against `instrument_spec.schema.json`.

**Outputs:**

- `instrument-registry/README.md`
- `instrument-registry/instruments/phq9/1-0-0.json`
- `instrument-registry/instruments/gad7/1-0-0.json`

---

### Step 3: Create Form Binding Registry with Example Binding [G0: Plan Approval]

**Objective:** Create form-binding-registry with an example binding spec.

**Prompt:**

Create the form binding registry structure:

```
form-binding-registry/
├── README.md
└── bindings/
    └── example_intake/
        └── 1-0-0.json
```

**Example binding spec (`bindings/example_intake/1-0-0.json`):**

```json
{
  "type": "form_binding_spec",
  "form_id": "googleforms::1FAIpQLSe_example",
  "binding_id": "example_intake",
  "version": "1.0.0",
  "description": "Example intake form with PHQ-9 and GAD-7",
  "sections": [
    {
      "name": "PHQ-9 Section",
      "instrument_id": "phq9",
      "instrument_version": "1.0.0",
      "bindings": [
        { "item_id": "phq9_item1", "by": "field_key", "value": "entry.123456001" },
        { "item_id": "phq9_item2", "by": "field_key", "value": "entry.123456002" },
        { "item_id": "phq9_item3", "by": "field_key", "value": "entry.123456003" },
        { "item_id": "phq9_item4", "by": "field_key", "value": "entry.123456004" },
        { "item_id": "phq9_item5", "by": "field_key", "value": "entry.123456005" },
        { "item_id": "phq9_item6", "by": "field_key", "value": "entry.123456006" },
        { "item_id": "phq9_item7", "by": "field_key", "value": "entry.123456007" },
        { "item_id": "phq9_item8", "by": "field_key", "value": "entry.123456008" },
        { "item_id": "phq9_item9", "by": "field_key", "value": "entry.123456009" }
      ]
    },
    {
      "name": "GAD-7 Section",
      "instrument_id": "gad7",
      "instrument_version": "1.0.0",
      "bindings": [
        { "item_id": "gad7_item1", "by": "field_key", "value": "entry.789012001" },
        { "item_id": "gad7_item2", "by": "field_key", "value": "entry.789012002" },
        { "item_id": "gad7_item3", "by": "field_key", "value": "entry.789012003" },
        { "item_id": "gad7_item4", "by": "field_key", "value": "entry.789012004" },
        { "item_id": "gad7_item5", "by": "field_key", "value": "entry.789012005" },
        { "item_id": "gad7_item6", "by": "field_key", "value": "entry.789012006" },
        { "item_id": "gad7_item7", "by": "field_key", "value": "entry.789012007" }
      ]
    }
  ]
}
```

Validate against `form_binding_spec.schema.json`.

**Outputs:**

- `form-binding-registry/README.md`
- `form-binding-registry/bindings/example_intake/1-0-0.json`

---

### Step 4: Package Foundation & Registry Loaders [G1: Code Readiness]

**Objective:** Create Python package scaffold with registry loading.

**Prompt:**

Create the final-form package structure:

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
├── conftest.py
└── test_registry.py
```

**Registry loader requirements:**

1. `InstrumentRegistry` class:
   - Load from `instrument-registry/instruments/<id>/<version>.json`
   - Validate against schema
   - Lookup by `(instrument_id, version)`

2. `BindingRegistry` class:
   - Load from `form-binding-registry/bindings/<id>/<version>.json`
   - Validate against schema
   - Lookup by `(binding_id, version)`

3. Pydantic models matching the JSON schemas

4. CLI skeleton with `--binding`, `--instrument-registry`, `--form-binding-registry` flags

**pyproject.toml dependencies:**
- pydantic >= 2.0
- typer
- jsonschema
- rich

**Commands:**

```bash
pytest tests/test_registry.py -v
ruff check final_form/
```

**Outputs:**

- `final_form/__init__.py`
- `final_form/registry/__init__.py`
- `final_form/registry/instruments.py`
- `final_form/registry/bindings.py`
- `final_form/registry/models.py`
- `final_form/io.py`
- `final_form/cli.py`
- `pyproject.toml`
- `tests/conftest.py`
- `tests/test_registry.py`

---

### Step 5: Mapping Engine [G1: Code Readiness]

**Objective:** Implement form item → instrument item mapping.

**Prompt:**

Create the mapping engine:

```
final_form/
└── mapping/
    ├── __init__.py
    └── mapper.py
```

**Mapper behavior:**

1. Takes: canonical form response + binding spec
2. For each section in binding spec:
   - For each binding in section:
     - If `by == "field_key"`: find form item where `field_key == value`
     - If `by == "position"`: find form item where `position == value`
     - Map to `instrument_item_id`
3. **Error if form item not found** (no fallback to question text, no fuzzy matching)
4. Returns: mapped items with `instrument_id`, `item_id`, `raw_answer`

**Critical:** The mapper is purely mechanical. It does not interpret question text or guess mappings.

**Commands:**

```bash
pytest tests/test_mapper.py -v
```

**Outputs:**

- `final_form/mapping/__init__.py`
- `final_form/mapping/mapper.py`
- `tests/test_mapper.py`

---

### Step 6: Recoding Engine [G1: Code Readiness]

**Objective:** Implement text → numeric value recoding.

**Prompt:**

Create the recoding engine:

```
final_form/
└── recoding/
    ├── __init__.py
    └── recoder.py
```

**Recoder behavior:**

1. Takes: mapped items + instrument spec
2. For each item:
   - If `raw_answer` is numeric (int or float): validate range, pass through
   - If `raw_answer` is numeric string: parse, validate range, pass through
   - If `raw_answer` is text:
     - Normalize (lowercase, strip whitespace)
     - Check instrument item's `aliases` first (resolve to canonical text)
     - Lookup in instrument item's `response_map`
     - Return numeric value
3. **Error if text not in response_map** (no fuzzy matching)
4. Returns: recoded items with numeric values

**Commands:**

```bash
pytest tests/test_recoder.py -v
```

**Outputs:**

- `final_form/recoding/__init__.py`
- `final_form/recoding/recoder.py`
- `tests/test_recoder.py`

---

### Step 7: Validation Layer [G1: Code Readiness]

**Objective:** Light validation after mapping and recoding.

**Prompt:**

Create validation checks:

```
final_form/
└── validation/
    ├── __init__.py
    └── checks.py
```

**Validation checks:**

1. **Completeness:** All items in binding spec present
2. **Range:** All values within instrument's response range (0 to max anchor)
3. **Missing:** Flag missing items with count

**Output:** `ValidationResult` with:
- `valid: bool`
- `completeness: float` (0.0 to 1.0)
- `missing_items: list[str]`
- `out_of_range_items: list[str]`
- `errors: list[str]`

**Commands:**

```bash
pytest tests/test_validation.py -v
```

**Outputs:**

- `final_form/validation/__init__.py`
- `final_form/validation/checks.py`
- `tests/test_validation.py`

---

### Step 8: Generic Scoring Engine [G1: Code Readiness]

**Objective:** Single scoring engine that interprets instrument specs.

**Prompt:**

Create the scoring engine:

```
final_form/
└── scoring/
    ├── __init__.py
    ├── engine.py
    ├── methods.py
    └── reverse.py
```

**Scoring engine behavior:**

1. Takes: recoded items + instrument spec
2. For each scale in instrument spec:
   - Get values for `items` in scale
   - Apply reverse scoring for items in `reversed_items` (max_value - value)
   - Compute score using `method`:
     - `"sum"`: sum of values
     - `"average"`: mean of values
     - `"sum_then_double"`: sum * 2
   - Handle missing items:
     - If missing <= `missing_allowed`: prorate or flag partial
     - If missing > `missing_allowed`: error
3. Returns: scale scores with values

**Critical:** No per-questionnaire code. The engine reads everything from the instrument spec.

**Commands:**

```bash
pytest tests/test_scoring.py -v --cov=final_form.scoring
```

**Outputs:**

- `final_form/scoring/__init__.py`
- `final_form/scoring/engine.py`
- `final_form/scoring/methods.py`
- `final_form/scoring/reverse.py`
- `tests/test_scoring.py`
- `tests/test_phq9_scoring.py`
- `tests/test_gad7_scoring.py`

---

### Step 9: Interpretation Layer [G1: Code Readiness]

**Objective:** Apply severity bands and labels.

**Prompt:**

Create the interpretation layer:

```
final_form/
└── interpretation/
    ├── __init__.py
    └── interpreter.py
```

**Interpreter behavior:**

1. Takes: scale scores + instrument spec
2. For each scale score:
   - Find matching range in `interpretations` where `min <= score <= max`
   - Return `label` (e.g., "Moderate")
3. Handle edge cases (score at boundary uses that range)
4. Returns: interpreted scores with labels

**Commands:**

```bash
pytest tests/test_interpretation.py -v
```

**Outputs:**

- `final_form/interpretation/__init__.py`
- `final_form/interpretation/interpreter.py`
- `tests/test_interpretation.py`

---

### Step 10: MeasurementEvent Emitter [G1: Code Readiness]

**Objective:** Build FHIR-aligned output objects.

**Prompt:**

Create the emitter:

```
final_form/
└── emitters/
    ├── __init__.py
    └── measurement.py
```

**Emitter builds:**

1. **MeasurementEvent** (one per instrument):
   ```json
   {
     "schema": "com.lifeos.measurement_event.v1",
     "measurement_event_id": "<uuid>",
     "instrument_id": "phq9",
     "instrument_version": "1.0.0",
     "subject_id": "<from form response>",
     "timestamp": "<from form response>",
     "source": {
       "form_id": "<from form response>",
       "form_submission_id": "<from form response>",
       "form_correlation_id": "<derived or provided>",
       "binding_id": "<from binding spec>",
       "binding_version": "<from binding spec>"
     },
     "observations": [...],
     "telemetry": {
       "processed_at": "<now>",
       "final_form_version": "0.1.0",
       "instrument_spec": "phq9@1.0.0",
       "form_binding_spec": "example_intake@1.0.0"
     }
   }
   ```

2. **Observations** (items + scales):
   ```json
   {
     "schema": "com.lifeos.observation.v1",
     "observation_id": "<uuid>",
     "instrument_id": "phq9",
     "code": "phq9_item1",
     "kind": "item",
     "value": 2,
     "value_type": "integer"
   }
   ```

**Commands:**

```bash
pytest tests/test_emitters.py -v
```

**Outputs:**

- `final_form/emitters/__init__.py`
- `final_form/emitters/measurement.py`
- `tests/test_emitters.py`

---

### Step 11: Diagnostics Collector [G1: Code Readiness]

**Objective:** Collect and emit processing diagnostics.

**Prompt:**

Create the diagnostics system:

```
final_form/
└── diagnostics/
    ├── __init__.py
    ├── collector.py
    └── models.py
```

**Diagnostic object:**

```json
{
  "form_submission_id": "...",
  "binding_id": "example_intake",
  "status": "success|partial|failed",
  "instruments_processed": ["phq9", "gad7"],
  "errors": [
    { "code": "UNMAPPED_FIELD", "message": "...", "field_key": "..." }
  ],
  "warnings": [
    { "code": "MISSING_ITEM", "message": "...", "item_id": "..." }
  ],
  "quality": {
    "phq9": { "completeness": 1.0, "missing_items": [] },
    "gad7": { "completeness": 0.86, "missing_items": ["gad7_item7"] }
  }
}
```

**Commands:**

```bash
pytest tests/test_diagnostics.py -v
```

**Outputs:**

- `final_form/diagnostics/__init__.py`
- `final_form/diagnostics/collector.py`
- `final_form/diagnostics/models.py`
- `tests/test_diagnostics.py`

---

### Step 12: CLI Integration & Pipeline [G2: Pre-Release]

**Objective:** Wire everything into CLI.

**Prompt:**

Complete the CLI:

```
final_form/
├── cli/
│   └── run.py
└── pipeline/
    └── orchestrator.py
```

**CLI interface:**

```bash
final-form run \
  --in forms.jsonl \
  --out measurements.jsonl \
  --binding example_intake \
  --binding-version 1.0.0 \
  --instrument-registry ./instrument-registry \
  --form-binding-registry ./form-binding-registry \
  --diagnostics diag.jsonl
```

**Flags:**
- `--in` (required): Input JSONL path
- `--out` (required): Output JSONL path
- `--binding` (required): Binding spec ID
- `--binding-version` (optional): Binding version (default: latest)
- `--instrument-registry` (optional): Path (default: env var)
- `--form-binding-registry` (optional): Path (default: env var)
- `--diagnostics` (optional): Diagnostics output path

**Pipeline orchestrator:**

1. Load binding spec
2. Load instrument specs for all instruments in binding
3. Read input JSONL
4. For each record:
   - Map → Recode → Validate → Score → Interpret → Emit
   - Collect diagnostics
5. Write output JSONL
6. Write diagnostics (if specified)

**Commands:**

```bash
pytest tests/test_cli.py -v
pytest tests/integration/test_pipeline.py -v

# Manual test
final-form run \
  --in tests/fixtures/sample.jsonl \
  --out /tmp/out.jsonl \
  --binding example_intake \
  --instrument-registry ./instrument-registry \
  --form-binding-registry ./form-binding-registry
```

**Outputs:**

- `final_form/cli/run.py`
- `final_form/pipeline/__init__.py`
- `final_form/pipeline/orchestrator.py`
- `tests/test_cli.py`
- `tests/integration/test_pipeline.py`

---

### Step 13: Golden Tests & Determinism [G2: Pre-Release]

**Objective:** Comprehensive tests with determinism verification.

**Prompt:**

Create golden test suite:

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
└── test_determinism.py
```

**Golden test approach:**
1. Input: canonical form response + binding spec
2. Expected: exact MeasurementEvent output (including UUIDs if deterministic)
3. Assert equality

**Determinism test:**
```python
def test_determinism():
    """Same input must produce same output every time."""
    for _ in range(5):
        result = process(input_fixture)
        assert result == expected_output
```

**Test cases:**
- Complete PHQ-9 (all items, all valid)
- Partial PHQ-9 (1 item missing)
- Text anchor responses (need recoding)
- Out-of-range values (should error)
- Multi-instrument form (PHQ-9 + GAD-7)

**Commands:**

```bash
pytest tests/golden/ -v
pytest tests/test_determinism.py -v
pytest tests/ -v --cov=final_form --cov-report=term-missing
```

**Outputs:**

- `tests/fixtures/canonical/phq9_complete.json`
- `tests/fixtures/canonical/phq9_partial.json`
- `tests/fixtures/canonical/gad7_complete.json`
- `tests/fixtures/canonical/multi_instrument.json`
- `tests/golden/phq9_complete_expected.json`
- `tests/golden/phq9_partial_expected.json`
- `tests/golden/gad7_complete_expected.json`
- `tests/test_determinism.py`
- `.github/workflows/ci.yml`

---

### Step 14: Documentation & Release [G4: Post-Implementation]

**Objective:** Documentation and v0.1.0 release.

**Prompt:**

Create documentation:

1. **README.md** — Installation, quick start, CLI usage
2. **docs/ARCHITECTURE.md** — Link to FINAL-FORM-ARCH.md
3. **docs/REGISTRIES.md** — How to create instrument specs and binding specs
4. **docs/CLI.md** — Full CLI reference

Update `pyproject.toml` version to `0.1.0`.

Create git tag `v0.1.0`.

**Commands:**

```bash
python -m build
twine check dist/*
git tag -a v0.1.0 -m "Release v0.1.0"
```

**Outputs:**

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/REGISTRIES.md`
- `docs/CLI.md`
- `CHANGELOG.md`
- Updated `pyproject.toml`

---

## Models & Tools

**Dependencies:**
- Python 3.11+
- pydantic >= 2.0
- typer
- jsonschema
- rich

**Dev Dependencies:**
- pytest
- pytest-cov
- ruff
- mypy

## Repository

**Branch:** `feat/final-form-v0.1.0`

**Merge Strategy:** squash

## Success Criteria

This implementation is successful when:

1. **No inference:** CLI requires `--binding`, mapper errors on unmapped fields, recoder errors on unknown text
2. **Determinism:** Same input + binding + instruments → same MeasurementEvent output, every time
3. **FHIR-aligned:** Output is MeasurementEvent with Observations, full telemetry
4. **Registry-driven:** Scoring rules from instrument specs, no per-questionnaire code
5. **Golden tests pass:** PHQ-9, GAD-7 with 100% accuracy
6. **Coverage:** 80% overall, 95% scoring engine
7. **CI green:** Lint + tests pass

## Future Versions

| Version | Scope |
|---------|-------|
| **v0.2** | ~13 instruments, enhanced diagnostics |
| **v0.3** | correlation_id support, batch correlation |
| **v1.0** | Stable API, plugin architecture |
| **v2.0** | Authoring tools (fuzzy matching for binding generation) |
| **v3.0** | Cross-domain expansion (labs, vitals, wearables) |

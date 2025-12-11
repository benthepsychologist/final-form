# FINAL-FORM Architecture Overview

**Version:** 0.2.0
**Status:** Architecture-Complete

---

## 1. Purpose

**finalform** is the semantic data engine that transforms canonical JSON records into **immutable, self-describing MeasurementEvent objects** with full provenance. It performs deterministic, domain-aware processing including mapping, recoding, scoring, interpretation, and validation.

finalform is the authoritative place where raw meaning becomes structured, validated signal. Once data passes through finalform, no further cleaning or scoring occurs downstream. It is the "last mile" of semantic processing before projection, vectorization, or analysis.

**Key Principle:** finalform outputs **measure instances**, not datasets. Datasets are projections of measure instances—that's downstream work.

---

## 2. Role in the Pipeline

finalform sits between canonizer and downstream consumers:

```
[raw ingest] → [canonizer] → **finalform** → [projection/analytics/vector-projector]
```

| Component | Responsibility |
|-----------|----------------|
| **canonizer** | Structural/canonical normalization (shape only, no semantics) |
| **finalform** | Semantic/domain normalization (scoring, interpretation, provenance) |
| **projection** | Transform measure instances into datasets (long/wide tables) |
| **vector-projector** | Representation into embeddings/feature spaces |

This keeps responsibilities clean and modular.

---

## 3. Core Architectural Principles

### 3.1 No Runtime Inference

**finalform never guesses.**

- It does not infer which questionnaire is present
- It does not fuzzy-match question text to items
- It does not auto-detect instruments

Instead, it is **handed explicit bindings**:
- Form binding spec tells it: "field X in form Y maps to item Z of instrument W"
- Instrument spec tells it: "instrument W has these items, scoring rules, and interpretation bands"

Fuzzy matching / wording banks belong in **authoring tools** that generate binding specs—not in the scoring runtime.

### 3.2 Deterministic

Given the same canonical input + binding spec + instrument spec, finalform **always** produces the same output. This enables:
- Replayability
- Diffability across versions
- Research reproducibility

### 3.3 Pure Semantics

finalform does not:
- Contact external APIs
- Perform ingestion
- Transform provider shapes
- Perform vectorization
- Build datasets

It only handles semantic meaning-making.

### 3.4 Local & Modular

It can run in:
- A pipeline (lorchestra)
- A researcher's local script
- A notebook
- A CLI command

...without requiring the full stack.

### 3.5 Registry-Driven

All semantic knowledge lives in registries, not code:
- Instrument definitions (what is PHQ-9?)
- Form bindings (how does this Google Form map to PHQ-9?)
- Finalization transforms (how do we emit observations?)

Changing scoring rules means updating registries, not code.

---

## 4. Three-Layer Data Model

### 4.1 Separation of Concerns

| Layer | Content | Owner |
|-------|---------|-------|
| **Canonical Form Response** | Shape only. `field_key`, `position`, `raw_answer`. No semantics. | canonizer |
| **Form Binding Spec** | "For form X version Y, field Z maps to instrument W item N" | form-binding-registry |
| **Instrument Spec** | What is PHQ-9? Items, anchors, scoring rules, interpretation bands | instrument-registry |

finalform consumes all three to produce **MeasurementEvents**.

### 4.2 Why This Matters

In the real world, a "form" contains multiple instruments woven together with platform-specific IDs (Google Forms `entry.123456`, Typeform UUIDs, etc.). Runtime guessing is fragile and loses rigor.

The fix: **explicit binding specs authored at design-time**, not inference at runtime.

---

## 5. Output Model: FHIR-Aligned

### 5.1 Nomenclature (Aligned with FHIR R4)

| Our Term | FHIR Equivalent | Meaning |
|----------|-----------------|---------|
| **Measure** (Instrument) | `Questionnaire` | Definition of a psychometric or clinical tool (PHQ-9, GAD-7) |
| **MeasurementEvent** | `QuestionnaireResponse` | One administration instance for one subject |
| **Observation** | `Observation` | Atomic values: item scores, scale scores, interpretations |

This alignment enables future interoperability with:
- Dataverse Healthcare
- Azure Health Data Services
- Epic/Cerner FHIR endpoints
- REDCap, ePRO platforms

### 5.2 What finalform Outputs

For each instrument found in a form submission, finalform emits **one MeasurementEvent** containing:

1. **Identity/Linkage** — `subject_id`, `form_id`, `form_submission_id`, `form_correlation_id`, `measurement_event_id`
2. **Instrument Metadata** — `instrument_id`, `instrument_version`, `binding_id`
3. **Observations** — Array of item values and scale scores
4. **Telemetry** — `processed_at`, `finalform_version`, spec versions used

**MeasurementEvents are:**
- Append-only
- Immutable
- Self-describing
- Ready for projection into any dataset format

### 5.3 Example Output Structure

```json
{
  "schema": "com.lifeos.measurement_event.v1",
  "measurement_event_id": "uuid-...",
  "instrument_id": "phq9",
  "instrument_version": "1.0.0",
  "subject_id": "contact::<uuid>",
  "timestamp": "2025-11-29T18:00:00Z",
  "source": {
    "form_id": "googleforms::<id>",
    "form_submission_id": "subm::<id>",
    "form_correlation_id": "intake_v1::<correlation>",
    "binding_id": "intake_v1",
    "binding_version": "1.2.0"
  },
  "observations": [
    {
      "schema": "com.lifeos.observation.v1",
      "observation_id": "uuid-item1",
      "instrument_id": "phq9",
      "code": "phq9_item1",
      "kind": "item",
      "value": 2,
      "value_type": "integer"
    },
    {
      "schema": "com.lifeos.observation.v1",
      "observation_id": "uuid-total",
      "instrument_id": "phq9",
      "code": "phq9_total",
      "kind": "scale",
      "value": 16,
      "label": "Moderately severe",
      "value_type": "integer"
    }
  ],
  "telemetry": {
    "processed_at": "2025-11-29T18:02:00Z",
    "finalform_version": "0.3.0",
    "instrument_spec": "phq9@1.0.0",
    "form_binding_spec": "intake_v1@1.2.0",
    "finalform_spec": "phq9_finalform@1.0.0"
  }
}
```

---

## 6. Registry Architecture

### 6.1 Three Registries

Mirroring canonizer's pattern (shapes, forms, transforms), finalform uses three registries:

| Registry | Contents | Format |
|----------|----------|--------|
| **instrument-registry** | Instrument definitions (PHQ-9, GAD-7, etc.) | JSON, SemVer'd |
| **form-binding-registry** | Form binding specs (form→instrument mappings) | JSON, SemVer'd |
| **finalform-registry** | Finalization transform specs | JSON, SemVer'd |

All registries use **JSON only** (not YAML). JSON is deterministic, machine-validated, and diffable.

### 6.2 Instrument Registry

Location: `instrument-registry/instruments/<id>/<version>.json`

Example: `instrument-registry/instruments/phq9/1-0-0.json`

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
  ],
  "scales": [
    {
      "scale_id": "phq9_total",
      "name": "PHQ-9 Total Score",
      "items": ["phq9_item1", "phq9_item2", "..."],
      "method": "sum",
      "reversed_items": [],
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

### 6.3 Form Binding Registry

Location: `form-binding-registry/bindings/<binding_id>/<version>.json`

Example: `form-binding-registry/bindings/intake_v1/1-2-0.json`

```json
{
  "type": "form_binding_spec",
  "form_id": "googleforms::<id>",
  "binding_id": "intake_v1",
  "version": "1.2.0",
  "description": "Intake form layout mapping fields to instruments",
  "sections": [
    {
      "name": "PHQ-9 block",
      "instrument_id": "phq9",
      "instrument_version": "1.0.0",
      "bindings": [
        {
          "item_id": "phq9_item1",
          "by": "field_key",
          "value": "Q1_12345"
        },
        {
          "item_id": "phq9_item2",
          "by": "position",
          "value": 15
        }
      ]
    },
    {
      "name": "GAD-7 block",
      "instrument_id": "gad7",
      "instrument_version": "1.0.0",
      "bindings": [...]
    }
  ]
}
```

**Key Points:**
- Supports both `field_key` (preferred, survives reordering) and `position` binding
- Multiple instruments per form
- Explicit versioning: change form layout → bump binding version

### 6.4 Finalization Registry (Transform Specs)

Location: `finalform-registry/transforms/<instrument_id>/<version>.json`

Example: `finalform-registry/transforms/phq9/1-0-0.json`

```json
{
  "type": "finalform_spec",
  "instrument_id": "phq9",
  "version": "1.0.0",
  "input_shape": "com.lifeos.form.response.v1",
  "output_shapes": [
    "com.lifeos.measurement_event.v1",
    "com.lifeos.observation.v1"
  ],
  "uses_instrument_spec": "phq9@1.0.0",
  "description": "Final-form scoring for PHQ-9",
  "rules": {
    "item_source": "form_binding_spec",
    "scale_scoring": "instrument_spec",
    "observation_emission": "standard_questionnaire_observation_v1"
  }
}
```

### 6.5 SemVer Discipline

All specs are independently versioned:

| Spec | Example Version |
|------|-----------------|
| Canonical input shape | `com.lifeos.form.response.v1` |
| Instrument spec | `phq9@1.0.0` |
| Form binding spec | `intake_v1@1.2.0` |
| Finalization transform | `phq9_finalform@1.0.3` |
| Output shapes | `measurement_event.v1`, `observation.v1` |

**Version bump rules:**
- **Major:** Change field meaning, remove fields, alter scoring rules
- **Minor:** Add optional fields, new aliases, new scales
- **Patch:** Bug fixes that don't change outputs for existing data

Telemetry records all versions used, enabling full reproducibility.

---

## 7. Processing Contract

### 7.1 Runtime Inputs

```python
process_form_response(
    response: CanonicalFormResponse,      # from canonizer
    binding_spec: FormBindingSpec,         # from form-registry
    instrument_registry: InstrumentRegistry  # from instrument-registry
) -> list[MeasurementEvent]
```

finalform never has to "figure out which questionnaire is where."

### 7.2 Processing Flow

```
canonical form_response (from canonizer)
  ↓
lookup binding_spec (by form_id)
  ↓
for each section in binding_spec:
  ↓
  resolve instrument_spec (from instrument-registry)
  ↓
  map form items → instrument items (mechanical, no inference)
  ↓
  recode values (text → numeric using response_map)
  ↓
  validate (range checks, completeness)
  ↓
  score (apply scoring rules from instrument_spec)
  ↓
  interpret (apply interpretation bands)
  ↓
  emit MeasurementEvent + Observations
  ↓
write output + diagnostics
```

### 7.3 Error Handling

If something doesn't map:
- **Missing field_key in binding:** Error, fail the record
- **Unknown answer value:** Error, fail the record
- **Missing items beyond threshold:** Warning, compute partial score with flag

finalform errors loudly. No silent fallbacks.

---

## 8. Input & Output Contracts

### 8.1 Inputs

**From canonizer:**
- `com.lifeos.form.response.v1` — shape only, stable field keys and positions
- JSONL format for batch processing

**Example canonical form response:**
```json
{
  "schema": "com.lifeos.form.response.v1",
  "form_id": "googleforms::<id>",
  "submission_id": "abc123",
  "submitted_at": "2025-11-29T17:00:00Z",
  "respondent_id": "contact::<uuid>",
  "items": [
    {
      "field_key": "Q1_12345",
      "position": 1,
      "question_text": "Over the last 2 weeks...",
      "raw_answer": "Nearly every day"
    }
  ]
}
```

Canonizer does **not** know about PHQ-9, GAD-7, etc. It just produces reliable, versioned shapes.

### 8.2 Outputs

- `com.lifeos.measurement_event.v1` — one per instrument per submission
- Contains embedded `com.lifeos.observation.v1` array
- JSONL format for batch output
- Optional diagnostics output (errors, warnings, quality metrics)

---

## 9. Internal Architecture

### 9.1 Modules

```
finalform/
├── registry/           # Registry loaders
│   ├── instruments.py  # Load instrument specs
│   ├── bindings.py     # Load form binding specs
│   └── transforms.py   # Load finalization specs
├── mapping/            # Form item → instrument item mapping
├── recoding/           # Text → numeric conversion
├── validation/         # Range checks, completeness
├── scoring/            # Generic scoring engine
├── interpretation/     # Severity bands, labels
├── emitters/           # MeasurementEvent builders
├── diagnostics/        # Error/warning collection
├── cli/                # Typer-based CLI
└── schemas/            # JSON Schema definitions
```

### 9.2 Generic Scoring Engine

**One engine, many instruments.**

The scoring engine:
1. Loads instrument spec from registry
2. Applies reverse scoring for specified items
3. Computes scales using method (`sum`, `average`, `sum_then_double`)
4. Applies interpretation ranges
5. Handles missing data per threshold

No per-questionnaire code. Registry is source of truth.

---

## 10. Where Inference Lives (Not Here)

Fuzzy matching and "pretty close" detection belong in **authoring tools**, not runtime:

| Mode | What Happens |
|------|--------------|
| **Runtime (finalform)** | Uses explicit bindings only. Fails if missing/wrong. Deterministic. |
| **Authoring (CLI tool)** | Proposes mappings based on text similarity. Human approves. Writes binding spec. |

The authoring tool might say: "Q1_12345 text is 94% similar to 'Little interest or pleasure'. Map to phq9_item1?"

If you accept, it writes the binding spec. finalform then consumes that spec mechanically.

---

## 11. Relationship to Datasets / Projection

finalform outputs **MeasurementEvents**, not datasets.

Projection is downstream and trivial:

| Projection | Method |
|------------|--------|
| Item-level long table | One row per `(subject_id, instrument_id, item_id, time)` |
| Scale-level long table | One row per `(subject_id, instrument_id, scale_id, time)` |
| Wide table per instrument | Pivot items into columns |

These are views over MeasurementEvents. Scoring logic never leaks into the view layer.

---

## 12. CLI Overview

### 12.1 Primary Command

```bash
finalform run \
  --in forms.jsonl \
  --out measurements.jsonl \
  --binding intake_v1 \
  --instrument-registry ./instrument-registry \
  --form-binding-registry ./form-binding-registry \
  --diagnostics diag.jsonl
```

### 12.2 Flags

| Flag | Required | Description |
|------|----------|-------------|
| `--in` | Yes | Input JSONL (canonical form responses) |
| `--out` | Yes | Output JSONL (MeasurementEvents) |
| `--binding` | Yes | Binding spec ID or path |
| `--instrument-registry` | No | Path to instrument registry (default: env var) |
| `--form-binding-registry` | No | Path to form binding registry (default: env var) |
| `--diagnostics` | No | Optional diagnostics output path |

**No auto-detection.** The binding is explicit.

---

## 13. Future Roadmap

| Version | Scope |
|---------|-------|
| **v0.1** | PHQ-9, GAD-7 with full pipeline |
| **v0.2** | ~13 instruments, missingness metrics |
| **v0.3** | Measurement event emitter, correlation_id support |
| **v1.0** | Stable API, plugin architecture |
| **v2.0** | Cross-domain expansion (labs, vitals, wearables) |

---

## 14. Summary

finalform is a **MeasurementEvent factory**:

1. **Consumes:** Canonical form responses + binding specs + instrument specs
2. **Produces:** Immutable, self-describing MeasurementEvents with Observations
3. **Guarantees:** Determinism, full provenance, FHIR-aligned nomenclature
4. **Does not:** Infer instruments, build datasets, contact external APIs

The system is designed to be:
- **Explicit** — no magic, all mappings authored upfront
- **Registry-driven** — change rules by updating JSON, not code
- **Reproducible** — same inputs always produce same outputs
- **Future-proof** — FHIR alignment enables healthcare interop

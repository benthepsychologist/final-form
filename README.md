# final-form

Semantic processing engine for psychological instruments with FHIR-aligned output.

## Overview

final-form transforms canonical form responses (from questionnaire platforms like Google Forms) into structured MeasurementEvent objects with:

- **Mapping**: Form fields → instrument items using binding specs
- **Recoding**: Text responses → numeric values using response maps
- **Scoring**: Compute scale scores (sum, average, proration)
- **Interpretation**: Apply severity bands and clinical labels
- **Provenance**: Full telemetry tracking all spec versions

## Supported Instruments

- **PHQ-9**: Patient Health Questionnaire (10 items: 9 symptoms + 1 severity)
- **GAD-7**: Generalized Anxiety Disorder (8 items: 7 symptoms + 1 severity)

## Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

### CLI Usage

Process form responses through the pipeline:

```bash
final-form run \
  --in forms.jsonl \
  --out measurements.jsonl \
  --binding example_intake \
  --instrument-registry ./instrument-registry \
  --form-binding-registry ./form-binding-registry \
  --diagnostics diagnostics.jsonl
```

### Python API

```python
from final_form.pipeline import Pipeline, PipelineConfig

config = PipelineConfig(
    instrument_registry_path=Path("instrument-registry"),
    binding_registry_path=Path("form-binding-registry"),
    binding_id="example_intake",
    binding_version="1.0.0",
)

pipeline = Pipeline(config)

result = pipeline.process({
    "form_id": "googleforms::abc",
    "form_submission_id": "sub_123",
    "subject_id": "contact::xyz",
    "timestamp": "2025-01-15T10:30:00Z",
    "items": [
        {"field_key": "entry.123456001", "answer": "several days"},
        # ... more items
    ],
})

for event in result.events:
    print(event.model_dump_json(by_alias=True))
```

## Input Format

Canonical form responses (JSONL):

```json
{
  "form_id": "googleforms::1FAIpQLSe_example",
  "form_submission_id": "submission_12345",
  "subject_id": "contact::abc123",
  "timestamp": "2025-01-15T10:30:00Z",
  "items": [
    { "field_key": "entry.123456001", "position": 1, "answer": "several days" },
    { "field_key": "entry.123456002", "position": 2, "answer": "not at all" }
  ]
}
```

## Output Format

MeasurementEvent (JSONL):

```json
{
  "schema": "com.lifeos.measurement_event.v1",
  "measurement_event_id": "uuid",
  "instrument_id": "phq9",
  "instrument_version": "1.0.0",
  "subject_id": "contact::abc123",
  "timestamp": "2025-01-15T10:30:00Z",
  "source": {
    "form_id": "googleforms::...",
    "form_submission_id": "...",
    "binding_id": "example_intake",
    "binding_version": "1.0.0"
  },
  "observations": [
    {
      "schema": "com.lifeos.observation.v1",
      "code": "phq9_total",
      "kind": "scale",
      "value": 12.0,
      "label": "Moderate"
    }
  ],
  "telemetry": {
    "processed_at": "2025-01-15T10:31:00Z",
    "final_form_version": "0.1.0",
    "instrument_spec": "phq9@1.0.0"
  }
}
```

## Registries

### Instrument Registry

Located at `instrument-registry/instruments/<id>/<version>.json`:

- Defines items, response maps, scales, and interpretations
- Each instrument is versioned (SemVer)
- Validated against `schemas/instrument_spec.schema.json`

### Form Binding Registry

Located at `form-binding-registry/bindings/<id>/<version>.json`:

- Maps form platform fields to instrument items
- Supports mapping by `field_key` or `position`
- Validated against `schemas/form_binding_spec.schema.json`

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=final_form

# Run specific test file
pytest tests/test_pipeline.py -v
```

## Architecture

```
canonical form_response
         │
         ▼
┌─────────────────────┐
│  Load Binding Spec  │ ← form-binding-registry
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   Map Form Items    │  field_key/position → instrument_item_id
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
│   Build Event       │  MeasurementEvent + Observations
└─────────────────────┘
         │
         ▼
MeasurementEvents (JSONL) + Diagnostics
```

## License

MIT

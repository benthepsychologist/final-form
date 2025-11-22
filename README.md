# final-form

**Semantic processing engine for mental health questionnaire responses**

Transforms canonical JSON input (from [canonizer](https://github.com/benthepsychologist/canonizer)) into fully scored, normalized, validated, research-ready output.

## Overview

`final-form` is the semantic layer that sits after canonization, handling:

1. **Mapping**: Platform-specific IDs → Canonical item IDs
2. **Recoding**: Text/numeric answer values → Numeric values
3. **Validation**: Completeness and range checks
4. **Scoring**: Generic engine interpreting registry rules
5. **Interpretation**: Severity bands and clinical metadata

## Architecture

```
Canonical Form Response (from canonizer)
    ↓
Mapper (item_id + value recoding)
    ↓
Validator (completeness + ranges)
    ↓
Scoring Engine (generic, registry-driven)
    ↓
Interpretation Layer (severity bands + metadata)
    ↓
Scored Response (research-ready JSONL)
```

## Installation

```bash
# Install in development mode
cd final-form
pip install -e ".[dev]"
```

## Usage

```bash
final-form \
  --in forms.jsonl \
  --out scored.jsonl \
  --mapping ~/questionnaire-registry/mappings/google_forms/mbc_initial_phq9_v1.json \
  --questionnaire-registry ~/questionnaire-registry
```

### Input Format

Canonical form responses from canonizer (JSONL):

```json
{
  "form_id": "mbc_initial_assessment",
  "response_id": "resp_001",
  "timestamp": "2024-01-15T10:30:00Z",
  "items": [
    {"question_id": "entry.123456", "answer_value": "Several days"},
    {"question_id": "entry.123457", "answer_value": 2},
    {"question_id": "phq_9_3", "answer_value": "1"}
  ]
}
```

### Output Format

Scored responses with interpretation (JSONL):

```json
{
  "response_id": "resp_001",
  "measure_id": "phq_9",
  "measure_name": "Patient Health Questionnaire-9",
  "timestamp": "2024-01-15T10:30:00Z",
  "items": [
    {"canonical_item_id": "phq_9_1", "original_value": "Several days", "numeric_value": 1, "reversed": false},
    {"canonical_item_id": "phq_9_2", "original_value": 2, "numeric_value": 2, "reversed": false},
    {"canonical_item_id": "phq_9_3", "original_value": "1", "numeric_value": 1, "reversed": false}
  ],
  "subscales": [
    {
      "subscale_name": "phq_9",
      "raw_score": 12,
      "score_range": {
        "min": 10,
        "max": 14,
        "label": "Moderate",
        "severity": "moderate",
        "description": "Moderate depression. Consider counseling, follow-up, and/or pharmacotherapy."
      },
      "included_items": ["phq_9_1", "phq_9_2", ...],
      "completeness": 1.0
    }
  ]
}
```

## Dependencies

- **questionnaire-registry**: Canonical measure definitions (~13 measures)
- **canonizer-registry**: JSON schemas for validation

## Supported Measures

The registry contains ~13 standard mental health measures:

- **Depression & Mood**: PHQ-9, GAD-7
- **Personality**: MSI, IPIP-NEO-60-C
- **Mindfulness**: PHLMS-10, SAFE, JOY
- **Stress & Trauma**: PSS-10, Trauma Exposure, PTSD Screen
- **Self-Perception**: FSCRS
- **Sleep**: Sleep Disturbances
- **Other**: DTS, CFS

## Development Status

**Current**: Step 4/12 - Foundation package structure complete

**Remaining**:
- Step 5: Implement mapper (item mapping + value recoding)
- Step 6: Add validation checks
- Step 7: Build generic scoring engine
- Step 8: Add interpretation layer
- Step 9: Build output emitters
- Step 10: Integrate CLI pipeline
- Step 11: Create test suite
- Step 12: Documentation and release

## License

Apache-2.0

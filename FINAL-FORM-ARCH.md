FINAL-FORM-ARCH.md

(High-Level Architecture & Design Document)

Title

FINAL-FORM Architecture Overview
Version: 0.1.0
Status: Draft (Architecture-Complete)

⸻

1. Purpose

final-form is the semantic data engine that transforms canonical JSON records into their final, research-ready form. It performs deterministic, domain-aware processing, including cleaning, normalization, scoring, interpretation, and semantic validation.

final-form is the authoritative place where raw meaning becomes structured, validated signal. Once data passes through final-form, no further cleaning or scoring occurs downstream. It is the “last mile” of semantic processing before vectorization, analysis, or dashboards.

⸻

2. Role in the Pipeline

final-form sits between canonizer and vector-projector:

[raw ingest] → [canonizer] → **final-form** → [vector-projector] → [analytics]

	•	canonizer solves structural/canonical normalization.
	•	final-form solves semantic/domain normalization.
	•	vector-projector solves representation into embeddings/feature spaces.

This keeps responsibilities clean and modular.

⸻

3. Core Responsibilities

final-form performs five deterministic operations on canonical input:

3.1 Clean
	•	Strip whitespace
	•	Standardize text normalization
	•	Normalize anchor/label variants (e.g., “More than half the time” → “more_than_half”)
	•	Remove noise from source systems

3.2 Normalize
	•	Convert text responses to numeric responses
	•	Enforce allowed ranges and domain constraints
	•	Harmonize naming, item IDs, scales, and response formats

3.3 Score
	•	Compute instrument total scores
	•	Compute subscale scores
	•	Apply scoring rules from the canonical questionnaire definition
	•	Apply transformations (sum, average, reverse-scoring, custom rules)

3.4 Annotate
	•	Add interpretation bands (mild, moderate, severe)
	•	Add metadata (completeness, missing data flags, scoring quality)
	•	Add provenance information

3.5 Emit
	•	Output the final canonical data object (in JSON)
	•	Guaranteed stable, validated, and analysis-ready
	•	May optionally emit intermediate diagnostic records

After emission, the record is considered final and should not be semantically mutated again.

⸻

4. Input & Output Contracts

4.1 Inputs

final-form accepts:
	1.	org.canonical/form_response
	2.	org.canonical/questionnaire_response (unscored or partially processed)
	3.	Future canonical domain objects (e.g., labs, vitals, psychometrics)

Each input type’s schema is governed externally (canonizer-registry + arch-gov).

4.2 Outputs

final-form emits:
	1.	org.canonical/questionnaire_response (semantic, scored, validated)
	2.	Optionally, org.canonical/measurement events (if measurement pipeline enabled)
	3.	Diagnostics (errors, warnings, missingness summaries)

Output schemas must adhere to canonical naming and versioning discipline.

⸻

5. Architectural Principles

5.1 Deterministic

Given the same canonical input, final-form always produces the same output.

5.2 Pure Semantics

final-form does not:
	•	contact external APIs
	•	perform ingestion
	•	transform provider shapes
	•	perform vectorization
It only handles semantic meaning-making.

5.3 Local & Modular

It can run in:
	•	a pipeline (lorchestra)
	•	a researcher’s local script
	•	a notebook
	•	a CLI command
without requiring the full stack.

5.4 Governed
	•	Schemas are validated via canonizer-registry
	•	Semantic rules can be governed by arch-gov (policies + contracts)
	•	Scoring logic is versioned and managed independent of pipeline code

5.5 Testable & Replayable

Every canonical input can be:
	•	replayed
	•	reprocessed
	•	diffed
across versions using the WAL.

⸻

6. Internal Architecture

6.1 Modules
	•	cleaning/ – text and anchor normalization
	•	mapping/ – text→numeric conversion
	•	scoring/ – scoring engines per instrument
	•	interpreters/ – severity & interpretation layers
	•	emitters/ – final JSON builders
	•	diagnostics/ – missingness, outliers, structural issues
	•	cli/ – Typer-based CLI wrapper
	•	schemas/ – internal schema references (pulled from canonizer-registry)

6.2 Execution Path

canonical JSON
  → validator
  → cleaning pipeline
  → normalization pipeline
  → scoring engine (instrument-specific)
  → interpretation
  → validation (post-scoring)
  → final-form output (canonical)
  → diagnostics

All steps are pure functions over JSON.

⸻

7. Extensibility Model

7.1 Instrument Plugins

final-form supports plugin registration:

final_form.plugins.register("phq9", PHQ9Scorer())
final_form.plugins.register("gad7", GAD7Scorer())

Plugins define:
	•	item mappings
	•	scoring rules
	•	interpretation rules

7.2 Domain Expansion

Future domain modules can extend final-form for:
	•	lab results
	•	vitals
	•	wearable data
	•	behavioral logs
	•	session metrics

final-form does not care—only that the input is canonical.

⸻

8. CLI Overview

Example Usage

final-form run --in forms.jsonl --out final.jsonl --instrument phq9

Or auto-detection:

final-form run --in canonical/*.jsonl --out final/

Optional diagnostics:

final-form run --in forms.jsonl --diagnostics diag.json


⸻

9. Integration Points

9.1 With lorchestra

lorch final-form becomes a standard pipeline step in Ops mode.

9.2 With vector-projector

Output from final-form becomes ready input for vector/feature generation.

9.3 With arch-gov

Optional validation of:
	•	instrument rules
	•	scoring rules
	•	schema contracts

9.4 With research SDK

final-form can become the backend for a higher-level final-form-sdk at a later stage.

⸻

10. Future Roadmap
	•	v0: Questionnaires (PHQ-9, GAD-7)
	•	v0.2: Missingness & quality metrics
	•	v0.3: Measurement event emitter
	•	v1.0: Plugin architecture
	•	v2.0: Cross-domain generalization

FINAL-FORM-BUILD-PLAN.md

(Execution & Implementation Plan)

Title

FINAL-FORM Build Plan
Version: 0.1.0
Status: Ready for Implementation

⸻

1. Objective

Build the final-form semantic processing engine that transforms canonical JSON input into fully scored, normalized, validated, research-ready canonical output.

This build plan is minimal, focused, and ready for execution with specwright + agentic coding.

⸻

2. Scope (v0)

Included:
	•	PHQ-9 instrument pipeline
	•	Cleaning + normalization + scoring + interpretation
	•	CLI for batch processing
	•	JSONL-in / JSONL-out
	•	Plugin framework placeholder
	•	Diagnostics (missingness, invalid values)

Excluded:
	•	Dataset adapters (pandas/arrow)
	•	SDK layering
	•	Vectorization
	•	Arch-gov integration

These come later.

⸻

3. Deliverables
	1.	Python package: final_form/
	2.	CLI: final-form
	3.	Module structure:
	•	cleaning/
	•	normalization/
	•	scoring/
	•	interpretation/
	•	emitters/
	•	diagnostics/
	•	cli/
	•	schemas/ (internal references only)
	4.	Test suite:
	•	PHQ9 fixtures (canonical → final-form)
	•	edge cases (missing, illegal values)
	•	golden outputs
	5.	Integration test with canonizer output
	6.	Version: v0.1.0

⸻

4. Work Breakdown Structure (WBS)

Phase 1 — Foundation (Config, Models, IO)
	•	Create package scaffold
	•	JSON loader + JSONL batch reader
	•	Validation wrapper (using canonizer-registry schemas)
	•	Minimal PHQ9 schema references
	•	CLI skeleton with run command

Artifacts:
	•	final_form/__init__.py
	•	final_form/io.py
	•	final_form/cli.py
	•	pyproject.toml

⸻

Phase 2 — Cleaning + Normalization Pipeline
	•	Text cleaning helpers
	•	Anchor normalization
	•	Text→numeric conversion
	•	Range enforcement
	•	Missingness detection

Artifacts:
	•	final_form/cleaning/*.py
	•	final_form/normalization/*.py

⸻

Phase 3 — Scoring Engine (PHQ-9 v0)
	•	Load PHQ9 scoring rules (from questionnaire definition)
	•	Implement item scoring
	•	Reverse scoring support
	•	Compute total score
	•	Validate scoring logic

Artifacts:
	•	final_form/scoring/phq9.py
	•	tests/phq9/test_scoring.py

⸻

Phase 4 — Interpretation Layer
	•	Apply interpretation ranges
	•	Add severity fields
	•	Missingness summary fields

Artifacts:
	•	final_form/interpretation/phq9.py

⸻

Phase 5 — Emitters & Output Builders
	•	Build final canonical questionnaire_response object
	•	Add provenance and metadata fields
	•	Add diagnostic object model

Artifacts:
	•	final_form/emitters/*.py
	•	final_form/diagnostics/*.py

⸻

Phase 6 — CLI Integration & Batch Runner
	•	Connect all phases in one pipeline
	•	Stream JSONL events
	•	Write outputs + diagnostics
	•	Add instrument auto-detection

Artifacts:
	•	final_form/cli/run.py
	•	tests/test_cli.py

⸻

Phase 7 — Tests & Fixtures
	•	Valid PHQ9 canonical inputs
	•	Dirty text inputs (text anchors)
	•	Missing values
	•	Out-of-range values
	•	Golden outputs for final-form results

Artifacts:
	•	tests/fixtures/phq9/*.json
	•	tests/golden/phq9/*.json

⸻

5. Sequence Diagram (High-Level)

canonical JSONL
    →
validate (canonizer-registry)
    →
clean_text
    →
normalize_values
    →
score_items
    →
compute_total
    →
interpret
    →
emit_final_canonical
    →
write_output
    →
diagnostics


⸻

6. Risks & Mitigations

Risk	Mitigation
Scoring logic drift	Use questionnaire definitions as the source of truth
Inconsistent canonical inputs	Validate using canonizer-registry schemas
Researchers misunderstand failures	Produce clear per-record diagnostics
Plugin explosion	Keep v0 scoped to PHQ9 only


⸻

7. Success Criteria
	•	Deterministic PHQ-9 scoring end-to-end
	•	Canonical JSON → final-form JSON with zero ambiguity
	•	CLI can process JSONL batch inputs
	•	Golden test suite passes
	•	Clear error messages and diagnostics
	•	Versioned, repeatable outputs

⸻

8. Future Versions
	•	v0.2 — GAD-7 + missingness metrics
	•	v0.3 — measurement emitter
	•	v1.0 — plugin architecture
	•	v2.0 — SDK wrappers (pandas, arrow)
	•	v3.0 — research façade (batch scoring, embeddings)

⸻

End of FINAL-FORM-BUILD-PLAN.md

⸻

If you want, I’ll now generate:
	•	FINAL-FORM-SPEC.md scaffold
	•	the canonical example pipeline for PHQ9
	•	or the integration stanza for your MASTER-ARCH.md.
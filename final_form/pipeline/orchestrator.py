"""Pipeline orchestrator for form processing.

Coordinates the full processing flow:
1. Load binding spec
2. Load instrument specs for instruments in binding
3. For each form response:
   - Map items using binding
   - Recode values using instrument response_map
   - Validate completeness and ranges
   - Score using generic engine
   - Interpret using severity bands
   - Build MeasurementEvent(s)
   - Collect diagnostics
"""

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from final_form.builders import MeasurementEvent, MeasurementEventBuilder
from final_form.diagnostics import DiagnosticsCollector, FormDiagnostic
from final_form.interpretation import Interpreter
from final_form.mapping import Mapper
from final_form.recoding import Recoder
from final_form.registry import BindingRegistry, InstrumentRegistry
from final_form.registry.models import FormBindingSpec, InstrumentSpec
from final_form.scoring import ScoringEngine
from final_form.validation import Validator


class PipelineConfig(BaseModel):
    """Configuration for the processing pipeline."""

    instrument_registry_path: Path
    binding_registry_path: Path
    binding_id: str
    binding_version: str | None = None
    instrument_schema_path: Path | None = None
    binding_schema_path: Path | None = None
    deterministic_ids: bool = False  # For testing


class ProcessingResult(BaseModel):
    """Result of processing a single form response."""

    form_submission_id: str
    events: list[MeasurementEvent]
    diagnostic: FormDiagnostic
    success: bool


class Pipeline:
    """Orchestrates the form processing pipeline.

    Processes canonical form responses through mapping, recoding,
    validation, scoring, interpretation, and event building stages.
    """

    def __init__(self, config: PipelineConfig) -> None:
        """Initialize the pipeline with configuration.

        Args:
            config: Pipeline configuration specifying registries and binding.
        """
        self.config = config

        # Initialize registries
        self.instrument_registry = InstrumentRegistry(
            config.instrument_registry_path,
            schema_path=config.instrument_schema_path,
        )
        self.binding_registry = BindingRegistry(
            config.binding_registry_path,
            schema_path=config.binding_schema_path,
        )

        # Load binding spec
        self.binding_spec = self.binding_registry.get(
            config.binding_id,
            config.binding_version,
        )

        # Load instrument specs for instruments in binding
        self.instruments: dict[str, InstrumentSpec] = {}
        for section in self.binding_spec.sections:
            inst_id = section.instrument_id
            inst_version = section.instrument_version
            self.instruments[inst_id] = self.instrument_registry.get(
                inst_id,
                inst_version,
            )

        # Initialize processing components
        self.mapper = Mapper()
        self.recoder = Recoder()
        self.validator = Validator()
        self.scoring_engine = ScoringEngine()
        self.interpreter = Interpreter()
        self.builder = MeasurementEventBuilder(
            deterministic_ids=config.deterministic_ids
        )

    def process(self, form_response: dict[str, Any]) -> ProcessingResult:
        """Process a single form response.

        Args:
            form_response: Canonical form response dict with fields:
                - form_id: str
                - form_submission_id: str
                - subject_id: str
                - timestamp: str
                - responses: dict[str, Any] mapping field_key to value

        Returns:
            ProcessingResult containing MeasurementEvents and diagnostics.
        """
        form_id = form_response["form_id"]
        form_submission_id = form_response["form_submission_id"]
        subject_id = form_response["subject_id"]
        timestamp = form_response["timestamp"]
        responses = form_response.get("responses", {})

        # Initialize diagnostics collector
        collector = DiagnosticsCollector(
            form_submission_id=form_submission_id,
            form_id=form_id,
            binding_id=self.binding_spec.binding_id,
            binding_version=self.binding_spec.version,
        )

        events: list[MeasurementEvent] = []
        warnings: list[str] = []

        try:
            # 1. Map form items to instrument items
            mapping_result = self.mapper.map(
                form_response=form_response,
                binding_spec=self.binding_spec,
            )
            collector.collect_from_mapping(mapping_result)

            # 2. Recode values for each instrument section
            recoding_result = self.recoder.recode(
                mapping_result=mapping_result,
                instruments=self.instruments,
            )
            collector.collect_from_recoding(recoding_result)

            # 3. Process each instrument section
            for section in recoding_result.sections:
                instrument = self.instruments[section.instrument_id]

                # 3a. Validate
                validation_result = self.validator.validate(
                    section=section,
                    instrument=instrument,
                )
                collector.collect_from_validation(validation_result, section.instrument_id)

                # Set quality metrics
                collector.set_instrument_quality(
                    instrument_id=section.instrument_id,
                    items_total=len(instrument.items),
                    items_present=len([i for i in section.items if not i.missing]),
                    missing_items=validation_result.missing_items,
                    out_of_range_items=validation_result.out_of_range_items,
                    prorated_scales=[],  # Will be filled from scoring
                )

                # 3b. Score
                scoring_result = self.scoring_engine.score(
                    section=section,
                    instrument=instrument,
                )
                collector.collect_from_scoring(scoring_result)

                # Update prorated scales
                prorated = [s.scale_id for s in scoring_result.scales if s.prorated]
                if prorated:
                    collector.set_instrument_quality(
                        instrument_id=section.instrument_id,
                        items_total=len(instrument.items),
                        items_present=len([i for i in section.items if not i.missing]),
                        missing_items=validation_result.missing_items,
                        out_of_range_items=validation_result.out_of_range_items,
                        prorated_scales=prorated,
                    )

                # Collect warnings for prorated scores
                for scale in scoring_result.scales:
                    if scale.prorated:
                        warnings.append(
                            f"Scale {scale.scale_id} was prorated "
                            f"(missing: {scale.missing_items})"
                        )

                # 3c. Interpret
                interpretation_result = self.interpreter.interpret(
                    scoring_result=scoring_result,
                    instrument=instrument,
                )

                # 3d. Build MeasurementEvent
                event = self.builder.build(
                    recoded_section=section,
                    scoring_result=scoring_result,
                    interpretation_result=interpretation_result,
                    binding_spec=self.binding_spec,
                    form_id=form_id,
                    form_submission_id=form_submission_id,
                    subject_id=subject_id,
                    timestamp=timestamp,
                    warnings=warnings if warnings else None,
                )
                events.append(event)

        except Exception as e:
            collector.add_error(
                stage="building",
                code="PIPELINE_ERROR",
                message=str(e),
            )

        # Finalize diagnostics
        diagnostic = collector.finalize()

        return ProcessingResult(
            form_submission_id=form_submission_id,
            events=events,
            diagnostic=diagnostic,
            success=diagnostic.status.value == "success" or diagnostic.status.value == "partial",
        )

    def process_batch(
        self,
        form_responses: list[dict[str, Any]],
    ) -> list[ProcessingResult]:
        """Process a batch of form responses.

        Args:
            form_responses: List of canonical form response dicts.

        Returns:
            List of ProcessingResults for each form response.
        """
        results = []
        for form_response in form_responses:
            result = self.process(form_response)
            results.append(result)
        return results

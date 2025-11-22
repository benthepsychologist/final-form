"""
Command-line interface for final-form.
"""

import click
from pathlib import Path


@click.command()
@click.option(
    "--in",
    "input_file",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Input JSONL file with canonical form responses from canonizer",
)
@click.option(
    "--out",
    "output_file",
    type=click.Path(path_type=Path),
    required=True,
    help="Output JSONL file for scored responses",
)
@click.option(
    "--mapping",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Form mapping JSON file (maps platform IDs to canonical IDs)",
)
@click.option(
    "--questionnaire-registry",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Path to questionnaire-registry directory",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def main(
    input_file: Path,
    output_file: Path,
    mapping: Path,
    questionnaire_registry: Path,
    verbose: bool,
):
    """
    Semantic processing engine for mental health questionnaire responses.

    Transforms canonical JSON input from canonizer into fully scored,
    normalized, validated, research-ready output.

    Example:

        final-form run \\
          --in forms.jsonl \\
          --out scored.jsonl \\
          --mapping ~/questionnaire-registry/mappings/google_forms/mbc_initial_phq9_v1.json \\
          --questionnaire-registry ~/questionnaire-registry
    """
    if verbose:
        click.echo("final-form v0.1.0")
        click.echo(f"Input: {input_file}")
        click.echo(f"Output: {output_file}")
        click.echo(f"Mapping: {mapping}")
        click.echo(f"Registry: {questionnaire_registry}")

    # TODO: Implement pipeline orchestration in later steps
    # For now, just validate that we can load the registry and mapping

    from .registry import QuestionnaireRegistry, FormMappingLoader

    try:
        # Load questionnaire registry
        if verbose:
            click.echo("\nLoading questionnaire registry...")
        registry = QuestionnaireRegistry(questionnaire_registry)
        if verbose:
            click.echo(f"  Loaded {len(registry.list_measures())} measures")

        # Load form mapping
        if verbose:
            click.echo("\nLoading form mapping...")
        mapping_loader = FormMappingLoader(questionnaire_registry)
        form_mapping = mapping_loader.load_mapping(mapping)
        if verbose:
            click.echo(f"  Mapping: {form_mapping.form_metadata.form_name}")
            click.echo(f"  Platform: {form_mapping.form_metadata.form_platform}")
            click.echo(f"  Measure: {form_mapping.measure_id}")
            click.echo(f"  Items: {len(form_mapping.item_mappings)}")

        # Verify measure exists
        measure = registry.get_measure(form_mapping.measure_id)
        if not measure:
            raise ValueError(
                f"Measure '{form_mapping.measure_id}' not found in registry. "
                f"Available: {', '.join(registry.list_measures())}"
            )

        if verbose:
            click.echo(f"\n✓ Successfully loaded measure: {measure.name}")

        # TODO: Implement actual processing pipeline
        click.echo("\n⚠ Pipeline implementation pending (Steps 5-9)")
        click.echo("  Registry and mapping loaded successfully!")

    except Exception as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()

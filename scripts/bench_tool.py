#!/usr/bin/env python3
"""
Dynaconf benchmarking and profiling tool.

This tool provides benchmarking and profiling capabilities for Dynaconf scenarios.
Scenarios are auto-discovered from the scripts/scenarios/ directory.

Requirements (uv will resolve these from comments):
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pyinstrument>=4.0.0",
#     "dynaconf",
#     "click>=8.0.0",
# ]
# ///
"""

from __future__ import annotations

import importlib.util
import timeit
from pathlib import Path
from textwrap import dedent

import click

project_root = Path(__file__).parent.parent


def discover_scenarios():
    """
    Auto-discover scenario modules from scripts/scenarios/ directory.

    Returns:
        dict: Mapping of scenario names to loaded modules
    """
    scenarios = {}
    scenarios_dir = Path(__file__).parent / "scenarios"

    if not scenarios_dir.exists():
        return scenarios

    for scenario_file in scenarios_dir.glob("*.py"):
        if scenario_file.name.startswith("__"):
            continue

        try:
            # Validate that the module has required functions
            scenario_name, module = _load_scenario_module(scenario_file)
            if not hasattr(module, "setup"):
                click.echo(
                    f"Warning: Scenario {scenario_name} missing setup() function",
                    err=True,
                )
                raise click.Abort()
            if not hasattr(module, "run"):
                click.echo(
                    f"Warning: Scenario {scenario_name} missing run() function",
                    err=True,
                )
                raise click.Abort()
            scenarios[scenario_name] = module
        except Exception as e:
            click.echo(
                f"Warning: Failed to load scenario {scenario_name}: {e}",
                err=True,
            )
            continue

    return scenarios


def _load_scenario_module(scenario_file):
    scenario_name = scenario_file.stem
    spec = importlib.util.spec_from_file_location(scenario_name, scenario_file)
    if spec is None or spec.loader is None:
        click.echo(
            f"Warning: Could not load spec for {scenario_file}", err=True
        )
        raise click.Abort()
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return scenario_name, module


def _get_scenario_source_code(scenario_name):
    """Get the file path for a scenario by name."""
    scenarios_dir = Path(__file__).parent / "scenarios"
    scenario_file = scenarios_dir / f"{scenario_name}.py"
    if not scenario_file.exists():
        click.echo(f"Error: Could not find scenario file for '{scenario_name}'", err=True)
        raise click.Abort()
    with open(scenario_file) as f:
        scenario_source = f.read()

    setup_code = dedent(
        scenario_source +
        "context = setup()"
    )
    stmt_code = "run(context)"
    return dedent(setup_code), stmt_code



def create_scenario_runner(scenario_module):
    """
    Create a callable that sets up the scenario once and runs it.

    Args:
        scenario_module: The loaded scenario module

    Returns:
        callable: Function that runs the scenario
    """
    try:
        context = scenario_module.setup()
        return lambda: scenario_module.run(context)
    except Exception as e:
        click.echo(f"Error setting up scenario: {e}", err=True)
        raise click.Abort()


@click.group()
def cli():
    """Benchmark and profile access patterns for dynaconf data structures."""
    pass


@cli.command()
def list():
    """List available scenarios."""
    scenarios = discover_scenarios()

    if not scenarios:
        click.echo("No scenarios found in scripts/scenarios/")
        return

    for scenario_name in sorted(scenarios.keys()):
        module = scenarios[scenario_name]
        description = _get_docstring(module)
        if description:
            click.echo(f"{scenario_name}: {description}")
        else:
            click.echo(scenario_name)


def _get_docstring(module):
    if hasattr(module, "__doc__") and module.__doc__:
        # Get first line of docstring
        return module.__doc__.strip().split("\n")[0]
    return ""


@cli.command()
@click.option(
    "--label",
    required=False,
    default="default",
    help="Label identifier for this benchmark run",
)
@click.argument("scenario", required=True)
def run(label, scenario):
    """Run benchmark for a specific scenario."""
    scenarios = discover_scenarios()

    if scenario not in scenarios:
        err_msg = (
            f"Error: Scenario '{scenario}' not found. Available scenarios:"
        )
        for scenario_name in sorted(scenarios.keys()):
            err_msg += f"\n    {scenario_name}"
        click.echo(err_msg, err=True)
        raise click.Abort()

    try:
        setup_code, stmt_code = _get_scenario_source_code(scenario)
        result = timeit.timeit(stmt_code, setup=setup_code, number=1)

        # Output in TSV format: LABEL RESULT
        print(f"{label}\t{result}")  # noqa
    except Exception as e:
        click.echo(f"Error running scenario '{scenario}': {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("scenario", required=True)
@click.option(
    "--output",
    "-o",
    help="Output file for profiling results (optional, defaults to browser)",
)
def profile(scenario, output):
    """Profile a specific scenario using pyinstrument."""
    from pyinstrument import Profiler

    scenarios = discover_scenarios()

    if scenario not in scenarios:
        err_msg = (
            f"Error: Scenario '{scenario}' not found. Available scenarios:"
        )
        for scenario_name in sorted(scenarios.keys()):
            err_msg += f"\n    {scenario_name}"
        click.echo(err_msg, err=True)
        raise click.Abort()

    scenario_module = scenarios[scenario]

    try:
        click.echo(f"Profiling scenario: {scenario}")

        context = scenario_module.setup()
        profiler = Profiler()
        profiler.start()
        scenario_module.run(context)
        profiler.stop()

        # Output results
        if output:
            click.echo(f"Saving profile results to: {output}")
            output_path = Path(output)

            # Choose output format based on file extension
            if output_path.suffix.lower() == ".html":
                with open(output, "w") as f:
                    f.write(profiler.output_html())
            else:
                # Default to text format for other extensions
                with open(output, "w") as f:
                    f.write(profiler.output_text())
        else:
            click.echo("Opening profile results in browser...")
            profiler.open_in_browser()

    except Exception as e:
        click.echo(f"Error profiling scenario '{scenario}': {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    cli()

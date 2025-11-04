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
        # Validate that the module has required functions
        scenario_name, module = _load_scenario_module(scenario_file)
        for required_fn in ("setup", "run", "baseline_setup", "baseline_run"):
            if not hasattr(module, required_fn):
                _missing_function_err(scenario_name, required_fn)
                raise click.Abort()
        scenarios[scenario_name] = module
    return scenarios


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


@cli.command()
@click.option(
    "--label",
    required=False,
    default="default",
    help="Label identifier for this benchmark run",
)
@click.option(
    "--baseline",
    is_flag=True,
    help="Run the baseline version of the scenario (label will be set to 'baseline')",
)
@click.argument("scenario", required=True)
def run(label, baseline, scenario):
    """Run benchmark for a specific scenario."""
    # Validate that --label and --baseline are not used together
    if baseline and label != "default":
        click.echo("Error: Cannot use --label with --baseline flag", err=True)
        raise click.Abort()

    if baseline:
        label = "baseline"

    scenarios = discover_scenarios()
    _validate_scenarios(scenarios, scenario)
    try:
        setup_code, stmt_code = _get_scenario_source_code(
            scenario, use_baseline=baseline
        )
        result = timeit.timeit(stmt_code, setup=setup_code, number=1)
        _output_tsv(label, result)
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
    _validate_scenarios(scenarios, scenario)
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


def _missing_function_err(scenario_name, required_fn):
    click.echo(
        f"Warning: Scenario {scenario_name} missing {required_fn} function",
        err=True,
    )


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


def _get_scenario_source_code(scenario_name, use_baseline=False):
    """Get the source code for a scenario by name.

    Args:
        scenario_name: Name of the scenario
        use_baseline: If True, use baseline_setup() and baseline_run() instead of setup() and run()

    Returns:
        tuple: (setup_code, stmt_code) for timeit
    """
    scenarios_dir = Path(__file__).parent / "scenarios"
    scenario_file = scenarios_dir / f"{scenario_name}.py"
    if not scenario_file.exists():
        click.echo(
            f"Error: Could not find scenario file for '{scenario_name}'",
            err=True,
        )
        raise click.Abort()
    with open(scenario_file) as f:
        scenario_source = f.read()

    setup_fn = "baseline_setup" if use_baseline else "setup"
    run_fn = "baseline_run" if use_baseline else "run"
    setup_code = scenario_source + f"\ncontext = {setup_fn}()"
    stmt_code = f"{run_fn}(context)"

    return setup_code, stmt_code


def _get_docstring(module):
    if hasattr(module, "__doc__") and module.__doc__:
        # Get first line of docstring
        return module.__doc__.strip().split("\n")[0]
    return ""


def _validate_scenarios(scenarios, scenario):
    if scenario not in scenarios:
        err_msg = (
            f"Error: Scenario '{scenario}' not found. Available scenarios:"
        )
        for scenario_name in sorted(scenarios.keys()):
            err_msg += f"\n    {scenario_name}"
        click.echo(err_msg, err=True)
        raise click.Abort()


def _output_tsv(label, data):
    print(f"{label}\t{data}")  # noqa


if __name__ == "__main__":
    cli()

#!/usr/bin/env python3
from __future__ import annotations

import os
import timeit
from textwrap import dedent

from dynaconf.vendor import click

setup_code = """\
from dynaconf import Dynaconf
from dynaconf.utils.boxing import DynaBox
from dynaconf.nodes import DataDict

data = {"common": {"mode": 123}}
settings = Dynaconf(
    **data,
)
# dynabox = DynaBox(data)
# datadict = DataDict(data)
settings.common  # trigger setup
"""

scenarios = {
    "baseline": """\
        for i in range({repeats}):
            x = data["common"]["mode"]
        """,
    "dot_access": """\
        for i in range({repeats}):
            x = settings.common.mode
        """,
    "subs_access": """\
        for i in range({repeats}):
            x = settings["common"]["mode"]
        """,
    "subs_access_pure_dynabox": """\
        for i in range({repeats}):
            x = dynabox["common"]["mode"]
        """,
    "dot_access_pure_datadict": """\
        for i in range({repeats}):
            x = datadict.common.mode
        """,
    "subs_access_pure_datadict": """\
        for i in range({repeats}):
            x = datadict["common"]["mode"]
        """,
}


@click.group()
def cli():
    """Benchmark access patterns for dynaconf data structures."""
    pass


@cli.command()
def list():
    """List available scenarios."""
    for scenario_name in scenarios.keys():
        click.echo(scenario_name)


@cli.command()
@click.option(
    "--git-ref",
    required=False,
    default="default",
    help="Git reference identifier",
)
@click.argument("scenario", required=True)
def run(git_ref, scenario):
    """Run benchmark."""
    global scenarios

    if scenario not in scenarios:
        click.echo(
            f"Error: Scenario '{scenario}' not found. Available scenarios:"
        )
        for scenario_name in scenarios.keys():
            click.echo(f"  {scenario_name}")
        return

    scenario_code = scenarios[scenario]

    # Use a fixed repeat count for single measurement
    repeat_count = 100_000
    code = dedent(scenario_code).format(repeats=repeat_count)
    result = timeit.timeit(stmt=code, setup=setup_code, number=1)

    # Output in TSV format: GIT_REF RESULT
    print(f"{git_ref}\t{result}")


if __name__ == "__main__":
    cli()

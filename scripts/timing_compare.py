#!/usr/bin/env python3
from __future__ import annotations

import os
import timeit
from textwrap import dedent

import click

setup_code = """\
from dynaconf import Dynaconf
from dynaconf.utils.boxing import DynaBox
from dynaconf.nodes import DataDict

data = {"common": {"mode": 123}}
settings = Dynaconf(
    **data,
)
dynabox = DynaBox(data)
datadict = DataDict(data)
"""

scenarios = {
    "baseline": """\
        for i in range({repeats}):
            x = data["common"]["mode"]
        """,
    # "dot_access": """\
    #     for i in range({repeats}):
    #         x = settings.common.mode
    #     """,
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
    "--repeat-set",
    "-r",
    default="1,10,100,1000,5000,10000,50000,100000,250000,500000",
    help="Comma-separated list of repeat counts",
)
@click.option(
    "--include",
    "-i",
    help="Comma-separated list of scenarios to include (default: all)",
)
@click.option(
    "--output-dir", "-o", help="Output directory (default: current directory)"
)
def run(repeat_set, include, output_dir):
    """Run benchmark."""
    global scenarios

    repeat_list = [int(x.strip()) for x in repeat_set.split(",")]
    include_list = []
    if include:
        include_list = [x.strip() for x in include.split(",")]

    scenarios_items = scenarios.items()
    if include_list:
        scenarios_items = [
            (k, v) for k, v in scenarios_items if k in include_list
        ]

    for scenario_name, scenario_code in scenarios_items:
        print(scenario_name)  # noqa
        filename = scenario_name + ".dat"
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.join(output_dir, filename)
        with open(filename, "w") as fd:
            for repeat in repeat_list:
                code = dedent(scenario_code).format(repeats=repeat)
                result = timeit.timeit(stmt=code, setup=setup_code, number=1)
                display = f"{repeat} {result}"
                print(display, file=fd)
                print(display)  # noqa


if __name__ == "__main__":
    cli()

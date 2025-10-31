#!/usr/bin/env python3
#
# THIS SCRIPT IS GERETATED BY AI.
# Remove this comment if a human refactors it.
"""
Create box plots from TSV benchmark data.

Requirements (uv will resolve these from comments):
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pandas>=2.0.0",
#     "matplotlib>=3.5.0",
#     "seaborn>=0.12.0",
#     "click>=8.0.0",
# ]
# ///
"""

from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


@click.command()
@click.argument("tsv_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output PNG file path. Default: tmp-bench/plot-{scenario}.png",
)
@click.option(
    "--title", "-t", help="Plot title. Default: derived from filename"
)
@click.option(
    "--figsize",
    default="12,8",
    help="Figure size as 'width,height'. Default: 12,8",
)
def main(tsv_file: Path, output: Path, title: str, figsize: str):
    """Create a box plot from TSV benchmark data."""

    # Read the TSV file
    try:
        df = pd.read_csv(
            tsv_file, sep="\t", header=None, names=["git_ref", "timing"]
        )
    except Exception as e:
        click.echo(f"Error reading {tsv_file}: {e}", err=True)
        raise click.Abort()

    if df.empty:
        click.echo(f"No data found in {tsv_file}", err=True)
        raise click.Abort()

    # Extract baseline mean for reference line and remove from main data
    baseline_data = df[df["git_ref"] == "baseline"]
    baseline_mean = (
        baseline_data["timing"].mean() if not baseline_data.empty else None
    )

    # Remove baseline from the main dataframe for box plotting
    df_plot = df[df["git_ref"] != "baseline"].copy()

    # Determine output file if not provided
    if output is None:
        bench_dir = Path("tmp-bench")
        bench_dir.mkdir(exist_ok=True)
        stem = tsv_file.stem
        # Extract scenario name by removing "bench-" prefix
        scenario = (
            stem.replace("bench-", "") if stem.startswith("bench-") else stem
        )
        output = bench_dir / f"plot-{scenario}.png"

    # Determine title if not provided
    if title is None:
        title = f"Performance Benchmark: {scenario.replace('_', ' ').title()}"

    # Parse figure size
    try:
        width, height = map(float, figsize.split(","))
    except ValueError:
        click.echo(
            f"Invalid figsize format: {figsize}. Use 'width,height'", err=True
        )
        raise click.Abort()

    # Create the plot
    plt.figure(figsize=(width, height))

    # Set style for better-looking plots
    sns.set_style("whitegrid")
    sns.set_palette("husl")

    # Get unique git_refs and invert the order
    git_refs = df_plot["git_ref"].unique()
    git_refs_inverted = git_refs[::-1]

    # Create box plot with inverted order
    ax = sns.boxplot(
        data=df_plot, x="git_ref", y="timing", order=git_refs_inverted
    )

    # Add baseline reference line if baseline data exists
    if baseline_mean is not None:
        ax.axhline(
            y=baseline_mean,
            color="red",
            linestyle="--",
            alpha=0.7,
            linewidth=2,
            label=f"Baseline mean: {baseline_mean:.6f}s",
        )
        ax.legend()

    # Customize the plot
    plt.title(title, fontsize=16, fontweight="bold", pad=20)
    plt.xlabel("Git Reference", fontsize=12, fontweight="bold")
    plt.ylabel("Execution Time (seconds)", fontsize=12, fontweight="bold")

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha="right")

    # Add grid for better readability
    plt.grid(True, alpha=0.3)

    # Tight layout to prevent label cutoff
    plt.tight_layout()

    # Add summary statistics as text
    if not df_plot.empty:
        samples_range = f"{df_plot.groupby('git_ref').size().min()}-{df_plot.groupby('git_ref').size().max()}"
    else:
        samples_range = "0"
    stats_text = f"Samples per git ref: {samples_range}"
    if baseline_mean is not None:
        stats_text += f" | Baseline mean: {baseline_mean:.6f}s"
    plt.figtext(0.02, 0.02, stats_text, fontsize=8, style="italic")

    # Save the plot
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(
            output,
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
        )
        click.echo(f"Box plot saved to: {output}")
    except Exception as e:
        click.echo(f"Error saving plot to {output}: {e}", err=True)
        raise click.Abort()

    # Show basic statistics
    click.echo("\nSummary Statistics (excluding baseline):")
    if not df_plot.empty:
        summary = df_plot.groupby("git_ref")["timing"].agg(
            ["count", "mean", "std", "min", "max"]
        )

        # Reorder summary to chronological order (reversed from plot order)
        summary_ordered = summary.loc[git_refs_inverted[::-1]]

        # Add comparison columns - compare each commit to the chronologically previous one
        summary_ordered["vs_previous"] = summary_ordered[
            "mean"
        ] / summary_ordered["mean"].shift(-1)
        # Set the last factor to 1.0 (no next commit to compare to)
        summary_ordered.loc[summary_ordered.index[-1], "vs_previous"] = 1.0

        if baseline_mean is not None:
            summary_ordered["vs_baseline"] = (
                summary_ordered["mean"] / baseline_mean
            )

        # Round different columns to different precision
        summary_display = summary_ordered.round(6).copy()
        summary_display["vs_previous"] = summary_ordered["vs_previous"].round(
            1
        )
        if baseline_mean is not None:
            summary_display["vs_baseline"] = summary_ordered[
                "vs_baseline"
            ].round(1)

        # Format and display the table
        click.echo(summary_display.to_string())
    else:
        click.echo("No data to display (only baseline found)")

    if baseline_mean is not None:
        click.echo("\nBaseline Statistics:")
        baseline_stats = baseline_data["timing"].agg(
            ["count", "mean", "std", "min", "max"]
        )
        click.echo(
            f"baseline  {baseline_stats['count']:6.0f}  {baseline_stats['mean']:10.6f}  {baseline_stats['std']:10.6f}  {baseline_stats['min']:10.6f}  {baseline_stats['max']:10.6f}"
        )


if __name__ == "__main__":
    main()

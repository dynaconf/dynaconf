#!/bin/bash

set -euo pipefail

BENCH_SCRIPT="scripts/bench_tool.py"
TMPDIR="tmp-bench"
SAMPLE_N=5
DRY_RUN=false
SCENARIO=""
CUSTOM_GIT_REFS=()

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    -r)
      if [[ $# -lt 2 ]] || [[ "$2" =~ ^-.*$ ]]; then
        echo "Error: -r flag requires a numeric value"
        echo "Usage: $0 [--dry-run] [-r <sample_count>] <scenario> [git_ref1 git_ref2 ...]"
        exit 1
      fi
      SAMPLE_N="$2"
      # Validate that it's a number
      if ! [[ "$SAMPLE_N" =~ ^[0-9]+$ ]]; then
        echo "Error: -r value must be a positive integer"
        echo "Usage: $0 [--dry-run] [-r <sample_count>] <scenario> [git_ref1 git_ref2 ...]"
        exit 1
      fi
      shift 2
      ;;
    *)
      if [ -z "$SCENARIO" ]; then
        SCENARIO="$1"
        shift
      else
        # Check if this is a flag that came after scenario
        if [[ "$1" == --* ]] || [[ "$1" == -* ]]; then
          echo "Error: Unknown flag '$1' or flag must come before scenario"
          echo "Usage: $0 [--dry-run] [-r <sample_count>] <scenario> [git_ref1 git_ref2 ...]"
          exit 1
        fi
        # All remaining non-flag arguments are custom git refs
        CUSTOM_GIT_REFS+=("$1")
        shift
      fi
      ;;
  esac
done

if [ -z "$SCENARIO" ]; then
  echo "Error: scenario argument is required"
  echo "Usage: $0 [--dry-run] [-r <sample_count>] <scenario> [git_ref1 git_ref2 ...]"
  exit 1
fi

# Utility function
 
CURRENT_CHECKOUT_LOCATION="git+file://$PWD"

function bench(){
  OUTPUT_FILE=$1
  SCENARIO=$2
  GIT_REF=$3
  if [ "$GIT_REF" = "DIRTY" ]; then
    PKG_LOCATION="$CURRENT_CHECKOUT_LOCATION"
  else
    PKG_LOCATION="git+file://$PWD@$GIT_REF"
  fi
  echo "uv run --with $PKG_LOCATION $BENCH_SCRIPT run --label $GIT_REF $SCENARIO"
  uv run --with "$PKG_LOCATION" "$BENCH_SCRIPT" run --label "$GIT_REF" "$SCENARIO" 1>> "$OUTPUT_FILE"
}


function run_baseline(){
  OUTPUT_FILE=$1
  SCENARIO=$2
  PKG_LOCATION="git+file://$PWD"
  echo "uv run --with $PKG_LOCATION $BENCH_SCRIPT run --baseline $SCENARIO"
  uv run --with "$PKG_LOCATION" "$BENCH_SCRIPT" run --baseline "$SCENARIO" >> "$OUTPUT_FILE"
}

# Main 

# Use custom git refs if provided, otherwise use default behavior
if [ ${#CUSTOM_GIT_REFS[@]} -gt 0 ]; then
  GIT_REFS=("${CUSTOM_GIT_REFS[@]}")
else
  git fetch upstream
  BRANCH_COMMITS=($(git rev-list --abbrev-commit upstream/master..HEAD))
  LAST_TAG=$(git describe --tags --abbrev=0 HEAD 2>/dev/null || echo "")

  GIT_REFS=(
    "${BRANCH_COMMITS[@]}"
    # we assume upstream points ot dynaconf/dynaconf
    # full spec is required  in github actions environment
    "refs/remotes/upstream/master"
  )

  # Add last tag if it exists
  # if [ -n "$LAST_TAG" ]; then
  #   GIT_REFS+=("$LAST_TAG")
  # fi
fi

echo "Using scenario: ${SCENARIO}"
echo "Sample count: ${SAMPLE_N}"
echo "Using refs:"
echo "${GIT_REFS[@]}"
echo

# Exit if dry-run is enabled
if [ "$DRY_RUN" = true ]; then
  echo "Dry-run mode: exiting without running benchmarks"
  exit 0
fi

mkdir -p $TMPDIR

# Run benchmarks for all combinations
 
OUTPUT_FILE="$TMPDIR/bench-${SCENARIO}.tsv"
# baseline
for ((i=1; i<=SAMPLE_N; i++)); do
    run_baseline "$OUTPUT_FILE" "$SCENARIO"
done
# regular scenarios
for GIT_REF in "${GIT_REFS[@]}"; do
  echo "$SCENARIO $GIT_REF"
  for ((i=1; i<=SAMPLE_N; i++)); do
      bench "$OUTPUT_FILE" "$SCENARIO" "$GIT_REF" 
  done
done

# Generate plot and summary
echo -e "----------------------------------------------\n\n"
uv run scripts/plot.py "$OUTPUT_FILE"
echo -e "----------------------------------------------\n\n"

# Generate profile results
echo "Generating profile for scenario: $SCENARIO"
PROFILE_OUTPUT="$TMPDIR/profile-${SCENARIO}.html"
uv run --with "$CURRENT_CHECKOUT_LOCATION" scripts/bench_tool.py profile "$SCENARIO" -o "$PROFILE_OUTPUT"
echo "Profile results saved to: $PROFILE_OUTPUT"


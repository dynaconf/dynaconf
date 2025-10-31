#!/bin/bash

BENCH_SCRIPT="scripts/timing_compare.py"
TMPDIR="tmp-bench"
SAMPLE_N=1
SCENARIOS=(
  # "baseline"
  "subs_access"
  "dot_access"
  # "subs_access_pure_dynabox"
)

# Utility funciton
 
function bench(){
  OUTPUT_FILE=$1
  SCENARIO=$2
  GIT_REF=$3
  if [ "$GIT_REF" = "DIRTY" ]; then
    PKG_LOCATION="git+file://$PWD"
  else
    PKG_LOCATION="git+file://$PWD@$GIT_REF"
  fi
  echo "uv run --with $PKG_LOCATION $BENCH_SCRIPT run --git-ref $GIT_REF $SCENARIO"
  uv run --with "$PKG_LOCATION" "$BENCH_SCRIPT" run --git-ref "$GIT_REF" "$SCENARIO" >> "$OUTPUT_FILE"
}


function run_baseline(){
  OUTPUT_FILE=$1
  BASELINE="baseline"
  PKG_LOCATION="git+file://$PWD"
  echo "uv run --with $PKG_LOCATION $BENCH_SCRIPT run --git-ref $BASELINE $BASELINE"
  uv run --with "$PKG_LOCATION" "$BENCH_SCRIPT" run --git-ref "$BASELINE" "$BASELINE" >> "$OUTPUT_FILE"
}

# Main 

git fetch upstream
CURRENT_BRANCH=$(git branch --show-current)
BRANCH_COMMITS=($(git rev-list --abbrev-commit master..$CURRENT_BRANCH~1))
GIT_REFS=(
  "$CURRENT_BRANCH"
  "${BRANCH_COMMITS[@]}"
  "master"
  "3.2.12"
  "3.2.6"
  "3.2.0"
  "3.1.0"
  "3.0.0"
)

echo "Using scenarios:"
echo "${SCENARIOS[@]}"
echo "Using refs:"
echo "${GIT_REFS[@]}"
echo

rm -rf $TMPDIR
mkdir -p $TMPDIR

# Run benchmarks for all combinations
 
for SCENARIO in "${SCENARIOS[@]}"; do
  OUTPUT_FILE="$TMPDIR/bench-${SCENARIO}.tsv"
  # baseline
  for ((i=1; i<=SAMPLE_N; i++)); do
      run_baseline "$OUTPUT_FILE"
  done
  # regular scenarios
  for GIT_REF in "${GIT_REFS[@]}"; do
    echo "$SCENARIO $GIT_REF"
    for ((i=1; i<=SAMPLE_N; i++)); do
        bench "$OUTPUT_FILE" "$SCENARIO" "$GIT_REF" 
    done
  done
done



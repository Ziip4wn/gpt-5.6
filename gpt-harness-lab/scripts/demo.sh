#!/usr/bin/env sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir"

export PYTHONPATH="$project_dir/src${PYTHONPATH:+:$PYTHONPATH}"
python -m gpt_harness ask "Calcule 12 * (3 + 2)"
python -m gpt_harness eval scenarios/demo.json


#!/usr/bin/env bash
# Swap in the round-1 parser (faithful to spec-v1), run the v2 criteria against it, restore.
set -u
cd "$(dirname "$0")/.."
cp app/mesh.py /tmp/mesh-round2.py
cp demo/round-1/mesh.py app/mesh.py
echo "=== round-1 parser (from spec-v1), tested against the v2 acceptance criteria ==="
.venv/bin/python -m pytest tests/test_obj_support.py -q --no-header -o addopts="" 2>&1 | tail -16
cp /tmp/mesh-round2.py app/mesh.py
echo; echo "=== restored. round 2: ==="
.venv/bin/python -m pytest tests/test_obj_support.py -q --no-header -o addopts="" 2>&1 | tail -2

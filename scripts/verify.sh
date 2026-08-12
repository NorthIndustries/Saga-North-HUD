#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

WORK="${ROOT}/scripts/work"
MODULAR="${WORK}/Saga-North-HUD.conf"
GFN="${WORK}/Saga-North-HUD-GFN.conf"
BUNDLED='require('\''autoconf/custom/saganorth/custom/mydu_atlas'\'')'

rm -rf "$WORK"
mkdir -p "$WORK"

echo "Checking source and atlas..."
test -f source/Saga_AP_release.json
test -f atlas/mydu_atlas.lua
grep -q 'return {' atlas/mydu_atlas.lua

echo "Checking modular patch..."
python3 scripts/patch_saga.py --output "$MODULAR"
head -n 1 "$MODULAR" | grep -q '^name: '
grep -q 'class: CoreUnit' "$MODULAR"
grep -q 's1:' "$MODULAR"
grep -q 'class: ScreenUnit' "$MODULAR"
grep -q 'class: ForceFieldUnit' "$MODULAR"
grep -q "$BUNDLED" "$MODULAR"
grep -q 'slot1=s1' "$MODULAR"
if grep -q 'slot1:' "$MODULAR"; then
  echo "ERROR: slot1: must not appear in slots (reserved autoconf name)" >&2
  exit 1
fi
if grep -q "require('atlas')" "$MODULAR"; then
  echo "ERROR: modular conf still requires global atlas" >&2
  exit 1
fi
python3 <<'PY'
import re
from pathlib import Path
text = Path("scripts/work/Saga-North-HUD.conf").read_text()
for token in ["    core:", "    s1:", "    s14:", "    s21:", "    unit:", "    system:", "    library:"]:
    assert token in text, token
lib = re.search(r"    library:(.*?)(?=\n\S|\Z)", text, re.S)
assert lib and len(re.findall(r"^\s+onStart:\s*$", lib.group(1), re.M)) == 3, "expected 3 library onStart handlers"
unit = re.search(r"    unit:(.*?)(?=\n    system:)", text, re.S)
assert unit and len(re.findall(r"^\s+onStart:\s*$", unit.group(1), re.M)) == 2, "expected 2 unit onStart handlers"
print("YAML structure OK")
PY

echo "Checking inline patch..."
python3 scripts/patch_saga.py --inline --output "$GFN"
grep -q 'bW={' "$GFN"
if grep -q 'mydu_atlas' "$GFN"; then
  echo "ERROR: GFN conf still references mydu_atlas require" >&2
  exit 1
fi
if grep -q "require('atlas')" "$GFN"; then
  echo "ERROR: GFN conf still requires global atlas" >&2
  exit 1
fi

echo "Checking build scripts..."
test -x scripts/build.sh
test -f scripts/patch_saga.py

echo "All static checks passed."

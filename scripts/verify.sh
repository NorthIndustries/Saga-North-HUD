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
grep -q "$BUNDLED" "$MODULAR"
if grep -q "require('atlas')" "$MODULAR"; then
  echo "ERROR: modular conf still requires global atlas" >&2
  exit 1
fi
python3 <<'PY'
import json, sys
from pathlib import Path
data = json.loads(Path("scripts/work/Saga-North-HUD.conf").read_text())
slots = data["slots"]
assert slots["-5"]["name"] == "library", slots
assert slots["-4"]["name"] == "system", slots
assert slots["-3"]["name"] == "player", slots
assert slots["-2"]["name"] == "construct", slots
assert "-3" not in {h["filter"]["slotKey"] for h in data["handlers"]}
assert "-2" not in {h["filter"]["slotKey"] for h in data["handlers"]}
print("Slot key normalization OK")
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

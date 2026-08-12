#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

rm -rf deploy
mkdir -p deploy/autoconf/custom/saganorth/custom

python3 scripts/patch_saga.py --output Saga-North-HUD.conf
cp Saga-North-HUD.conf deploy/
cp atlas/mydu_atlas.lua deploy/autoconf/custom/saganorth/custom/

(
  cd deploy
  zip -r ../Saga-North-HUD.zip .
)

python3 scripts/patch_saga.py --inline --output Saga-North-HUD-GFN.conf

echo "Build complete:"
ls -lh Saga-North-HUD.conf Saga-North-HUD-GFN.conf Saga-North-HUD.zip

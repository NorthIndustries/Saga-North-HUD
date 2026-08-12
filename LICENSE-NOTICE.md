# License and attribution notice

## Original Saga AP HUD

The minified autoconf in `source/Saga_AP_release.json` is derived from a **Saga AP HUD** community release. In-code credit:

> HUD/Autopilot by Sagacious, Mayumi and CodeInsight

North Industries does **not** claim ownership of the Saga HUD logic, UI, or autopilot behavior. The upstream license for that release is **unknown**; only the minified JSON autoconf was provided for patching.

## This repository

This repo contains **only**:

- A patch that replaces `require('atlas')` with bundled MyDU planet data
- `atlas/mydu_atlas.lua` — North Industries MyDU server planet data (from `Game/data/lua/atlas.lua`)
- Build scripts and install documentation

The original Saga credit string in the patched conf is preserved.

## Planet data (`mydu_atlas.lua`)

Planet names, positions, and metadata reflect the North Industries MyDU server configuration. Update this file when the server atlas changes.

## Distribution

If you redistribute patched builds, keep this notice and the in-conf Saga author credit intact.

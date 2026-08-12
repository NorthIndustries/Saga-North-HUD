# Saga North HUD

MyDU fork of the **Saga AP HUD** with **bundled server planet data** (`mydu_atlas.lua`). Players do not need to replace the global `Game/data/lua/atlas.lua`.

Original HUD credit (from in-conf string): **Sagacious, Mayumi, CodeInsight**.

## Downloads

From [GitHub Releases](https://github.com/NorthIndustries/Saga-North-HUD/releases):

| Artifact | Use when |
|----------|----------|
| **Saga-North-HUD.zip** | Normal install (recommended) |
| **Saga-North-HUD.conf** | Modular conf only (you still need `mydu_atlas.lua` from the zip) |
| **Saga-North-HUD-GFN.conf** | Atlas embedded in the conf; no separate atlas file |

See [INSTALL.md](INSTALL.md) for player setup.

## What changed

The minified Saga release calls `require('atlas')` once in its startup handler. This repo patches that to:

```lua
require('autoconf/custom/saganorth/custom/mydu_atlas')
```

The GFN variant inlines the atlas table directly into the conf (~280–300 KB total).

Planet data comes from North Industries MyDU `atlas.lua`. See [LICENSE-NOTICE.md](LICENSE-NOTICE.md).

## Building

Requirements: `python3`, `zip`.

```bash
chmod +x scripts/*.sh
./scripts/verify.sh
./scripts/build.sh
```

Outputs: `Saga-North-HUD.conf`, `Saga-North-HUD.zip`, `Saga-North-HUD-GFN.conf`.

## Updating planet data

1. Copy the current MyDU client `Game/data/lua/atlas.lua` into `atlas/mydu_atlas.lua` (keep the header comment).
2. Run `./scripts/build.sh`.
3. Tag and push to `master` — CI publishes a GitHub Release.

## Help

North Industries: [mydu.north-industries.com](https://mydu.north-industries.com)

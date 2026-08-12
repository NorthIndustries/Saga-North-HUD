# Saga North HUD install (North Industries)

Saga AP HUD fork with **bundled server planet data** (`mydu_atlas.lua`). You do **not** need to replace the global `Game/data/lua/atlas.lua` for this HUD.

## Downloads

From [GitHub Releases](https://github.com/NorthIndustries/Saga-North-HUD/releases):

| Artifact | Use when |
|----------|----------|
| **Saga-North-HUD.zip** | Normal install (recommended) |
| **Saga-North-HUD.conf** | Modular conf only (you still need the atlas file from the zip) |
| **Saga-North-HUD-GFN.conf** | Single-file install; atlas embedded in the conf |

## Modular install (recommended)

1. Download **Saga-North-HUD.zip** from Releases.
2. Extract into your MyDU client folder:

   ```
   MyDU/Game/data/lua/autoconf/custom/
   ```

   You should have:

   - `Saga-North-HUD.conf`
   - `autoconf/custom/saganorth/custom/mydu_atlas.lua`

3. In game, on your pilot seat / control unit, apply autoconf profile **Saga North HUD** (filename `Saga-North-HUD.conf`).
4. Link elements per the usual Saga HUD setup (slots `slot1` … `slot21`).

Keep your vanilla `atlas.lua` unchanged; other HUDs may still depend on it.

## GFN-style install (atlas in conf)

1. Download **Saga-North-HUD-GFN.conf** → `MyDU/Game/data/lua/autoconf/custom/`
2. Apply **Saga North HUD** in game (atlas is embedded; no separate atlas file).

This variant is suitable when you cannot drop extra `.lua` files beside the conf (e.g. GeForce Now–style workflows).

## Planet icons

`iconPath` values in `mydu_atlas.lua` point at client PNGs under `gui/screen_unit/img/planets/`. Custom bodies need those assets on the client, or reuse existing vanilla icon paths.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Wrong planet names / autopilot targets vanilla bodies | Reinstall from **Saga-North-HUD.zip**; ensure `mydu_atlas.lua` is present |
| `no file '…lua' in the lua folder` | Extract the full zip so `autoconf/custom/saganorth/custom/mydu_atlas.lua` exists |
| `=> -3: missing 'class' description` | Old release with legacy slot keys — rebuild from latest repo |
| `=> 0: missing 'class' description` | Old release without core slot at index 0 — rebuild from latest repo |
| HUD works but map icons wrong | Add missing planet PNGs or fix `iconPath` in atlas |

## Help

North Industries: [mydu.north-industries.com](https://mydu.north-industries.com)

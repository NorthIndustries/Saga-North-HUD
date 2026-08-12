#!/usr/bin/env python3
"""Patch Saga AP release JSON to bundle MyDU atlas (modular or inlined)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "source" / "Saga_AP_release.json"
ATLAS = ROOT / "atlas" / "mydu_atlas.lua"
BUNDLED_REQUIRE = "autoconf/custom/saganorth/custom/mydu_atlas"
ATLAS_REQUIRE = "require('atlas')"
ASSIGNMENT = f"bW={ATLAS_REQUIRE}"
VERSION_RE = re.compile(r'Q="([0-9.]+)"')
EMPTY_SLOT_TYPE = {"methods": [], "events": []}
# Saga export uses legacy keys (-3=library, -2=system). MyDU expects -5/-4/-3/-2/-1.
HANDLER_SLOT_KEY_REMAP = {"-3": "-5", "-2": "-4"}


def atlas_table_literal() -> str:
    lines = ATLAS.read_text(encoding="utf-8").splitlines()
    while lines and (not lines[0].strip() or lines[0].lstrip().startswith("--")):
        lines.pop(0)
    body = "\n".join(lines).strip()
    if body.startswith("return"):
        body = body[len("return") :].strip()
    if not body.startswith("{"):
        raise SystemExit(f"Expected atlas module to return a table literal in {ATLAS}")
    return body


def display_name(version: str) -> str:
    return f"Saga North HUD v{version} (North Industries)"


def normalize_slot_keys(data: dict) -> None:
    """Remap legacy Saga slot keys to current MyDU JSON autoconf layout."""
    slots = data.get("slots", {})
    if slots.get("-5", {}).get("name") == "library":
        return

    legacy_library = slots.get("-3")
    legacy_system = slots.get("-2")
    unit = slots.get("-1")
    if legacy_library is None or legacy_system is None or unit is None:
        raise SystemExit("Expected legacy Saga slots -3 (library), -2 (system), -1 (unit)")

    element_slots = {key: value for key, value in slots.items() if not str(key).startswith("-")}
    data["slots"] = {
        **element_slots,
        "-5": legacy_library,
        "-4": legacy_system,
        "-3": {"name": "player", "type": dict(EMPTY_SLOT_TYPE)},
        "-2": {"name": "construct", "type": dict(EMPTY_SLOT_TYPE)},
        "-1": unit,
    }

    for handler in data.get("handlers", []):
        slot_key = handler.get("filter", {}).get("slotKey")
        if slot_key in HANDLER_SLOT_KEY_REMAP:
            handler["filter"]["slotKey"] = HANDLER_SLOT_KEY_REMAP[slot_key]


def patch_source(inline: bool) -> dict:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    version = "0.1.2"
    for handler in data.get("handlers", []):
        match = VERSION_RE.search(handler.get("code", ""))
        if match:
            version = match.group(1)
            break

    data["name"] = display_name(version)
    hits = 0
    bundled_require = f"require('{BUNDLED_REQUIRE}')"

    for handler in data.get("handlers", []):
        code = handler.get("code", "")
        if ATLAS_REQUIRE not in code:
            continue
        hits += 1
        if inline:
            handler["code"] = code.replace(ASSIGNMENT, f"bW={atlas_table_literal()}", 1)
        else:
            handler["code"] = code.replace(ATLAS_REQUIRE, bundled_require, 1)

    if hits != 1:
        raise SystemExit(f"Expected exactly 1 atlas require, found {hits}")

    normalize_slot_keys(data)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inline", action="store_true", help="Inline atlas table into handler code")
    parser.add_argument("--output", required=True, type=Path, help="Output .conf path")
    args = parser.parse_args()

    if not SOURCE.is_file():
        raise SystemExit(f"Missing source file: {SOURCE}")
    if not ATLAS.is_file():
        raise SystemExit(f"Missing atlas file: {ATLAS}")

    data = patch_source(inline=args.inline)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {args.output} ({args.output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

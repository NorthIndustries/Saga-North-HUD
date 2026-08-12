#!/usr/bin/env python3
"""Patch Saga AP release and emit MyDU YAML autoconf with bundled atlas."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "source" / "Saga_AP_release.json"
ATLAS = ROOT / "atlas" / "mydu_atlas.lua"
BUNDLED_REQUIRE = "autoconf/custom/saganorth/custom/mydu_atlas"
ATLAS_REQUIRE = "require('atlas')"
ASSIGNMENT = f"bW={ATLAS_REQUIRE}"
VERSION_RE = re.compile(r'Q="([0-9.]+)"')
EMPTY_SLOT_TYPE = {"methods": [], "events": []}
HANDLER_SLOT_KEY_REMAP = {"-3": "-5", "-2": "-4"}
HANDLER_SLOTS = {"-5": "library", "-4": "system", "-1": "unit"}
FORCEFIELD_SLOTS = {"slot14", "slot21"}


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


def element_slot_names(data: dict) -> list[str]:
    items = sorted(
        (int(key), value["name"])
        for key, value in data["slots"].items()
        if key.lstrip("-").isdigit() and int(key) >= 0
    )
    names = [name for _, name in items if name != "core"]
    ordered = ["core", *names]
    if "slot14" not in ordered:
        rebuilt: list[str] = []
        for name in ordered:
            rebuilt.append(name)
            if name == "slot11":
                rebuilt.append("slot14")
        ordered = rebuilt
    return ordered


def slot_class(name: str) -> tuple[str, str | None]:
    if name == "core":
        return "CoreUnit", None
    if name in FORCEFIELD_SLOTS:
        return "ForceFieldUnit", "manual"
    return "ScreenUnit", "manual"


def parse_signature(signature: str) -> tuple[str, list[str]]:
    match = re.match(r"([^(]+)\((.*)\)", signature)
    if not match:
        return signature, []
    params = [part.strip() for part in match.group(2).split(",") if part.strip()]
    return match.group(1), params


def yaml_arg(value: str) -> str:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        return value
    return f"'{value}'"


def emit_lua_block(lines: list[str], indent: int, code: str) -> None:
    pad = " " * indent
    pad_code = " " * (indent + 2)
    lines.append(f"{pad}lua: |")
    if code:
        for line in code.splitlines():
            lines.append(f"{pad_code}{line}")
    else:
        lines.append(pad_code)


def handler_yaml_key(filter_obj: dict) -> tuple[str, list[str] | None]:
    signature = filter_obj["signature"]
    args = filter_obj.get("args", [])
    if any(arg.get("variable") == "*" for arg in args):
        return signature, None

    event_name, param_names = parse_signature(signature)
    if not args:
        return event_name, None

    yaml_args: list[str] = []
    for index, arg in enumerate(args):
        if "value" in arg:
            yaml_args.append(arg["value"])
        elif "variable" in arg:
            yaml_args.append(param_names[index] if index < len(param_names) else "arg")
    return event_name, yaml_args


def emit_handlers(lines: list[str], handlers: list[dict], indent: int) -> None:
    pad = " " * indent
    pad2 = " " * (indent + 2)
    index = 0
    while index < len(handlers):
        handler = handlers[index]
        filt = handler["filter"]
        signature = filt["signature"]
        args = filt.get("args", [])

        if signature in ("onStart()", "onStop()") and not args:
            chunks = [handler["code"]]
            next_index = index + 1
            while (
                next_index < len(handlers)
                and handlers[next_index]["filter"]["signature"] == signature
                and not handlers[next_index]["filter"].get("args")
            ):
                chunks.append(handlers[next_index]["code"])
                next_index += 1
            event_name = signature[:-2]
            lines.append(f"{pad}{event_name}:")
            emit_lua_block(lines, indent + 2, "\n".join(chunks))
            index = next_index
            continue

        event_name, yaml_args = handler_yaml_key(filt)
        lines.append(f"{pad}{event_name}:")
        if yaml_args:
            rendered = ", ".join(yaml_arg(value) for value in yaml_args)
            lines.append(f"{pad2}args: [{rendered}]")
        emit_lua_block(lines, indent + 2, handler["code"])
        index += 1


def to_yaml(data: dict, name: str) -> str:
    lines = [f"name: {name}", "", "slots:"]
    for slot_name in element_slot_names(data):
        class_name, select_mode = slot_class(slot_name)
        lines.append(f"  {slot_name}:")
        lines.append(f"    class: {class_name}")
        if select_mode:
            lines.append(f"    select: {select_mode}")

    lines.append("")
    lines.append("handlers:")
    grouped: dict[str, list[dict]] = {slot: [] for slot in HANDLER_SLOTS.values()}
    for handler in sorted(
        data.get("handlers", []),
        key=lambda item: (item["filter"]["slotKey"], int(item["key"])),
    ):
        slot_key = handler["filter"]["slotKey"]
        slot_name = HANDLER_SLOTS.get(slot_key)
        if slot_name:
            grouped[slot_name].append(handler)

    for slot_name in ("library", "unit", "system"):
        slot_handlers = grouped[slot_name]
        if not slot_handlers:
            continue
        lines.append(f"  {slot_name}:")
        emit_handlers(lines, slot_handlers, indent=4)

    return "\n".join(lines) + "\n"


def patch_source(inline: bool) -> tuple[dict, str]:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    version = "0.1.2"
    for handler in data.get("handlers", []):
        match = VERSION_RE.search(handler.get("code", ""))
        if match:
            version = match.group(1)
            break

    name = display_name(version)
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
    return data, name


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inline", action="store_true", help="Inline atlas table into handler code")
    parser.add_argument("--output", required=True, type=Path, help="Output .conf path")
    args = parser.parse_args()

    if not SOURCE.is_file():
        raise SystemExit(f"Missing source file: {SOURCE}")
    if not ATLAS.is_file():
        raise SystemExit(f"Missing atlas file: {ATLAS}")

    data, name = patch_source(inline=args.inline)
    output = to_yaml(data, name)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(f"Wrote {args.output} ({args.output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

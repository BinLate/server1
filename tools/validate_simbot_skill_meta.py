# -*- coding: utf-8 -*-
"""Dev-time validator for SimBot FACTION_SKILLS combat metadata + user canonical matrix."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "script/global/nobitaxd/vdk/simcity/components/sim.skill_meta.lua"
PROG = ROOT / "script/global/nobitaxd/vdk/simcity/components/sim.progression.lua"
CORE = ROOT / "script/global/nobitaxd/vdk/simcity/components/sim.core.lua"
HORSE = ROOT / "script/global/nobitaxd/vdk/simcity/components/sim.horse_skills.lua"
PLUYEN = ROOT / "script/global/nobitaxd/vdk/simcity/plugins/pluyencong.lua"

sys.path.insert(0, str(ROOT / "tools"))
from gen_skill_meta import USER_CANONICAL_9X  # noqa: E402


def parse_meta(text: str):
    out = {}
    for m in re.finditer(r"\[(\d+)\]=\{([^}]+)\}", text):
        sid = int(m.group(1))
        body = m.group(2)
        out[sid] = {
            "horse": int(re.search(r"horse=(\d+)", body).group(1)),
            "ar": int(re.search(r"ar=(\d+)", body).group(1)),
            "tiles": int(re.search(r"tiles=(\d+)", body).group(1)),
            "melee": int(re.search(r"melee=(\d+)", body).group(1)),
            "typ": int(re.search(r"typ=(\d+)", body).group(1)),
        }
    return out


def faction_skill_ids(text: str):
    ids = set()
    m = re.search(r"SimProgression\.FACTION_SKILLS\s*=\s*\{", text)
    if not m:
        return ids
    depth = 1
    i = m.end()
    while i < len(text) and depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    body = text[m.end() : i - 1]
    for em in re.finditer(r"id\s*=\s*(\d+)", body):
        ids.add(int(em.group(1)))
    return ids


def main() -> int:
    meta = parse_meta(META.read_text(encoding="ascii", errors="replace"))
    prog = PROG.read_text(encoding="utf-8", errors="replace")
    core = CORE.read_text(encoding="utf-8", errors="replace")
    horse = HORSE.read_text(encoding="utf-8", errors="replace")
    pluyen = PLUYEN.read_text(encoding="utf-8", errors="replace")
    ids = faction_skill_ids(prog)
    errors = []
    warns = []

    if "SIMBOT_DISMOUNT_SKILLS = nil" not in core:
        errors.append("SIMBOT_DISMOUNT_SKILLS not cleared")
    if "SIMBOT_SKILL_RANGE = nil" not in core:
        errors.append("SIMBOT_SKILL_RANGE not cleared")
    if "HORSE_SKILLS = {}" not in horse:
        warns.append("HORSE_SKILLS should be empty stub")
    if "random(1, 3)" not in pluyen:
        errors.append("train spawn must assign peaceful camp via random(1, 3)")
    if re.search(r"local camp = \(isDoSat == 1 and 5\) or 0", pluyen):
        errors.append("train spawn still uses camp 0 for peaceful bots")

    for sid in sorted(ids):
        m = meta.get(sid)
        if not m:
            errors.append(f"FACTION_SKILLS id {sid} missing metadata")
            continue
        if m["typ"] == 2 and m["horse"] == 1:
            errors.append(f"{sid}: trap marked horse-allowed")
        if m["typ"] == 3 and m["horse"] == 1:
            errors.append(f"{sid}: support marked horse-allowed")

    for sid, (wh, wnear) in USER_CANONICAL_9X.items():
        m = meta.get(sid)
        if not m:
            errors.append(f"canonical id {sid} missing")
            continue
        if m["horse"] != wh:
            errors.append(f"canonical horse mismatch {sid}: want {wh} got {m['horse']}")
        near = 1 if (m["melee"] == 1 or m["typ"] == 2 or m["ar"] <= 120) else 0
        if near != wnear:
            errors.append(
                f"canonical range mismatch {sid}: want near={wnear} got near={near} ar={m['ar']} melee={m['melee']}"
            )

    print(f"checked {len(ids)} FACTION_SKILLS ids, {len(USER_CANONICAL_9X)} canonical 9x")
    for w in warns:
        print("WARN:", w)
    for e in errors:
        print("ERROR:", e)
    if errors:
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

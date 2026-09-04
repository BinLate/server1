# -*- coding: utf-8 -*-
"""
Generate SimSkillMeta from settings/skills.txt with STRICT horse ALLOWLIST.

Policy:
  - AttackRadius: always from skills.txt (AR=0 -> 64px engine basic failsafe)
  - horseAllowed: DEFAULT DENY (0). Set to 1 ONLY if skillId is in
    VERIFIED_HORSE_ALLOWLIST AND HorseLimit==0 in skills.txt.
  - HL>=1 never mounts, even if listed (safety).
  - Tile distance: ceil(px/32) so 90px -> 3 tiles (not floored to 2).

Also writes the FACTION_SKILLS combat audit report.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_TXT = ROOT / "settings" / "skills.txt"
PROGRESSION = (
    ROOT
    / "script"
    / "global"
    / "nobitaxd"
    / "vdk"
    / "simcity"
    / "components"
    / "sim.progression.lua"
)
OUT_LUA = (
    ROOT
    / "script"
    / "global"
    / "nobitaxd"
    / "vdk"
    / "simcity"
    / "components"
    / "sim.skill_meta.lua"
)
OUT_REPORT = (
    ROOT
    / "plans"
    / "260904-ai-bot-simulated-player"
    / "reports"
    / "faction-skills-combat-meta.md"
)

# Positively verified mounted combat skill IDs (ALLOWLIST).
# Evidence: user matrix §14 + skills.txt HorseLimit==0 confirmation.
# 150 upgrades with HL>=1 are intentionally EXCLUDED (default deny).
VERIFIED_HORSE_ALLOWLIST = {
    # Thieu Lam Dao — Vo Tuong Tram line
    321,
    1057,
    13,  # Lap Dia Thanh Phat (HL=0, dao branch ranged)
    # Thien Vuong Dao — Pha Thien Tram line (1059 HL=1 excluded)
    322,
    32,  # Vo Dich / Vo Tam Tram HL=0 melee mounted
    # Duong Mon Tu Tien (amkhi) — Bao Vu Le Hoa (1069 HL=1 excluded)
    302,
    # Ngu Doc Dao — Huyen Am Tram line
    355,
    1067,
    74,
    64,
    # Thien Nhan Van Long (repo branch key "dao"; skill ID is authority)
    # 1076 HL=1 excluded
    361,
}

# Trap / placement skills (not projectile target-cast)
TRAP_SKILLS = {351, 59, 52, 1071}

# Active support / heal / aura / debuff — never inherit "mounted" from branch
SUPPORT_SKILLS = {
    69,
    79,
    89,
    92,
    252,
    332,
    390,
    391,
    394,
    1114,
    176,
    171,
    179,
    139,
    140,
    66,
    65,
}


def ceil_tiles(ar_px: int) -> int:
    if ar_px <= 0:
        return 2
    return max(1, (ar_px + 31) // 32)


def range_class(ar_px: int) -> str:
    if ar_px <= 0:
        return "unknown"
    if ar_px <= 120:
        return "melee"
    if ar_px <= 256:
        return "short"
    if ar_px <= 384:
        return "mid"
    return "long"


def skill_type(sid: int, ar_px: int, is_melee: int) -> str:
    if sid in TRAP_SKILLS:
        return "trap"
    if sid in SUPPORT_SKILLS:
        return "support"
    if is_melee == 1 or (ar_px > 0 and ar_px <= 120):
        return "melee"
    if ar_px <= 0:
        return "attack"
    return "ranged"


def load_skills():
    by_id = {}
    with open(SKILLS_TXT, encoding="latin1", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            try:
                sid = int(row["SkillId"])
            except Exception:
                continue
            try:
                hl = int(row.get("HorseLimit") or 0)
            except Exception:
                hl = 0
            try:
                ar = int(row.get("AttackRadius") or 0)
            except Exception:
                ar = 0
            try:
                melee = int(row.get("IsMelee") or 0)
            except Exception:
                melee = 0
            try:
                t_horse = int(row.get("TimePerCastOnHorse") or 0)
            except Exception:
                t_horse = 0
            name = (row.get("SkillName") or "").strip()
            by_id[sid] = {
                "name": name,
                "hl": hl,
                "ar": ar,
                "melee": melee,
                "t_horse": t_horse,
            }
    return by_id


def decide_horse(sid: int, hl: int, stype: str) -> tuple[int, str]:
    """Return (horseAllowed, evidence). DEFAULT DENY."""
    if stype in ("trap", "support"):
        return 0, "default-deny: trap/support"
    if sid not in VERIFIED_HORSE_ALLOWLIST:
        return 0, "default-deny: not in verified allowlist"
    if hl != 0:
        return 0, "default-deny: HorseLimit!=0 blocks allowlist"
    return 1, "allowlist+HorseLimit=0"


def parse_faction_skills(lua_text: str):
    """Parse FACTION_SKILLS entries: fac -> branch -> list of {reqLv,id}."""
    # Find table body
    m = re.search(
        r"SimProgression\.FACTION_SKILLS\s*=\s*\{", lua_text
    )
    if not m:
        raise SystemExit("FACTION_SKILLS not found")
    start = m.end()
    # naive brace scan
    depth = 1
    i = start
    while i < len(lua_text) and depth:
        c = lua_text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        i += 1
    body = lua_text[start : i - 1]

    fac_pat = re.compile(
        r"(\w+)\s*=\s*\{",
    )
    entry_pat = re.compile(
        r"\{\s*reqLv\s*=\s*(\d+)\s*,\s*id\s*=\s*(\d+)\s*\}"
    )

    result = {}
    # Split by top-level faction keys roughly via regex positions
    # Re-parse with nested approach
    pos = 0
    while True:
        fm = re.search(r"(\w+)\s*=\s*\{", body[pos:])
        if not fm:
            break
        fac = fm.group(1)
        if fac in ("reqLv",):
            pos += fm.end()
            continue
        abs_start = pos + fm.end()
        depth = 1
        j = abs_start
        while j < len(body) and depth:
            if body[j] == "{":
                depth += 1
            elif body[j] == "}":
                depth -= 1
            j += 1
        fac_body = body[abs_start : j - 1]
        pos = j

        # Only treat known faction names (skip branch-level false positives later)
        # Detect if fac_body contains branch = { with reqLv entries
        branches = {}
        bpos = 0
        while True:
            bm = re.search(r"(\w+)\s*=\s*\{", fac_body[bpos:])
            if not bm:
                break
            branch = bm.group(1)
            b_abs = bpos + bm.end()
            depth = 1
            k = b_abs
            while k < len(fac_body) and depth:
                if fac_body[k] == "{":
                    depth += 1
                elif fac_body[k] == "}":
                    depth -= 1
                k += 1
            branch_body = fac_body[b_abs : k - 1]
            bpos = k
            entries = [
                {"reqLv": int(a), "id": int(b)}
                for a, b in entry_pat.findall(branch_body)
            ]
            if entries:
                branches[branch] = entries
        if branches:
            result[fac] = branches
    return result


def main():
    skills = load_skills()
    prog = PROGRESSION.read_text(encoding="utf-8", errors="replace")
    factions = parse_faction_skills(prog)

    # Collect SKILL_ATTACK_RADIUS discrepancies for report
    rad_map = {}
    for m in re.finditer(r"\[(\d+)\]\s*=\s*(\d+)", prog):
        # only inside SKILL_ATTACK_RADIUS section roughly — take all then filter
        rad_map[int(m.group(1))] = int(m.group(2))
    # Better: slice SKILL_ATTACK_RADIUS
    sm = re.search(r"SimProgression\.SKILL_ATTACK_RADIUS\s*=\s*\{", prog)
    lua_radius = {}
    if sm:
        depth = 1
        i = sm.end()
        while i < len(prog) and depth:
            if prog[i] == "{":
                depth += 1
            elif prog[i] == "}":
                depth -= 1
            i += 1
        block = prog[sm.end() : i - 1]
        for m in re.finditer(r"\[(\d+)\]\s*=\s*(\d+)", block):
            lua_radius[int(m.group(1))] = int(m.group(2))

    lines = []
    lines.append("-- AUTO-GENERATED by tools/gen_skill_meta.py - do not hand-edit")
    lines.append("-- Horse: STRICT ALLOWLIST / DEFAULT-DENY (see VERIFIED_HORSE_ALLOWLIST in generator)")
    lines.append("-- AttackRadius: settings/skills.txt; tiles = ceil(px/32); AR=0 -> 64px/2 tiles failsafe")
    lines.append("-- GetDistanceRadius uses TILE units; cast compares tiles to meta.tiles")
    lines.append("SimSkillMeta = SimSkillMeta or {}")
    lines.append("SimSkillMeta.byId = {")

    meta_cache = {}
    for sid in sorted(skills.keys()):
        s = skills[sid]
        ar_raw = s["ar"]
        ar_out = ar_raw if ar_raw > 0 else 64
        tiles = ceil_tiles(ar_out)
        stype = skill_type(sid, ar_out if ar_raw > 0 else 0, s["melee"])
        horse, evidence = decide_horse(sid, s["hl"], stype)
        # support/trap force foot even if somehow listed
        if stype in ("trap", "support"):
            horse = 0
        rclass = range_class(ar_out if ar_raw > 0 else 0)
        melee_flag = 1 if stype == "melee" else 0
        meta_cache[sid] = {
            "horse": horse,
            "ar": ar_out,
            "ar_raw": ar_raw,
            "tiles": tiles,
            "melee": melee_flag,
            "hl": s["hl"],
            "t_horse": s["t_horse"],
            "name": s["name"],
            "stype": stype,
            "rclass": rclass,
            "evidence": evidence,
        }
        # Keep Lua table compact for engine: horse, ar, tiles, melee, type code
        # type: 0=attack/ranged, 1=melee, 2=trap, 3=support
        tcode = {"melee": 1, "trap": 2, "support": 3}.get(stype, 0)
        lines.append(
            "  [%d]={horse=%d,ar=%d,tiles=%d,melee=%d,typ=%d},"
            % (sid, horse, ar_out, tiles, melee_flag, tcode)
        )

    lines.append("}")
    lines.append("")
    lines.append("-- typ: 0=ranged/attack 1=melee 2=trap 3=support")
    lines.append("function SimSkillMeta:Get(skillId)")
    lines.append("  if not skillId or skillId <= 0 then return nil end")
    lines.append("  return self.byId[skillId]")
    lines.append("end")
    lines.append("")
    lines.append("function SimSkillMeta:GetSkillCombatMeta(skillId)")
    lines.append("  local m = self:Get(skillId)")
    lines.append("  if not m then return nil end")
    lines.append("  local typName = \"ranged\"")
    lines.append("  if m.typ == 1 then typName = \"melee\"")
    lines.append("  elseif m.typ == 2 then typName = \"trap\"")
    lines.append("  elseif m.typ == 3 then typName = \"support\" end")
    lines.append("  local rclass = \"long\"")
    lines.append("  if m.ar <= 120 then rclass = \"melee\"")
    lines.append("  elseif m.ar <= 256 then rclass = \"short\"")
    lines.append("  elseif m.ar <= 384 then rclass = \"mid\" end")
    lines.append("  return {")
    lines.append("    attackRadiusPx = m.ar,")
    lines.append("    attackRadiusTiles = m.tiles,")
    lines.append("    horseAllowed = m.horse,")
    lines.append("    rangeClass = rclass,")
    lines.append("    skillType = typName,")
    lines.append("  }")
    lines.append("end")
    lines.append("")
    lines.append("function SimSkillMeta:CanCastOnHorse(skillId)")
    lines.append("  local m = self:Get(skillId)")
    lines.append("  if m and m.horse == 1 then return 1 end")
    lines.append("  return 0")
    lines.append("end")
    lines.append("")
    lines.append("function SimSkillMeta:GetAttackRadiusTiles(skillId)")
    lines.append("  local m = self:Get(skillId)")
    lines.append("  if m and m.tiles and m.tiles > 0 then return m.tiles end")
    lines.append("  return nil")
    lines.append("end")
    lines.append("")
    lines.append("function SimSkillMeta:GetAttackRadiusPixels(skillId)")
    lines.append("  local m = self:Get(skillId)")
    lines.append("  if m and m.ar and m.ar > 0 then return m.ar end")
    lines.append("  return nil")
    lines.append("end")
    lines.append("")
    lines.append("function SimSkillMeta:IsMelee(skillId)")
    lines.append("  local m = self:Get(skillId)")
    lines.append("  if m and m.melee == 1 then return 1 end")
    lines.append("  return 0")
    lines.append("end")
    lines.append("")
    lines.append("function SimSkillMeta:IsTrap(skillId)")
    lines.append("  local m = self:Get(skillId)")
    lines.append("  if m and m.typ == 2 then return 1 end")
    lines.append("  return 0")
    lines.append("end")
    lines.append("")

    OUT_LUA.parent.mkdir(parents=True, exist_ok=True)
    OUT_LUA.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")

    # Report for FACTION_SKILLS
    report = []
    report.append("# FACTION_SKILLS Combat Metadata Audit")
    report.append("")
    report.append("Generated by `tools/gen_skill_meta.py`.")
    report.append("")
    report.append("## Policy")
    report.append("")
    report.append("- **Horse**: STRICT ALLOWLIST / DEFAULT-DENY.")
    report.append("- **Radius**: `settings/skills.txt` AttackRadius wins.")
    report.append("- **Tiles**: `ceil(px/32)` because `GetDistanceRadius` uses tile units.")
    report.append("- Unknown / unverified horse => **FOOT (NO)**.")
    report.append("")
    report.append("## Verified horse allowlist (generator)")
    report.append("")
    report.append("```")
    report.append(", ".join(str(x) for x in sorted(VERIFIED_HORSE_ALLOWLIST)))
    report.append("```")
    report.append("")
    report.append("| Faction | Branch | ReqLv | Skill ID | Skill Name | AR px | AR tiles | Range class | Skill type | HorseLimit | TimePerCastOnHorse | Mounted | Evidence |")
    report.append("|---|---|---:|---:|---|---:|---:|---|---|---:|---:|---|---|")

    missing = []
    discrepancies = []
    for fac in sorted(factions.keys()):
        for branch in sorted(factions[fac].keys()):
            for entry in factions[fac][branch]:
                sid = entry["id"]
                req = entry["reqLv"]
                m = meta_cache.get(sid)
                if not m:
                    missing.append((fac, branch, req, sid))
                    report.append(
                        f"| {fac} | {branch} | {req} | {sid} | MISSING | - | - | - | - | - | - | **NO** | missing from skills.txt |"
                    )
                    continue
                mounted = "YES" if m["horse"] == 1 else "NO"
                name = m["name"].replace("|", "/")[:40]
                # ASCII-safe name for md
                name_safe = "".join(ch if ord(ch) < 128 else "?" for ch in name)
                report.append(
                    f"| {fac} | {branch} | {req} | {sid} | {name_safe} | {m['ar']} | {m['tiles']} | {m['rclass']} | {m['stype']} | {m['hl']} | {m['t_horse']} | **{mounted}** | {m['evidence']} |"
                )
                if sid in lua_radius and lua_radius[sid] != m["ar_raw"] and m["ar_raw"] > 0:
                    discrepancies.append(
                        (sid, lua_radius[sid], m["ar_raw"], name_safe)
                    )

    report.append("")
    report.append("## skills.txt vs legacy SKILL_ATTACK_RADIUS discrepancies")
    report.append("")
    if not discrepancies:
        report.append("None for FACTION_SKILLS IDs (or no overlapping entries).")
    else:
        report.append("| Skill ID | Legacy Lua px | skills.txt AR | Name |")
        report.append("|---:|---:|---:|---|")
        for sid, legacy, txt, name in discrepancies:
            report.append(f"| {sid} | {legacy} | {txt} | {name} | Winner: **skills.txt** |")

    report.append("")
    report.append("## Missing from skills.txt")
    report.append("")
    if not missing:
        report.append("None.")
    else:
        for row in missing:
            report.append(f"- {row}")

    report.append("")
    report.append("## High-priority matrix check")
    report.append("")
    expect = {
        318: 0, 319: 0, 321: 1, 322: 1, 302: 1, 342: 0, 351: 0,
        355: 1, 336: 0, 337: 0, 361: 1, 362: 0, 368: 0, 375: 0,
        323: 0, 325: 0, 1059: 0, 1069: 0, 1076: 0,
    }
    report.append("| ID | Expected Mounted | Actual | Pass |")
    report.append("|---:|---|---|---|")
    for sid, exp in sorted(expect.items()):
        m = meta_cache.get(sid)
        act = m["horse"] if m else -1
        ok = "PASS" if act == exp else "FAIL"
        report.append(f"| {sid} | {exp} | {act} | {ok} |")

    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")

    # Sanity print
    fails = []
    for sid, exp in expect.items():
        m = meta_cache.get(sid)
        if not m or m["horse"] != exp:
            fails.append((sid, exp, m["horse"] if m else None))
    print("wrote", OUT_LUA)
    print("wrote", OUT_REPORT)
    print("allowlist size", len(VERIFIED_HORSE_ALLOWLIST))
    print("matrix fails", fails if fails else "none")
    print("faction skills missing", len(missing))


if __name__ == "__main__":
    main()

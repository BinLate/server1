import csv

rows = list(csv.DictReader(open("settings/skills.txt", "r", encoding="latin1"), delimiter="\t"))
lines = []
lines.append("-- AUTO-GENERATED from settings/skills.txt - do not hand edit")
lines.append("-- HorseLimit: 1 = can cast on horse (allowlist); 0 = MUST dismount (default deny)")
lines.append("-- AttackRadius: pixels; tiles = max(1, floor(AR/32)); AR=0 -> melee failsafe 2 tiles")
lines.append("SimSkillMeta = SimSkillMeta or {}")
lines.append("SimSkillMeta.byId = {")
for row in rows:
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
    horse = 1 if hl >= 1 else 0
    if ar <= 0:
        tiles = 2
        ar_out = 64
    else:
        tiles = max(1, ar // 32)
        ar_out = ar
    lines.append(
        "  [%d]={horse=%d,ar=%d,tiles=%d,melee=%d},"
        % (sid, horse, ar_out, tiles, melee)
    )
lines.append("}")
lines.append("")
lines.append("function SimSkillMeta:Get(skillId)")
lines.append("  if not skillId or skillId <= 0 then return nil end")
lines.append("  return self.byId[skillId]")
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
lines.append("  return 2")
lines.append("end")
lines.append("")
lines.append("function SimSkillMeta:GetAttackRadiusPixels(skillId)")
lines.append("  local m = self:Get(skillId)")
lines.append("  if m and m.ar and m.ar > 0 then return m.ar end")
lines.append("  return 64")
lines.append("end")
lines.append("")

out = "script/global/nobitaxd/vdk/simcity/components/sim.skill_meta.lua"
with open(out, "w", encoding="ascii", newline="\n") as f:
    f.write("\n".join(lines) + "\n")
print("wrote", out, "entries", len(lines))

# SimBot Horse / Range Combat Authenticity Audit (final)

## Policy

**Only positively verified skill IDs may cast while mounted. Everything else dismounts.**

**Every cast uses the exact AttackRadius of the exact pending skill.**

Horse and range are independent (`MOUNTED+MELEE`, `MOUNTED+RANGED`, `FOOT+MELEE`, `FOOT+RANGED`).

## Single source of truth

| Concern | Authority |
|---------|-----------|
| Runtime meta | `sim.skill_meta.lua` via `SimSkillMeta:GetSkillCombatMeta(id)` |
| Generator | `tools/gen_skill_meta.py` |
| Radius | `settings/skills.txt` AttackRadius (wins over legacy Lua tables) |
| Horse | STRICT allowlist in generator (`VERIFIED_HORSE_ALLOWLIST`) + requires `HorseLimit==0` |
| Validator | `tools/validate_simbot_skill_meta.py` |
| Full FACTION_SKILLS table | `plans/.../reports/faction-skills-combat-meta.md` |

### Removed contradictions

- `SimProgression.HORSE_SKILLS` emptied (stub only)
- `SIMBOT_DISMOUNT_SKILLS = nil`
- `SIMBOT_SKILL_RANGE = nil`

## HorseLimit vs allowlist

`HorseLimit` alone is insufficient (many HL=0 support/buff skills must stay FOOT).

Final horse decision:

```text
horseAllowed = 1
  IFF skillId in VERIFIED_HORSE_ALLOWLIST
  AND HorseLimit == 0
  AND skill is not trap/support
ELSE horseAllowed = 0
```

Verified allowlist (HL=0 confirmed): `13, 32, 64, 74, 302, 321, 322, 355, 361, 1057, 1067`

Excluded despite classic "maybe mounted" when `HorseLimit!=0`: `1059`, `1069`, `1076`.

## Tile conversion

`GetDistanceRadius` uses **tile** units.

```text
tiles = ceil(AttackRadiusPx / 32)   -- (px + 31) // 32
90px -> 3 tiles (not floored to 2)
60px -> 2 tiles
470px -> 15 tiles
```

## Pending-skill pipeline

```text
SimPickSkill once -> pendingSkillId
  -> GetSkillCombatMeta
  -> range / horse / type from SAME id
  -> move / dismount / cast SAME id
```

No second `SimPickSkill` between range check and cast on BV path.

## High-priority matrix

| ID | Mounted | AR px | tiles | Notes |
|----|---------|------:|------:|-------|
| 318 | NO | 90 | 3 | melee foot |
| 321 | YES | 400 | 13 | mounted ranged |
| 322 | YES | 90 | 3 | mounted melee (must chase) |
| 302 | YES | 470 | 15 | mounted long |
| 342 | NO | 360 | 12 | foot ranged |
| 351 | NO | 50 | 2 | trap |
| 355 | YES | 180 | 6 | mounted mid |
| 361 | YES | 60 | 2 | mounted melee (must get close) |
| 362 | NO | 420 | 14 | foot long |
| 368 | NO | 90 | 3 | foot melee |
| 375 | NO | 470 | 15 | Conlon lightning FOOT |

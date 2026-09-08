# Client skill VFX vs server cast (2026-09-04)

## Client: `Client_VLTK_SHXT`

| Asset | Status |
|-------|--------|
| `data/skills.pak` | Present (~40 MB, PACK) |
| `data/spr.pak` | Present (~738 MB) |
| `settings/skills.txt` | 1224 skills; train IDs 318/321/322/351/355/361/372/375 all present |
| CharAnimId | Most skills have anim IDs (Client can play cast pose) |
| PreCastSpr | Sparse (e.g. 361/372/375 have `.spr`); many skills rely on anim/missile instead |

**Verdict:** Client package is sufficient for faction skill VFX. Missing visuals were not due to absent `skills.pak`.

## Server fix

Engine AI alone often **auto-attacks** (little/no skill VFX). Train bots now:

1. `SetNpcCombat(1, skillId)` on JoinFight + while fighting
2. Lua `Update` every fight tick (force cast)
3. Prefer `BotDoSkill(caster, skill, lv, targetIndex)` for NPC targets
4. `TRAIN_SKILL_CAST_CD_TICKS = 1` shorter cast gap

Restart GS / reload scripts, respawn train bots, watch faction skill anims on Client.

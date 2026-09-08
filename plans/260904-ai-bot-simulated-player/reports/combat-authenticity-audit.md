# SimBot Horse / Range / PK — Canonical Standard (locked 2026-09-04)

## Horse + range matrix (9x primary skills)

| Branch | Skill ID | Horse | Range |
|--------|--------:|-------|-------|
| Thieu Lam Quyen | 318 | FOOT | melee |
| Thieu Lam Bong | 319 | FOOT | melee |
| Thieu Lam Dao | 321 | **MOUNT** | ranged |
| Thien Vuong Thuong | 323 | FOOT | melee |
| Thien Vuong Dao | 322 | **MOUNT** | melee |
| Thien Vuong Chuy | 325 | FOOT | melee |
| Duong Mon Tu Tien | 302 | **MOUNT** | long |
| Duong Mon Phi Tieu | 342 | FOOT | ranged |
| Duong Mon Phi Dao | 339 | FOOT | ranged |
| Duong Mon Bay | 351 | FOOT | trap |
| Ngu Doc Dao | 355 | **MOUNT** | mid/ranged |
| Ngu Doc Chuong | 353 | FOOT | ranged |
| Nga Mi Kiem | 328 | FOOT | ranged |
| Nga Mi Chuong | 380 | FOOT | ranged |
| Thuy Yen Don Dao | 336 | FOOT | ranged |
| Thuy Yen Song Dao | 337 | FOOT | ranged |
| Cai Bang Chuong | 357 | FOOT | ranged |
| Cai Bang Bong | 359 | FOOT | ranged |
| Thien Nhan Mau | 361 | **MOUNT** | melee |
| Thien Nhan Dao | 362 | FOOT | ranged |
| Vo Dang Kiem | 368 | FOOT | melee |
| Vo Dang Khi | 365 | FOOT | long |
| Con Lon Dao | 372 | FOOT | ranged |
| Con Lon Kiem | 375 | FOOT | long |

Source of truth: `tools/gen_skill_meta.py` → `USER_CANONICAL_9X` + `VERIFIED_HORSE_ALLOWLIST`.

## PK / Do Sat training bots

- Peaceful train bots use **camp 1–3** (never camp 0 — camp 0 is unattackable by players on this engine).
- Do Sat bots use **camp 5**.
- Train bots stay `NpcKind=0` always (player-attackable).
- No potion heal while under player PK (`duelPlayerId` / `selfDefTick`).
- Train combat uses **Lua cast** (`SetNpcAI 0`), not engine AI mode 1 (which cast while mounted).

## Runtime API

```lua
SimSkillMeta:GetSkillCombatMeta(skillId)
-- horseAllowed, attackRadiusPx, attackRadiusTiles, rangeClass, skillType
```

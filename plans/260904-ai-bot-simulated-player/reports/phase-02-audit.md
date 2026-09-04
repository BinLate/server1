# Phase 02 Audit — Growth / Train lifecycle

Date: 2026-09-04

## Feature matrix

| Feature | Label | Notes |
|---------|-------|-------|
| `pluyencong` AOI scan / hibernate | COMPLETE | `ATick` + `hibernateMap` + ClearMap(train) |
| Roster Save/Load atomic | COMPLETE | `SIMROSTER_V1` + tmp rename; Lua 4.0 pcall-safe |
| EXP while fighting | COMPLETE | `sim.core` trainExpTick → `AddExp` |
| Level up / gear apply | PARTIAL | `OnLevelUp` exists; gear depth = Phase 3 |
| Map migration on outlevel | COMPLETE | Hibernate migrates roster to next tier |
| Caps per-map / global | COMPLETE | `TRAIN_BOT_*` knobs |
| Spawn start ~lv 10 | BROKEN→FIXED | Was random(min,max) or level=1; now `SIMBOT_TRAIN_START_LEVEL` |
| TRAIN_MAPS map IDs | BROKEN→FIXED | Wrong IDs (11=city, 325=bao danh TK, …) corrected vs `thanhthi.txt` |
| Dual spawn pthanhthi+AOI | BROKEN→FIXED | Early delegate on train maps; removed bulk train branch |
| Idempotent no-dup | PARTIAL | Count gate exists; no stable bot UUID yet |
| Death→respawn same identity | PARTIAL | noRevive=0; name/level from roster on re-spawn after hibernate |

## Corrected TRAIN_MAPS

| Tier | Name | mapId |
|------|------|-------|
| 1-20 | Ba Lang Huyen | 53 |
| 20-40 | Phuc Nguu Son Tay | 41 |
| 40-60 | Kinh Hoang Dong | 5 |
| 60-80 | Lam Du Quan | 319 |
| 80-90 | Dao Hoa Nguyen | 55 |
| 90-120 | Truong Bach Son Nam | 321 |
| 120-150 | Mac Bac Thao Nguyen | 341 |
| 150-180 | Sa Mac Tang 1 | 225 |
| 180-200 | Vi Son Dao | 342 |

## Still open (next Phase 2 slices)

- Stable identity key beyond `szName` order in roster file
- Periodic save while map active (not only hibernate)
- Skill curve polish / map transfer while awake

# Phase 02: Bot lớn dần + tự train (+ kiến trúc population)
Status: 🟡 In Progress
Dependencies: Phase 01

## Objective

Feature cốt lõi: bot có **persistent identity/lifecycle** — spawn ~cấp 10, tự train, EXP/level/skill, đổi bãi, chết→hồi sinh→tiếp tục; hibernate rồi trở lại **cùng bot**, giữ progression, lên tới max level server.

AOI/hibernate/budget là **yêu cầu kiến trúc từ phase này**, không chờ Phase 07.

## Requirements

### Functional
- [x] Audit `pluyencong.lua` + `sim.progression` + roster save/load: PARTIAL→COMPLETE (slice 1)
- [x] Spawn level theo config (mặc định ~10) — `SIMBOT_TRAIN_START_LEVEL`
- [x] Tự tìm quái, nhận EXP, level up (core ticks) — skill polish còn lại
- [x] Đổi bãi train theo sức mạnh / map table (hibernate migrate)
- [ ] Death → respawn → tiếp tục cùng identity (PARTIAL)
- [x] Hibernate/AOI: map trống → sleep; có player → wake roster
- [ ] Idempotent spawn: **no duplicate** cùng bot id (count gate only)
- [x] Global/map bot caps (`TRAIN_BOT_MAX_PER_MAP`, `TRAIN_BOT_GLOBAL_BUDGET`)

### Non-Functional
- [x] Bounded pathfinding & timers (existing)
- [x] Persistence atomic (đã có `_sim_*`; Lua 4.0 safe)
- [x] Không block game loop khi I/O save (hibernate path)

## Implementation Steps
1. [x] Audit matrix train lifecycle vs vision
2. [ ] Định nghĩa identity key (mapId + botId/name stable)
3. [x] Wire Save/Load roster vào spawn/hibernate paths (AOI owns train maps)
4. [ ] Level/skill curve tới `SIMBOT_MAX_LEVEL` / max server
5. [x] Map transfer rules khi “đủ mạnh” (on hibernate)
6. [ ] Stress: caps, no leak timers, no dup bots
7. [x] Fix TRAIN_MAPS IDs + remove pthanhthi dual train spawn

## Files
- `plugins/pluyencong.lua`
- `components/sim.progression.lua`
- `components/sim.fight.lua` / `sim.core.lua` (EXP hooks)
- `config.lua` (caps, start level)
- `tests/` train/persistence

## Test Criteria
- [ ] Restart server: roster file giữ level
- [ ] Hibernate → wake: cùng level/exp
- [ ] Không vượt global budget
- [ ] Unit/integration tests xanh

## Notes
Tận dụng code hiện có — **không** tạo subsystem train song song.

**Blocker (2026-09-04):** bot trên Lâm Du Quan đứng cạnh quái không đánh — xem plan fix riêng [phase-02b-train-combat-fix.md](phase-02b-train-combat-fix.md) trước khi tiếp identity/save.

---
Next: [phase-02b-train-combat-fix.md](phase-02b-train-combat-fix.md) → rồi [phase-03-gear-horse.md](phase-03-gear-horse.md)

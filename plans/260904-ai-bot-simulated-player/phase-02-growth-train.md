# Phase 02: Bot lớn dần + tự train (+ kiến trúc population)
Status: ⬜ Pending
Dependencies: Phase 01

## Objective

Feature cốt lõi: bot có **persistent identity/lifecycle** — spawn ~cấp 10, tự train, EXP/level/skill, đổi bãi, chết→hồi sinh→tiếp tục; hibernate rồi trở lại **cùng bot**, giữ progression, lên tới max level server.

AOI/hibernate/budget là **yêu cầu kiến trúc từ phase này**, không chờ Phase 07.

## Requirements

### Functional
- [ ] Audit `pluyencong.lua` + `sim.progression` + roster save/load: PARTIAL→COMPLETE
- [ ] Spawn level theo config (mặc định ~10)
- [ ] Tự tìm quái, nhận EXP, level up, cập nhật skill theo level
- [ ] Đổi bãi train theo sức mạnh / map table
- [ ] Death → respawn → tiếp tục cùng identity
- [ ] Hibernate/AOI: map trống → sleep; có player → wake **cùng roster**
- [ ] Idempotent spawn: **no duplicate** cùng bot id
- [ ] Global/map bot caps (`TRAIN_BOT_MAX_PER_MAP`, `TRAIN_BOT_GLOBAL_BUDGET`)

### Non-Functional
- [ ] Bounded pathfinding & timers
- [ ] Persistence atomic (đã có hướng `_sim_*`; verify Lua 4.0 safe)
- [ ] Không block game loop khi I/O save

## Implementation Steps
1. [ ] Audit matrix train lifecycle vs vision
2. [ ] Định nghĩa identity key (mapId + botId/name stable)
3. [ ] Wire Save/Load roster vào spawn/hibernate paths
4. [ ] Level/skill curve tới `SIMBOT_MAX_LEVEL` / max server
5. [ ] Map transfer rules khi “đủ mạnh”
6. [ ] Stress: caps, no leak timers, no dup bots

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

---
Next Phase: [phase-03-gear-horse.md](phase-03-gear-horse.md)

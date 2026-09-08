# Phase 03: Trang bị + ngựa theo cấp
Status: ⬜ Pending
Dependencies: Phase 02

## Objective

Gear/ngựa tăng dần theo level. Không còn bot low-level cưỡi ngựa/endgame. Stat hiển thị “có tác dụng” phải ảnh hưởng combat thật qua API/data JX1 — không fake nếu engine không hỗ trợ.

## Requirements

### Functional
- [ ] Audit `sim.gear.lua` / `pngoaitrang.lua` / ApplyGearByLevel
- [ ] Bảng tier theo level (vũ khí, giáp, ngựa)
- [ ] On level-up: refresh visual + combat-relevant stats nếu API cho phép
- [ ] Verify từng stat với engine (document: supported vs cosmetic-only)

### Non-Functional
- [ ] Không tăng chi phí spawn quá mức (cache templates)
- [ ] Lua 4.0 safe

## Implementation Steps
1. [ ] Matrix: cosmetic vs real combat modifiers
2. [ ] Map level → gear tier; horse unlock thresholds
3. [ ] Hook level-up + train spawn apply
4. [ ] In-game verify damage/speed/defense deltas

## Files
- `components/sim.gear.lua`, `sim.progression.lua` (ApplyGearByLevel)
- `plugins/pngoaitrang.lua`
- Settings/item tables nếu cần

## Test Criteria
- [ ] LV10 không ra ngựa/endgame look
- [ ] LV cao đổi ngựa/đồ đúng tier
- [ ] Combat khác biệt đo được với stat engine hỗ trợ

---
Next Phase: [phase-04-faction-behavior.md](phase-04-faction-behavior.md)

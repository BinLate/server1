# Phase 04: Hành vi môn phái
Status: ⬜ Pending
Dependencies: Phase 03

## Objective

Mỗi môn phái đánh khác nhau: cận áp sát, xa giữ khoảng, skill đúng radius, xuống ngựa khi `HorseLimit`, heal/buff/control đúng phái. Xác minh từ game data — không đoán semantics.

## Requirements

### Functional
- [ ] Audit melee/ranged tables (`SIMBOT_MELEE_SKILLS`, skill range)
- [ ] Đọc `HorseLimit` / skill radius từ setting/skill data thật
- [ ] Melee: close distance trước khi cast
- [ ] Ranged: kite/maintain range
- [ ] Dismount khi skill yêu cầu
- [ ] Faction buff/heal/control paths đúng phái

### Non-Functional
- [ ] Không spam pathfind mỗi tick vượt bound
- [ ] Regression train + thành thị

## Implementation Steps
1. [ ] Extract skill metadata từ settings (document nguồn file)
2. [ ] State machine combat đã có (Phase C) → gắn faction profiles
3. [ ] Tests: TL cận vs NM xa vs cưỡi ngựa
4. [ ] Tune khoảng cách theo radius thực

## Files
- `components/sim.fight.lua`, `sim.movement.lua`, `sim.progression.lua`
- Skill/settings data under `settings/` hoặc engine tables

## Test Criteria
- [ ] Quan sát ingame: nhận ra đặc trưng phái
- [ ] Không cast skill out-of-range liên tục
- [ ] HorseLimit được tôn trọng

---
Next Phase: [phase-05-tong-kim.md](phase-05-tong-kim.md)

# Phase 07: Thế giới sống (polish)
Status: ⬜ Pending
Dependencies: Phase 06; kiến trúc AOI đã có từ Phase 02

## Objective

Polish cảm giác “Võ Lâm vẫn sống khi solo”. AOI/hibernate/budget **đã là yêu cầu từ Phase 02** — phase này tối ưu cảm giác: gặp bot ngang đường, về thành thấy người, giờ TK có trận, gặp lại bot đã lớn.

## Requirements

### Functional
- [ ] Cảm giác mật độ thành/thôn hợp lý theo giờ
- [ ] Cross-map sightings (bot train chạy ngang)
- [ ] “Meet again” narrative (cùng identity đã level-up)
- [ ] Soft events: đi thành, tụ tập attraction — không phá caps

### Non-Functional
- [ ] Re-verify global caps, timer bounds, pathfinding bounds
- [ ] Profiling CPU với 1 player solo

## Implementation Steps
1. [ ] Telemetry: bot counts per map, hibernate ratio
2. [ ] Tune THANHTHI_SIZE / THON_SIZE / train budgets
3. [ ] Optional schedule (giờ TK / giờ đông thành)
4. [ ] Final acceptance vs vision doc

## Files
- `config.lua`, `pluyencong.lua`, `pthanhthi.lua`, reports

## Test Criteria
- [ ] Solo 30–60 phút: vẫn thấy hoạt động, không leak bot/timer
- [ ] Caps không bị phá
- [ ] Vision checklist PASS phần gameplay (social AI tùy Phase 06)

---
Back to [plan.md](plan.md)

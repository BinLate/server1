# Phase 01: Thành thị như bản gốc
Status: 🟡 In Progress
Dependencies: Phase 00 ✅

## Objective

Khôi phục behavior thành thị ổn định từ `server1-goc` / upstream [vinh-ttn/simcity](https://github.com/vinh-ttn/simcity) trước khi mở rộng AI.

## Requirements

### Functional
- [x] Audit matrix thành thị: walk / stall / fight / chat chance / Triệu Mẫn / Vô Kỵ / EnterMap spawn
- [x] Bot đi lại trên nodes/preset paths (path COMPLETE vs goc; live confirm pending)
- [x] Gian hàng / attraction behavior như gốc (code COMPLETE)
- [x] Bot-vs-bot / chance fight theo config gốc (không “AI mới”)
- [x] NPC điều khiển SimCity (Triệu Mẫn menu) hoạt động — indent + Luyện Công guard
- [x] Không rewrite hệ thống đang `COMPLETE`

### Non-Functional
- [x] Diff tối thiểu so với goc trên đường spawn thành thị
- [x] Regression: spawn Phase 0 vẫn xanh (user confirm)

## Implementation Steps
1. [x] Feature matrix `COMPLETE/PARTIAL/BROKEN/MISSING` (report)
2. [x] Fix BROKEN: eager `initThanhThi`, lazy `Get`, EnterMap guard, menu cleanup
3. [ ] Verify 7 thành chính + vài thôn (user / live)
4. [x] Document config knobs thành thị (`THANHTHI_SIZE`, `STARTUP_AUTOADD_THANHTHI`, …) — see audit report

## Files (expected touch)
- `plugins/pthanhthi.lua`, `pworld.lua`, `pnpcinfo.lua`, `pchat.lua`
- `controllers/thanhthi.lua`, `vdk/main.lua` (EnterMap Reg)
- Settings: `settings/global/vdk/simcity/maps/**`

## Test Criteria
- [ ] Vào Tương Dương / Biện Kinh: bot đi + có tương tác đánh nhau theo chance
- [ ] Menu Triệu Mẫn mở được
- [ ] Không luaerror mới

---
Next Phase: [phase-02-growth-train.md](phase-02-growth-train.md)

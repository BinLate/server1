# Phase 01: Thành thị như bản gốc
Status: ⬜ Pending
Dependencies: Phase 00

## Objective

Khôi phục behavior thành thị ổn định từ `server1-goc` / upstream [vinh-ttn/simcity](https://github.com/vinh-ttn/simcity) trước khi mở rộng AI.

## Requirements

### Functional
- [ ] Audit matrix thành thị: walk / stall / fight / chat chance / Triệu Mẫn / Vô Kỵ / EnterMap spawn
- [ ] Bot đi lại trên nodes/preset paths
- [ ] Gian hàng / attraction behavior như gốc
- [ ] Bot-vs-bot / chance fight theo config gốc (không “AI mới”)
- [ ] NPC điều khiển SimCity (Triệu Mẫn menu) hoạt động
- [ ] Không rewrite hệ thống đang `COMPLETE`

### Non-Functional
- [ ] Diff tối thiểu so với goc trên đường spawn thành thị
- [ ] Regression: spawn Phase 0 vẫn xanh

## Implementation Steps
1. [ ] Feature matrix `COMPLETE/PARTIAL/BROKEN/MISSING` (report)
2. [ ] Port/fix từng mục BROKEN từ goc hoặc upstream — từng PR nhỏ
3. [ ] Verify 7 thành chính + vài thôn
4. [ ] Document config knobs thành thị (`THANHTHI_SIZE`, `STARTUP_AUTOADD_THANHTHI`, …)

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

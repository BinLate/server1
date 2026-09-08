# Phase 00: Restore spawn (blocker)
Status: 🟡 In Progress
Dependencies: none

## Objective

Khôi phục spawn SimBot ổn định khi vào thành. Đây là blocker — không mở rộng AI cho đến khi acceptance pass.

## Known live failure (2026-09-04)

`\\192.168.1.188\jxser\server1\Logs\script\luaerror_2026_09_04.txt`:

```
attempt to perform arithmetic on field `x' (a nil value)
  function loadMap at data.lua:284
```

Chuỗi: `loadMap` crash khi Include `data.lua` → `SimCityMap`/nodes không hoàn chỉnh → EnterMap không spawn.

Lưu ý: log trong Documents `server1\Logs` có thể trống trong khi server live vẫn lỗi.

## Requirements

### Functional
- [ ] Audit matrix spawn path: `COMPLETE/PARTIAL/BROKEN/MISSING` vs `server1-goc` + upstream
- [ ] Fix tận gốc nil `x` trong `loadMap` (không “nuốt” lỗi rồi tiếp tục với graph hỏng)
- [ ] Harden Include chain cho Kingsoft Lua 4.0 (đã có một phần; verify còn sót)
- [ ] Enter map thành thị → bot xuất hiện ổn định
- [ ] Timers `mainLoop` / `worldLoop` chạy khi class load thành công

### Non-Functional
- [ ] `luaerror` sau restart: không còn lỗi liên quan simcity/`data.lua`/`progression`
- [ ] Không tăng CPU ngoài baseline goc khi idle trong thành

## Root-cause hypothesis (to verify)

Final-touch preset path trong `libs/data.lua` tạo `world.nodes[nodeName]` với `x,y` từ `nodeNameToCoords`. Nếu tên waypoint không parse được → node độc với `x=nil` → vòng link (`otherNode.x - …`) crash.

So với `server1-goc`: cùng pattern — nghĩa là **dữ liệu/preset path hoặc TabFile fallback** trên server1 đang đưa tên node xấu vào graph. Fix đúng = không bao giờ đưa node thiếu tọa độ vào `world.nodes`; sửa nguồn preset / parse; đồng thời không để node cũ thiếu `x` tồn tại.

## Implementation Steps
1. [ ] Diff spawn chain: `head.lua`, `vdk/main.lua`, `main.lua`, `data.lua`, `pthanhthi.lua`, `config.lua`
2. [ ] Reproduce: tìm preset/node name nào sinh `x=nil` (so file settings maps)
3. [ ] Fix `loadMap` final-touch: chỉ tạo node khi `x,y` hợp lệ; loại/sửa waypoint preset lỗi tại nguồn
4. [ ] Verify không còn nested outer-scope closures / `local function` / `/* */`
5. [ ] Sync live server + restart script; check `luaerror` + vào Tương Dương
6. [ ] Ghi evidence vào `reports/phase-00-verify.md`

## Files to Create/Modify
- `script/global/nobitaxd/vdk/simcity/libs/data.lua` — loadMap graph integrity
- `script/global/nobitaxd/vdk/simcity/libs/common.lua` — helpers nếu cần (không fake distance)
- `tests/test_lua40_compat.py` / thêm test loadMap nếu khả thi
- `plans/.../reports/phase-00-*.md`

## Test Criteria
- [ ] `pytest tests/test_lua40_compat.py` PASS
- [ ] Live `luaerror_*.txt` không còn stack `loadMap` / `sim.progression` outer-scope
- [ ] Vào map thành (VD 78 Tương Dương): thấy simbot trong ~vài giây (`STARTUP_AUTOADD_THANHTHI=1`)

## Notes
- Không workaround bằng cách tắt SimCity hoặc bỏ Include.
- Không nâng population TK trong phase này.

---
Next Phase: [phase-01-thanh-thi-baseline.md](phase-01-thanh-thi-baseline.md)

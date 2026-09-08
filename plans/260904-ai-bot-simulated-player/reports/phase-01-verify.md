# Phase 01 Verify

Date: 2026-09-04

## Code changes (synced to live share)

| File | Change |
|------|--------|
| `head.lua` | Eager `SimCityWorld:initThanhThi()` after data/plugins init |
| `plugins/pworld.lua` | Lazy `Get` from `SimCityMap`; `Update` refuses ephemeral `{}` |
| `plugins/pthanhthi.lua` | Enter/ExitMap guard; menu indent + Luyện Công if plugin exists |

## Tests

- `pytest tests/test_simcity_world_get.py tests/test_lua40_compat.py tests/test_loadmap_graph_integrity.py` → **17 passed**
- Live hash match after copy to `\\192.168.1.188\jxser\server1\...`

## Live checklist (user)

1. Reload script / re-enter map (or GS reload if required)
2. Tương Dương / Biện Kinh: bots still walk + stall
3. Talk Triệu Mẫn: menu opens, population count shows
4. Confirm `Logs\script\luaerror_*.txt` stays clean

## Status

Phase 0 ✅ (user confirmed simbots). Phase 1 code ✅; awaiting user live menu/walk spot-check before marking Phase 1 Done and starting Phase 2.

# Plan: AI Bot Simulated Player (Võ Lâm Offline)
Created: 2026-09-04 11:26
Status: 🟡 In Progress
Owner decision: **1D 2B** — cân bằng, làm ít–làm chắc

## Overview

Xây **Simulated Player** trên nền SimCity JX1 Linux: bot lớn dần như người chơi, tự train, trang bị theo cấp, hành vi môn phái, Tống Kim thông minh — nhưng **không rewrite** SimCity từ đầu.

**Thứ tự triển khai (đã chốt):**
`Phase 0 → 1 → 2 → 3 → 4 → 5` rồi `6 → 7` (polish / social).

**MVP chơi được:** `0 → 1 → 2 → 5`  
Phase 3–4 làm ngay sau MVP vì gắn trực tiếp với “lớn lên như người thật”.

## Sources of truth

| Source | Path / URL | Vai trò |
|--------|------------|---------|
| Working baseline | `server1-goc/` | Behavior thành thị ổn định trước khi ZCode/AI sửa |
| Current worktree | `server1/` | Code đang chạy / sửa |
| Upstream SimCity | https://github.com/vinh-ttn/simcity | Bản gốc cộng đồng v5.11.1 |
| TK pressure guide | `Ap-luc-SimBot-Tong-Kim.pdf` | 6 cổng aggro, bẫy `CHANCE_*`, trần 32 ô |

## Priority stack (tuyệt đối)

1. Spawn ổn định  
2. Lifecycle đúng (persistent identity)  
3. Population bounded  
4. CPU / pathfinding ổn  
5. Gameplay  
6. Realism  
7. Social AI  

## Nguyên tắc trước mỗi phase

1. Audit `server1`
2. So `server1-goc`
3. So `vinh-ttn/simcity` (khi cần)
4. Gắn nhãn feature: `COMPLETE / PARTIAL / BROKEN / MISSING`
5. Reuse/fix trước khi viết mới
6. Engine = Kingsoft Lua 4.0 fork — không `local function`, không nested `pcall(function()…end)` capture outer local, không `/* */`

## Tech context

- Script root: `script/global/nobitaxd/vdk/simcity/`
- Entry: `head.lua` → plugins → `data.lua` → `sim_citizen` / `SimCore`
- Train: `plugins/pluyencong.lua` + `components/sim.progression.lua`
- Combat/move: `sim.fight.lua`, `sim.movement.lua`
- TK: `plugins/ptongkim.lua`, `battles/marshal/simtk.lua`, `config.lua`
- Hard caps (giữ): **5 Tống / 5 Kim / 10 SimBot TK tối đa**

## Phases

| Phase | Name | Status | Progress |
|-------|------|--------|----------|
| 00 | Restore spawn (blocker) | ✅ Done | 100% |
| 01 | Thành thị như bản gốc | 🟡 In Progress | 70% |
| 02 | Bot lớn dần + tự train (+ AOI/persistence kiến trúc) | ⬜ Pending | 0% |
| 03 | Trang bị + ngựa theo cấp | ⬜ Pending | 0% |
| 04 | Hành vi môn phái | ⬜ Pending | 0% |
| 05 | Tống Kim thông minh (5/5/10) | ⬜ Pending | 0% |
| 06 | Chat / giao dịch (sau MVP, không LLM trong MVP) | ⬜ Pending | 0% |
| 07 | Thế giới sống (polish AOI/feel) | ⬜ Pending | 0% |

## MVP definition

- [x] Vào thành thấy bot ổn định; `luaerror` không còn lỗi SimCity load
- [ ] Thành thị: đi lại / gian hàng / đánh nhau / NPC điều khiển như gốc
- [ ] Train bots: persistent identity, EXP/level, đổi bãi, hibernate không mất progression
- [ ] Tống Kim: tối đa 10 bot, tìm địch / chase có bound / rút lui / cleanup hết trận

## Out of MVP (Phase 6+)

- LLM chat, PM AI, mặc cả thông minh
- Nâng quân số TK lên >10

## Quick commands

- Start Phase 0: `/code phase-00` (hoặc bảo agent “làm Phase 0”)
- Next: `/next`
- Save context: `/save-brain`

## Reports

Xem `reports/` sau mỗi phase (audit matrix, luaerror evidence, verify notes).

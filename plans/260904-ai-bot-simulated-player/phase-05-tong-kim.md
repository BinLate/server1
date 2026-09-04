# Phase 05: Tống Kim thông minh (5/5/10)
Status: ⬜ Pending
Dependencies: Phase 04 (MVP có thể song song sau Phase 02 nếu cần — mặc định sau 04)

## Objective

Tống Kim **thông minh hơn**, không phải đông hơn. Giữ cứng: **5 Tống / 5 Kim / 10 SimBot tối đa**. Áp dụng ý tưởng hữu ích từ `Ap-luc-SimBot-Tong-Kim.pdf` với mọi tham số configurable và CPU ổn định.

## Hard caps (không đụng)

- `TONGKIM_SIMBOT_PER_CAMP = 5`
- `TONGKIM_SIMBOT_TOTAL = 10`
- Không nâng 20/30/60

## PDF gates (reference)

1. `GetNpcAroundPlayerList` scan radius (trần 32 ô thường; 60 train/PH)
2. `SIMBOT_AGGRO_PLAYER` + `RADIUS_FIGHT_PLAYER`
3. `SimCityCanFight` / `tkWarStarted`
4. `CHANCE_PREFER_PLAYER` (percent — chiều khác 4 nút kia)
5. `CHANCE_JOIN_FIGHT` (`random(0,N)<=2` → N nhỏ = hung)
6. `CHANCE_ATTACK_PLAYER` / revenge HP ratio

Bẫy: ghi chú “1/3000” sai; trần radius 32.

## Requirements

### Functional
- [ ] Tìm địch, truy đuổi có giới hạn (`SIMBOT_CHASE_MAX_TILES/TICKS`)
- [ ] Chia mục tiêu (không cả 10 đổ 1 người trừ khi config intentionally)
- [ ] Tập hợp nhẹ đồng đội
- [ ] Rút lui khi bất lợi → hồi phục → quay lại
- [ ] Death/respawn đúng trong trận
- [ ] Hết TK: cleanup hoàn toàn
- [ ] Nếu bot persistent: quay về lifecycle train (Phase 02)

### Non-Functional
- [ ] Mọi knobs trong config/webconfig — có preset Hiện tại / Gắt / Tàn khốc (tài liệu)
- [ ] Không mở scan 60 ô cho mọi tongkim nếu CPU không chịu (đo trước)

## Implementation Steps
1. [ ] Audit TK spawn/trim vs 5/5/10
2. [ ] Wire configurable pressure presets từ PDF
3. [ ] Target share + retreat state
4. [ ] Cleanup on war end + optional return-to-train
5. [ ] Measure `simtk_diag` / CPU

## Files
- `config.lua`, `webconfig.lua` (nếu có), `battles/marshal/simtk.lua`
- `plugins/ptongkim.lua`, `pchientranh.lua`
- `components/sim.movement.lua`, `sim.fight.lua`
- `Ap-luc-SimBot-Tong-Kim.pdf` (reference only)

## Test Criteria
- [ ] Không bao giờ >10 simbot TK
- [ ] Có truy đuổi / rút lui quan sát được
- [ ] Hết trận: 0 bot TK sót
- [ ] luaerror sạch

---
Next Phase: [phase-06-chat-trade.md](phase-06-chat-trade.md)

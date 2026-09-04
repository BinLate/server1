# Phase 02b: Fix SimBot train combat (đánh quái + cày cấp)

Status: 🔴 Ready to implement (chờ duyệt)
Dependencies: Phase 02 slice spawn/AOI
Evidence: Lâm Du Quan (map **319**) — bot đứng cạnh **Bôn Lôi**, không vào combat; trước đó Vũ Lăng Động (199) tương tự.

## Goal (DoD)

Trên map train (319 / 199 / …), bot `mode="train"`:

1. Tự **bật trạng thái chiến đấu** khi gần quái.
2. **Chạy tới + đánh** (AI engine + skill cast), không chỉ đi vòng.
3. Giữ `isFighting=1` đủ lâu để `sim.core` tick **EXP** (`trainExpTick`).
4. Không phá thanh thị (Ba Lang stall / cityPeace vẫn đúng).
5. Sau sync: **restart GS** → verify in-game trên Lâm Du Quan.

Encoding tiếng Việt: **không đụng** string TCVN3 trong `pthanhthi.lua` trừ khi có bằng chứng byte lệch; mọi comment/patch ASCII-only.

---

## Root cause (đã đối chiếu `server1-goc`)

Hai regression trong `sim.movement.lua` + filter quái trong `sim.fight.lua` làm bot **không vào / không giữ** combat:

### A. Case 3 — vào combat quá chặt (train)

| | `server1-goc` | `server1` hiện tại |
|---|---|---|
| Train Case 3 | `CHANCE_ATTACK_NPC > 1` → **JoinFight ngay** (engine AI tự tìm địch) | Chỉ JoinFight nếu `TriggerFightWithNPC` tìm được enemy |
| Hậu quả | Bot vào AI fight → quái bị aggro | Không tìm thấy enemy → mãi walk random |

`pluyencong` set `CHANCE_ATTACK_NPC = 2` đúng ý goc (luôn pass `random(1,2) <= 2` và `> 1`). Logic mới **bỏ mất** đường vào combat “mù” của goc.

### B. Case 2 — thoát combat quá sớm

| | `server1-goc` | `server1` hiện tại |
|---|---|---|
| `CanLeaveFight == 1` | `return 1` (**không** LeaveFight) | `LeaveFight(...)` ngay |
| Hậu quả | Giữ AI fight trong `tick_canswitch` | Vào fight 1 tick → không thấy enemy → thoát → chạy lung tung |

### C. `IsNpcEnemyAround` — filter kind

- **Goc:** chỉ `GetNpcKind == 0` (NPC kiểu người). Quái map thường **kind ≠ 0** → scan “không có địch”.
- **Hiện tại:** nới `fighter2Kind ~= nil` (đúng hướng) nhưng Case 2/3 vẫn phụ thuộc scan → nếu list/radius/param lệch vẫn fail.
- Chase/cast vẫn cần scan đúng **quái** (không skip nhầm, không nhắm simbot `GetNpcParam(_,4)==1`).

### D. Không phải map ID / không phải “chưa sync outdoor”

- Lâm Du Quan **đã** trong `TRAIN_MAPS` (`mapId=319`).
- `IsThanhThiMap` **không** gồm 319 → không bị `cityPeace=1` mặc định.
- Nếu AOI/`LUYENCONG_AUTOADD` chạy, bot phải `mode="train"`. Plan vẫn có bước **verify mode** (tránh nhầm bot thành thị / stall).

---

## Combat pipeline (chuẩn sau fix)

```
Breath tick (movement, isFighting==0)
  → SimCityCanFight == 1  (train / outdoorOk)
  → Case3: CHANCE_ATTACK_NPC > 1
      → JoinFight (train): SetNpcCombat + SetNpcAI(1) + optional NpcRun tới target
  → isFighting=1
Breath tick (isFighting==1)
  → Chase (NpcRun) nếu có target scan
  → Cast skill (fightSys:Update) khi có target
  → KHÔNG LeaveFight chỉ vì CanLeaveFight (giống goc); chỉ Leave khi hết tick_canswitch / peace zone / chết
sim.core
  → train + isFighting → AddExp định kỳ
```

---

## Implementation plan (3 slices)

### Slice 1 — Restore train engage/leave như goc (P0)

**Files:** `components/sim.movement.lua`

1. **Case 2 (đang fighting):** với `mode=="train"` (và optional outdoor grind), khi `CanLeaveFight==1` → `return 1` **không** gọi `LeaveFight` (khớp goc). Thành thị / tongkim giữ LeaveFight nếu cần an toàn PK.
2. **Case 3 (chưa fighting):** với `mode=="train"`:
   - Giữ ưu tiên `TriggerFightWithNPC` nếu đã có target.
   - Nếu chưa có target nhưng `CHANCE_ATTACK_NPC > 1` → **JoinFight** như goc (`"I start a fight"`).
3. Outdoor non-train (`allowFighting==1`, `cityPeace~=1`): cùng rule engage; leave rule cẩn thận (không để bot thành thị bị ép PK).

**Không** đổi menu / encoding.

### Slice 2 — Target scan chuẩn cho quái (P0)

**Files:** `components/sim.fight.lua`

1. `IsNpcEnemyAround` (Citizen):
   - Skip self + simbot (`GetNpcParam(i,4)==1`).
   - Train/outdoor: chấp nhận **monster kind** (không chỉ kind==0). Ưu tiên: kind monster trước, rồi kind==0 khác camp / non-simbot.
   - Radius train: dùng `RADIUS_FIGHT_SCAN` bot (đã 20) — không rơi về config mặc định 8 nếu thiếu field.
2. `JoinFight` train/outdoor: giữ `SetFightState` + `SetNpcCombat`; nếu có `foundNpcEnemy` thì `NpcRun`; gọi `Update` cast ngay 1 nhịp.
3. `TriggerFightWithNPC`: train luôn được phép (đã có); giữ outdoorOk.

**So sánh regression:** unit/logic test mô phỏng bảng quyết định (kind/camp/param) — không cần GS.

### Slice 3 — Verify spawn + EXP + sync (P1)

**Files:** `plugins/pluyencong.lua`, `plugins/pthanhthi.lua` (ASCII-only), optional debug flag

1. Confirm `createNpcSoCapByMap` early-return train → `spawnForMap` (không spawn thanhthi chồng).
2. Confirm spawn fields: `mode="train"`, `CHANCE_ATTACK_NPC=2`, `leaveFightWhenNoEnemy=0`, `RADIUS_FIGHT_SCAN=20`, `allowFighting=1`.
3. Optional: `SIMBOT_COMBAT_DEBUG=1` → `Msg2Player` / log thưa (mode, canFight, enemyIdx, join/leave reason) — tắt mặc định.
4. `sim.core` EXP: không đổi contract; chỉ verify điều kiện `mode==train && isFighting==1`.
5. Sync live (`sync_to_server.bat`) → **restart GameServer** → test map 319.

---

## Test plan (acceptance)

### In-game (bắt buộc)

1. Restart GS sau sync.
2. Vào **Lâm Du Quan** (319); đảm bảo Luyện Công auto-add / menu spawn map này.
3. Đứng cạnh **Bôn Lôi** + bot tên tiếng Việt (vd. BaVươngVương):
   - Trong ~vài giây bot **đổi tư thế / chạy tới quái / cast**.
   - Quái mất máu hoặc bot vào combat state.
4. Quan sát 1–2 phút: level/EXP bot tăng (hoặc debug tick EXP nếu có).
5. Spot-check **Ba Lang (53)**: stall vẫn ngồi bán; không PK loạn trong thành.

### Automated

- Extend / add `tests/` decision-table cho Case2/Case3 train vs thanhthi.
- Không save file Lua tiếng Việt bằng editor UTF-8.

### Fail → debug order

1. Bot có `mode=="train"` không? (nếu không → spawn path / ClearMap).
2. `SimCityCanFight`? (`worldInfo.allowFighting`, `cityPeace`).
3. `JoinFight` có gọi không? (debug flag).
4. `IsNpcEnemyAround` trả index quái? (kind/radius).
5. Có bị LeaveFight ngay tick sau? (Case 2).

---

## Out of scope (làm sau Phase 02b)

- Stable bot UUID / periodic roster save / no-dup identity (Phase 02 còn lại).
- Gear/horse (Phase 03).
- Sửa lại toàn bộ menu encoding trừ khi verify hex lệch goc.

---

## Risk & rollback

| Risk | Mitigation |
|------|------------|
| Train bot PK người chơi | Giữ `CHANCE_ATTACK_PLAYER` DoSat-only; Case 2 leave chỉ nới cho train/outdoor |
| Bot đánh cả simbot khác | Skip `GetNpcParam(_,4)==1` |
| Re-corrupt TCVN3 | ASCII-only edits; không rewrite `pthanhthi` Viet strings |
| Patch không vào live | Sync + **restart GS**; hash so khớp worktree |

Rollback: revert Slice 1–2 về behavior goc nguyên bản trong 2 file movement/fight.

---

## Effort estimate

- Slice 1: nhỏ (~30–60 phút) — impact lớn nhất  
- Slice 2: nhỏ–vừa  
- Slice 3 + in-game verify: phụ thuộc restart GS  

**Thứ tự:** Slice 1 → Slice 2 → sync/restart → verify ảnh Lâm Du Quan → rồi mới Phase 02 identity.

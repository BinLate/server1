# Train maps 0x-200 + faction camp colors

## Camp (engine name color)

From `npcthunghiem.lua`: `SetCamp(1)=Chinh`, `SetCamp(3)=Trung lap`, `SetCamp(2)=Ta phai`.

| Phe | Camp | Color | Factions |
|-----|-----:|-------|----------|
| Chinh phai | 1 | Vang | thieulam, ngami, caibang, vodang |
| Trung lap | 3 | Xanh | thienvuong, duongmon, thuyyen, conlon |
| Ta phai | 2 | Tim | ngudoc, thiennhan |
| Newbie 0x | 0 | Trang | level &lt; 10 |
| Do Sat | 5 | Do | TRAIN_DOSAT_PCT |
| Tong Kim | 1/2 | battlefield | tongkim=1, restore via `RestoreSimBotFactionCamp` |

API: `GetFactionCamp` / `ApplySimBotFactionCamp` in `libs/common.lua`.

## Level rule

`lv = random(minLv, maxLv)` per map bracket. Skills: highest `reqLv <= bot.level` (lv&lt;10 => skill 53 only).

## Maps

All Map IDs verified in `settings/global/vdk/simcity/maps/thanhthi.txt` (must have walk nodes). See `pluyencong.lua` TRAIN_MAPS.

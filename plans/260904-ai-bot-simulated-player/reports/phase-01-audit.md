# Phase 01 Audit — Thành thị baseline

Date: 2026-09-04  
Baseline: `server1-goc` + live confirm Phase 0 (user: vào game có simbot)

## Feature matrix

| Feature | server1 vs goc | Label | Notes |
|---------|----------------|-------|-------|
| City knobs (`STARTUP_AUTOADD_THANHTHI`, `THANHTHI_SIZE=300`, `THON_SIZE`, chance, `BOT_VS_BOT`) | Same core values | COMPLETE | Extra TK/AOI/SIMBOT_* knobs in server1 only (Phase 2–5 prep) |
| City spawn batch (`map9x==0` / thanh thi) | Same path, level 95 | COMPLETE | `_createSingle` defaults `mode="thanhthi"` |
| Stall bots (thành + 8 thôn + Đá Tàu) | Same gates | COMPLETE | |
| Walk / preset fallback | Same | COMPLETE | Missing presetPaths → `walkMode=random` |
| Fight chance / bot-vs-bot | Same config | COMPLETE | Train branch overrides CHANCE_* (Phase 2) |
| Chat chance | Plugin loaded | COMPLETE | `CHANCE_CHAT=10` |
| Triệu Mẫn menu | PARTIAL → fixed indent + guarded Luyện Công | PARTIAL→FIXED | Luyện Công line kept (Phase 2 entry), only if plugin exists |
| EnterMap → autoCreateNpc | Same | COMPLETE | |
| `initThanhThi` timing | goc: only via controller Include | BROKEN→FIXED | Now eager in `head.lua` + lazy `Get` |
| `SimCityWorld:Get` ephemeral `{}` | Same latent bug in goc | BROKEN→FIXED | Lazy hydrate from `SimCityMap`; Update refuses empty |
| Enter/ExitMap nil `playerTracker` | Same latent crash on unknown map | BROKEN→FIXED | Guard before index |
| Train branch (`LUYENCONG_AUTOADD`) | Persistence / level=1 | DEFERRED Phase 2 | Do not strip; city path isolated |
| `THON_SIZE` in `processBatches` | Unused in both | PARTIAL | Document only; matching goc leaves threshold=`THANHTHI_SIZE` |
| Controllers `thanhthi.lua` | Same init call | COMPLETE | Still safe as re-init |

## City maps (IsThanhThiMap)

37, 78, 176, 162, 80, 1, 11 — unchanged.

## Diff policy this phase

- Minimal city-path changes
- No rewrite of walk/fight/stall
- Train persistence left for Phase 2

## Verify checklist

- [x] Phase 0 live: user sees simbots; `luaerror_2026_09_04.txt` empty at Phase 1 start
- [ ] After sync: no new luaerror on enter Tương Dương / Biện Kinh
- [ ] Bot walk + stall present
- [ ] Triệu Mẫn menu opens (Luyện Công only if plugin present)

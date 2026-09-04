# Phase 00 — verify / audit notes
Date: 2026-09-04

## Live evidence (before fix)

`\\192.168.1.188\jxser\server1\Logs\script\luaerror_2026_09_04.txt` @ 11:14:

```
attempt to perform arithmetic on field `x' (a nil value)
  loadMap at data.lua:284
```

Local Documents `Logs\script` can be empty while live still errors — always check the running server tree.

## Root cause

1. Preset/node cells sometimes carry trailing `\r` (CRLF) from text files / fallback TabFile reader.
2. `nodeNameToCoords("1881_2598\r")` → `tonumber("2598\r")` = **nil**.
3. Final-touch still inserted `world.nodes[name] = { x=…, y=nil }`.
4. Link pass did `otherNode.x - world.nodes[testNode].x` → crash; `loadMap` aborted → incomplete `SimCityMap` → no spawn.

This is data-integrity corruption, not “skip the error”.

## Fix applied

- `SimCityTrimCell` + strict `nodeNameToCoords` (exactly 2 numeric parts) in `libs/common.lua`
- TabFile + fallback readers trim every cell; `*n` uses `tonumber(trim) or 0`
- `loadMap` stores canonical keys `format("%d_%d", x, y)`
- Final-touch: never insert node without numeric x,y; drop invalid waypoints; compact path; link only nodes with x,y; removed dead nil-unsafe `dx/dy` arithmetic
- `local allPaths` (was accidental global)

## Tests

- `pytest tests/test_lua40_compat.py tests/test_loadmap_graph_integrity.py` → 11 passed

## Live sync

Copied to `\\192.168.1.188\jxser\server1`:
- `libs/common.lua`, `libs/data.lua`

## Operator acceptance (manual)

1. `systemctl restart jxgame` (or equivalent script reload)
2. Confirm new `luaerror_*.txt` has no `loadMap` / nil `x` stacks
3. Enter Tương Dương (78) — simbots appear with `STARTUP_AUTOADD_THANHTHI=1`

## Audit matrix (spawn path) — snapshot

| Feature | server1 | vs goc | Label |
|---------|---------|--------|-------|
| loadMap graph | fixed CRLF/nil x | goc same crash pattern if tainted | was BROKEN → fixed |
| EnterMap Reg | guarded empty map | goc unguarded | PARTIAL (OK if map loads) |
| STARTUP_AUTOADD | 1 | 1 | COMPLETE |
| Sim*Sys constructors | present | present | COMPLETE |
| progression Include | outer-scope pcall fixed earlier | n/a in goc | was BROKEN → fixed prior |

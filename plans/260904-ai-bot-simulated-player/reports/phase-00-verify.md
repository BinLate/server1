# Phase 00 — correction note (2026-09-04 12:00)

## Apology / what went wrong

Earlier fixes treated symptoms and reported "done" too early:

1. First: CRLF trim (needed, but not enough).
2. Then: `getn(point)~=2` false positive → console flood of valid nodes.
3. Then: rate-limit the print → **hid** remaining failures instead of fixing them.

## Real root cause (verified)

Custom `split()` in `simcity/libs/common.lua` used:

```lua
strfind(szFullString, szSeparator, nFindStartIndex, 1)  -- Lua 5 "plain" 4th arg
```

On Kingsoft Lua 4.0 that 4th argument breaks matching, so `"_"` never splits.
`nodeNameToCoords("1361_2758")` left everything in `point[1]`, `point[2]=nil` → every preset node looked "invalid".

File data is fine (hex dump of `1_phuongtuong_preset.txt` is clean ASCII).

## Fix now on disk + live share

- Removed broken custom `split`; use `script/lib/string.lua` (with safe `if not split` fallback, **3-arg** `strfind` only).
- `loadMap` restored to server1-goc flow + only: trim cells, refuse nil x/y inserts, no drop spam.
- Live SHA256 matches local for `common.lua` + `data.lua`.
- Tests: 13 passed (`test_loadmap_graph_integrity` + `test_lua40_compat`).

## Operator check (do not mark Phase 0 complete until this)

1. Restart `server1` fully.
2. Startup log must **not** show `drop invalid preset node`.
3. `luaerror_*.txt` must not show `loadMap` / nil `x`.
4. Enter a city map → simbots visible.

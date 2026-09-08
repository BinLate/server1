# -*- coding: utf-8 -*-
import re
from pathlib import Path
src = Path("script/global/nobitaxd/vdk/simcity/components/sim.skill_meta.lua").read_text(encoding="ascii", errors="replace")
# expect horse: 1=mounted, 0=foot; melee: 1=near, 0=ranged
expect = {
    318: (0, 1, "TL Quyen"),
    319: (0, 1, "TL Bong"),
    321: (1, 0, "TL Dao"),
    323: (0, 1, "TV Thuong"),
    322: (1, 1, "TV Dao"),
    325: (0, 1, "TV Chuy"),
    302: (1, 0, "DM Tu Tien"),
    342: (0, 0, "DM Phi Tieu"),
    339: (0, 0, "DM Phi Dao"),
    351: (0, 1, "DM Bay"),  # trap near
    355: (1, 0, "ND Dao"),
    353: (0, 0, "ND Chuong"),
    328: (0, 0, "NM Kiem"),
    380: (0, 0, "NM Chuong"),
    336: (0, 0, "TY Don Dao"),
    337: (0, 0, "TY Song Dao"),
    357: (0, 0, "CB Chuong"),
    359: (0, 0, "CB Bong"),
    361: (1, 1, "TN Mau"),
    362: (0, 0, "TN Dao"),
    368: (0, 1, "VD Kiem"),
    365: (0, 0, "VD Khi"),
    372: (0, 0, "CL Dao"),
    375: (0, 0, "CL Kiem"),
}
print("ID horse melee typ ar tiles | want_h want_m | OK? name")
fails = []
for sid, (wh, wm, name) in expect.items():
    m = re.search(rf"\[{sid}\]={{([^}}]+)}}", src)
    if not m:
        print(sid, "MISSING")
        fails.append(sid)
        continue
    b = m.group(1)
    horse = int(re.search(r"horse=(\d+)", b).group(1))
    ar = int(re.search(r"ar=(\d+)", b).group(1))
    tiles = int(re.search(r"tiles=(\d+)", b).group(1))
    melee = int(re.search(r"melee=(\d+)", b).group(1))
    typ = int(re.search(r"typ=(\d+)", b).group(1))
    # for trap 351, melee flag may be 0 but typ=2; treat near as ar<=120 or typ==2
    near = 1 if (melee == 1 or typ == 2 or ar <= 120) else 0
    ok = (horse == wh) and (near == wm)
    if not ok:
        fails.append(sid)
    print(f"{sid:4d} h={horse} m={melee} t={typ} ar={ar:3d} tiles={tiles:2d} | want h={wh} near={wm} | {'OK' if ok else 'FAIL'} {name}")
print("FAILS", fails)

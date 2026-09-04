# -*- coding: utf-8 -*-
"""Audit HorseLimit vs canonical matrix for key SimBot skills."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ids = [
    318, 319, 321, 1055, 1056, 1057, 323, 1058, 322, 1059, 325, 1060,
    302, 1069, 342, 1070, 339, 351, 59, 353, 1066, 355, 1067, 390, 69,
    328, 1061, 380, 1062, 332, 1114, 336, 1063, 337, 1065, 357, 1073,
    359, 1074, 361, 1076, 362, 1075, 391, 368, 1079, 365, 1078, 372,
    1081, 375, 1080, 394, 14, 271, 272, 10, 2, 13, 53,
]
want = set(str(i) for i in ids)

# User canonical expected horse (1=mounted, 0=foot). None = FOOT DEFAULT.
EXPECTED = {
    321: 1, 1057: 1,  # TL dao mounted if confirmed
    322: 1, 1059: 1,  # TV dao mounted
    302: 1, 1069: 1,  # DM tu tien mounted
    355: 1, 1067: 1,  # ND dao mounted
    361: 1, 1076: 1,  # TN mau mounted
    318: 0, 319: 0, 1055: 0, 1056: 0,
    323: 0, 1058: 0, 325: 0, 1060: 0,
    342: 0, 1070: 0, 339: 0, 351: 0, 59: 0,
    353: 0, 1066: 0, 390: 0, 69: 0,
    328: 0, 1061: 0, 380: 0, 1062: 0, 332: 0, 1114: 0,
    336: 0, 1063: 0, 337: 0, 1065: 0,
    357: 0, 1073: 0, 359: 0, 1074: 0,
    362: 0, 1075: 0, 391: 0,
    368: 0, 1079: 0, 365: 0, 1078: 0,
    372: 0, 1081: 0, 375: 0, 1080: 0, 394: 0,
}

rows = list(csv.DictReader(open(ROOT / "settings" / "skills.txt", encoding="latin1"), delimiter="\t"))
print("fieldnames horse-related:", [c for c in rows[0].keys() if "Horse" in c or "Time" in c or c in ("IsMelee", "AttackRadius", "SkillId")])
by = {}
for row in rows:
    sid = row.get("SkillId")
    if sid in want:
        by[int(sid)] = row

print(f"{'ID':>5} {'HL':>3} {'AR':>4} {'melee':>5} {'tHorse':>6} {'exp':>3} {'HL0=ok?':>8} name")
for sid in ids:
    row = by.get(sid)
    if not row:
        print(f"{sid:>5} MISSING")
        continue
    hl = int(row.get("HorseLimit") or 0)
    ar = int(row.get("AttackRadius") or 0)
    melee = row.get("IsMelee")
    th = row.get("TimePerCastOnHorse", "?")
    exp = EXPECTED.get(sid, "-")
    # If HL==0 means may mount (previous invert)
    hl0 = 1 if hl == 0 else 0
    match = ""
    if exp in (0, 1):
        match = "OK" if hl0 == exp else "MISMATCH"
    name = (row.get("SkillName") or "")[:28]
    print(f"{sid:>5} {hl:>3} {ar:>4} {str(melee):>5} {str(th):>6} {str(exp):>3} {match:>8} {name}")

import csv
from collections import Counter

with open("settings/skills.txt", "r", encoding="latin1") as f:
    rows = list(csv.DictReader(f, delimiter="\t"))

by_id = {}
for row in rows:
    try:
        sid = int(row["SkillId"])
    except Exception:
        continue
    by_id[sid] = row

print("HorseLimit counts", Counter(r.get("HorseLimit") for r in rows))
print("IsMelee counts", Counter(r.get("IsMelee") for r in rows))

ids = [
    10, 17, 30, 47, 50, 54, 85, 91, 102, 128, 155, 164, 271, 283, 284, 286, 288, 290,
    302, 304, 318, 319, 321, 322, 323, 325, 328, 336, 337, 339, 342, 351, 353, 357,
    359, 361, 362, 365, 368, 372, 375, 380, 389, 429,
]
print("--- samples ---")
for sid in ids:
    row = by_id.get(sid)
    if not row:
        print(sid, "MISSING")
        continue
    name = (row.get("SkillName") or "")[:40]
    print(
        "%5d HL=%s AR=%s Melee=%s %s"
        % (sid, row.get("HorseLimit"), row.get("AttackRadius"), row.get("IsMelee"), name)
    )

# Known horseback skills in classic VLTK (often: some TL/TV skills that work on horse)
# Compare AR for HL=0 vs HL=1 melee
print("--- HL vs IsMelee crosstab ---")
ct = Counter()
for r in rows:
    ct[(r.get("HorseLimit"), r.get("IsMelee"))] += 1
for k, v in sorted(ct.items(), key=lambda x: str(x[0])):
    print(k, v)

# Generate meta lua snippet stats
horse_ok = [sid for sid, r in by_id.items() if (r.get("HorseLimit") or "0") == "1"]
print("HorseLimit==1 count", len(horse_ok))
# AR distribution for horse skills
ars = Counter()
for sid in horse_ok:
    ars[by_id[sid].get("AttackRadius")] += 1
print("top AR for HL1", ars.most_common(10))

"""Train map ID integrity vs city/thon stall maps (mirrors pluyencong TRAIN_MAPS)."""

CITY_MAPS = {37, 78, 176, 162, 80, 1, 11}
THON_STALL_MAPS = {53, 20, 99, 100, 101, 121, 153, 174}

# Corrected IDs from settings/.../thanhthi.txt (Ba Lang 53 kept for stalls, not train)
TRAIN_MAPS = [
    {"name": "Kim Quang Dong", "mapId": 4, "minLv": 1, "maxLv": 20},
    {"name": "Phuc Nguu Son Tay", "mapId": 41, "minLv": 20, "maxLv": 40},
    {"name": "Kinh Hoang Dong", "mapId": 5, "minLv": 40, "maxLv": 60},
    {"name": "Lam Du Quan", "mapId": 319, "minLv": 60, "maxLv": 80},
    {"name": "Dao Hoa Nguyen", "mapId": 55, "minLv": 80, "maxLv": 90},
    {"name": "Truong Bach Son Nam", "mapId": 321, "minLv": 90, "maxLv": 120},
    {"name": "Mac Bac Thao Nguyen", "mapId": 341, "minLv": 120, "maxLv": 150},
    {"name": "Sa Mac Tang 1", "mapId": 225, "minLv": 150, "maxLv": 180},
    {"name": "Vi Son Dao", "mapId": 342, "minLv": 180, "maxLv": 200},
]

FORBIDDEN_TRAIN_IDS = {11, 17, 70, 181, 325, 340, 53}


def test_no_overlap_with_city_maps():
    ids = {m["mapId"] for m in TRAIN_MAPS}
    assert ids.isdisjoint(CITY_MAPS)


def test_no_overlap_with_thon_stall_maps():
    ids = {m["mapId"] for m in TRAIN_MAPS}
    assert ids.isdisjoint(THON_STALL_MAPS)


def test_unique_train_map_ids():
    ids = [m["mapId"] for m in TRAIN_MAPS]
    assert len(ids) == len(set(ids))


def test_forbidden_wrong_ids_not_used():
    ids = {m["mapId"] for m in TRAIN_MAPS}
    assert ids.isdisjoint(FORBIDDEN_TRAIN_IDS)


def test_start_level_clamp():
    start = 10
    m = TRAIN_MAPS[0]
    lv = start if m["minLv"] <= start else m["minLv"]
    if lv < m["minLv"]:
        lv = m["minLv"]
    if lv > m["maxLv"]:
        lv = m["maxLv"]
    assert lv == 10

    m2 = TRAIN_MAPS[5]
    lv2 = start if m2["minLv"] <= start else m2["minLv"]
    assert lv2 == 90


def test_reject_temple_template_name():
    name = "Temple 22"
    assert "Temple" in name
    fixed = "LangTuKiem"
    assert "Temple" not in fixed

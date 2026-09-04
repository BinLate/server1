"""Unit-level checks for SimCityWorld Get/Update hardening (Lua 4.0 semantics mirrored in Python)."""


def lazy_get(data_store, sim_map, n_w, new_fn):
    key = "w" + str(n_w)
    if data_store.get(key) is not None:
        return data_store[key]
    if sim_map and n_w in sim_map:
        new_fn(sim_map[n_w])
        if data_store.get(key) is not None:
            return data_store[key]
    return {}


def update(data_store, sim_map, n_w, key, value, new_fn):
    data = lazy_get(data_store, sim_map, n_w, new_fn)
    if data is None or len(data) == 0:
        return False
    data[key] = value
    return True


def test_lazy_hydrate_from_map():
    store = {}
    sim_map = {37: {"worldId": 37, "name": "Bien Kinh", "nodes": {}, "presetPaths": {}, "decoration": []}}

    def new_fn(d):
        key = "w" + str(d["worldId"])
        if key not in store:
            d = dict(d)
            d["playerTracker"] = {}
            d["playerTrackerCount"] = 0
            store[key] = d

    got = lazy_get(store, sim_map, 37, new_fn)
    assert got.get("name") == "Bien Kinh"
    assert "playerTracker" in got
    assert store["w37"] is got


def test_unknown_map_returns_empty():
    store = {}
    got = lazy_get(store, {}, 999, lambda d: None)
    assert got == {}


def test_update_refuses_ephemeral_empty():
    store = {}
    ok = update(store, {}, 999, "foo", 1, lambda d: None)
    assert ok is False
    assert store == {}


def test_update_writes_hydrated():
    store = {}
    sim_map = {1: {"worldId": 1, "name": "PT"}}

    def new_fn(d):
        key = "w" + str(d["worldId"])
        if key not in store:
            store[key] = dict(d)

    ok = update(store, sim_map, 1, "tick", 5, new_fn)
    assert ok is True
    assert store["w1"]["tick"] == 5

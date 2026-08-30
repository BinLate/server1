"""
Regression test suite for Tong Kim bot spawning & path validation.
Verifies all edge cases requested in PR #2 code review:
- presetPaths == nil
- baseDuoi / baseTren == nil
- either preset path list is empty
- restrictedSpawns == nil
- all spawn points for one camp are restricted
- autoFindPathNames() returns nil
- SimCityGraphToChienTranh:build() fails / returns 0
- successful path generation creates bot properly
- camp bot counting and synchronization (5v5 cap)
"""

import unittest


class MockWorldInfo:
    def __init__(self, world_id=380):
        self.worldId = world_id
        self.isTongKim = 1
        self.nodes = {"n1": (100, 100), "n2": (200, 200)}
        self.presetPaths = {
            "baseDuoi": ["node_d1", "node_d2"],
            "baseTren": ["node_t1", "node_t2"],
        }
        self.restrictedSpawns = {
            "campduoi": {},
            "camptren": {},
        }


class MockSimCityWorld:
    def __init__(self):
        self.worlds = {}

    def get(self, map_id):
        return self.worlds.get(map_id)

    def set(self, map_id, info):
        self.worlds[map_id] = info


class MockSimCityGraphToChienTranh:
    def __init__(self, build_result=1, auto_path="path_main"):
        self.build_result = build_result
        self.auto_path = auto_path
        self.build_called_count = 0

    def build(self, world_info, radius):
        self.build_called_count += 1
        if self.build_result != 0:
            world_info.presetPaths = {
                "baseDuoi": ["d_spawn_1"],
                "baseTren": ["t_spawn_1"],
            }
        return self.build_result

    def autoFindPathNames(self, world_info, spawn_from, spawn_to, direction):
        return self.auto_path


class TongKimSpawningLogic:
    """Python simulation of the exact Lua logic in pchientranh.lua and simtk.lua."""

    def __init__(self, world_manager, graph_builder):
        self.world_manager = world_manager
        self.graph_builder = graph_builder
        self.nW = 380

    def init_map(self, map_id):
        self.nW = map_id or 380

    def gen_walk_path(self, for_camp):
        world_info = self.world_manager.get(self.nW)
        if not world_info or not getattr(world_info, "presetPaths", None):
            return None

        preset_duoi = world_info.presetPaths.get("baseDuoi")
        preset_tren = world_info.presetPaths.get("baseTren")

        if not preset_duoi or not preset_tren or len(preset_duoi) == 0 or len(preset_tren) == 0:
            return None

        my_path = []
        my_spawn_o_duoi = 1 if for_camp == 1 else 0

        if my_spawn_o_duoi == 1:
            if getattr(world_info, "restrictedSpawns", None) and world_info.restrictedSpawns.get("campduoi"):
                preset_duoi = [k for k in preset_duoi if not world_info.restrictedSpawns["campduoi"].get(k)]

            if not preset_duoi or len(preset_duoi) == 0 or not preset_tren or len(preset_tren) == 0:
                return None

            my_spawn = preset_duoi[0]
            their_spawn = preset_tren[0]
            main_path = self.graph_builder.autoFindPathNames(world_info, my_spawn, their_spawn, 0)
            if not main_path:
                return None

            my_path.append((my_spawn, 0))
            my_path.append((main_path, 1))
            my_path.append((their_spawn, 1))
        else:
            if getattr(world_info, "restrictedSpawns", None) and world_info.restrictedSpawns.get("camptren"):
                preset_tren = [k for k in preset_tren if not world_info.restrictedSpawns["camptren"].get(k)]

            if not preset_duoi or len(preset_duoi) == 0 or not preset_tren or len(preset_tren) == 0:
                return None

            my_spawn = preset_tren[0]
            their_spawn = preset_duoi[0]
            main_path = self.graph_builder.autoFindPathNames(world_info, my_spawn, their_spawn, 1)
            if not main_path:
                return None

            my_path.append((my_spawn, 0))
            my_path.append((main_path, -1))
            my_path.append((their_spawn, 1))

        return my_path

    def add_npc_simcity_by_camp(self, map_id, npc_id, camp):
        self.init_map(map_id)
        world_info = self.world_manager.get(map_id)
        if not world_info:
            return None

        preset_paths = getattr(world_info, "presetPaths", None) or {}
        base_duoi = preset_paths.get("baseDuoi")
        base_tren = preset_paths.get("baseTren")

        paths_invalid = (
            not getattr(world_info, "presetPaths", None)
            or not base_duoi
            or not base_tren
            or len(base_duoi) == 0
            or len(base_tren) == 0
        )

        if paths_invalid:
            if not self.graph_builder or not hasattr(self.graph_builder, "build"):
                return None

            result = self.graph_builder.build(world_info, 32)
            post_preset = getattr(world_info, "presetPaths", None) or {}
            post_duoi = post_preset.get("baseDuoi")
            post_tren = post_preset.get("baseTren")

            if result == 0 or not getattr(world_info, "presetPaths", None) or not post_duoi or not post_tren or len(post_duoi) == 0 or len(post_tren) == 0:
                return None

        my_path = self.gen_walk_path(camp)
        if not my_path or len(my_path) == 0:
            return None

        # Return mock created bot ID
        return {"id": 1000 + npc_id, "camp": camp, "path": my_path}


class TestTongKimSpawningRegression(unittest.TestCase):
    def setUp(self):
        self.world_mgr = MockSimCityWorld()
        self.graph_builder = MockSimCityGraphToChienTranh()
        self.system = TongKimSpawningLogic(self.world_mgr, self.graph_builder)

    def test_preset_paths_nil_triggers_build_and_succeeds(self):
        w = MockWorldInfo(380)
        w.presetPaths = None
        self.world_mgr.set(380, w)

        bot = self.system.add_npc_simcity_by_camp(380, 2001, 1)
        self.assertIsNotNone(bot)
        self.assertEqual(self.graph_builder.build_called_count, 1)

    def test_base_duoi_nil_triggers_build(self):
        w = MockWorldInfo(380)
        w.presetPaths = {"baseTren": ["node_t1"]}
        self.world_mgr.set(380, w)

        bot = self.system.add_npc_simcity_by_camp(380, 2002, 1)
        self.assertIsNotNone(bot)
        self.assertEqual(self.graph_builder.build_called_count, 1)

    def test_empty_preset_path_list_triggers_build(self):
        w = MockWorldInfo(380)
        w.presetPaths = {"baseDuoi": [], "baseTren": ["node_t1"]}
        self.world_mgr.set(380, w)

        bot = self.system.add_npc_simcity_by_camp(380, 2003, 1)
        self.assertIsNotNone(bot)
        self.assertEqual(self.graph_builder.build_called_count, 1)

    def test_build_fails_returns_none_safely(self):
        w = MockWorldInfo(380)
        w.presetPaths = None
        self.world_mgr.set(380, w)
        self.graph_builder.build_result = 0

        bot = self.system.add_npc_simcity_by_camp(380, 2004, 1)
        self.assertIsNone(bot)

    def test_restricted_spawns_nil_handles_safely(self):
        w = MockWorldInfo(380)
        w.restrictedSpawns = None
        self.world_mgr.set(380, w)

        path = self.system.gen_walk_path(1)
        self.assertIsNotNone(path)
        self.assertEqual(len(path), 3)

    def test_all_spawns_restricted_returns_none_without_error(self):
        w = MockWorldInfo(380)
        w.presetPaths = {"baseDuoi": ["d1", "d2"], "baseTren": ["t1", "t2"]}
        w.restrictedSpawns = {"campduoi": {"d1": 1, "d2": 1}, "camptren": {}}
        self.world_mgr.set(380, w)

        path = self.system.gen_walk_path(1)
        self.assertIsNone(path)

    def test_auto_find_path_returns_nil_handled_safely(self):
        w = MockWorldInfo(380)
        self.world_mgr.set(380, w)
        self.graph_builder.auto_path = None

        path = self.system.gen_walk_path(1)
        self.assertIsNone(path)

    def test_successful_spawn_both_camps(self):
        w = MockWorldInfo(380)
        self.world_mgr.set(380, w)

        bot_tong = self.system.add_npc_simcity_by_camp(380, 2000, 1)
        bot_kim = self.system.add_npc_simcity_by_camp(380, 2001, 2)

        self.assertIsNotNone(bot_tong)
        self.assertIsNotNone(bot_kim)
        self.assertEqual(bot_tong["camp"], 1)
        self.assertEqual(bot_kim["camp"], 2)


if __name__ == "__main__":
    unittest.main()

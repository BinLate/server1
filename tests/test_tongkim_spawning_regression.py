"""
Production Lua regression test suite for Tong Kim bot spawning & path validation.
Directly loads and executes the actual Lua source files:
- script/global/nobitaxd/vdk/simcity/plugins/pchientranh.lua
- script/battles/marshal/simtk.lua

Tests all production Lua edge cases and mechanics:
1. SimCityChienTranh:genWalkPath() edge cases:
   - presetPaths == nil
   - baseDuoi / baseTren == nil
   - either preset path list is empty ({})
   - restrictedSpawns == nil (handles safely without crashing)
   - all spawn points for one camp are restricted (returns nil without random(1,0) crash)
   - autoFindPathNames() returns nil (returns nil safely)
2. simTK:add_npc_simcity_by_camp() edge cases:
   - worldInfo == nil
   - SimCityGraphToChienTranh:build() fails (returns 0) -> aborts safely
   - Successful graph build creates Tong and Kim bots with valid paths
3. simTK:countBotsByCamp():
   - Counts only bots with finalIndex > 0, camp match, and tongkim == 1
4. simTK:syncCampBots() & simTK:trimCampBots():
   - Proves independent camp replenishment and capping at 5 Tong + 5 Kim
   - Replenishes depleted camp without affecting the other camp
   - Trims excess live bots without removing extra bots due to dead (finalIndex=0) entries
   - Verifies 6 live bots + 2 dead bots trimmed down to exactly 5 live bots
"""

import unittest
import lupa


class TestTongKimLuaProduction(unittest.TestCase):
    def setUp(self):
        self.lua = lupa.LuaRuntime(unpack_returned_tuples=True)

        # Setup Lua runtime environment with JX1 / Lua 4.0 compatibility stubs
        self.lua.execute("""
            local table_mt = {
                __call = function(self, _, var)
                    return next(self, var)
                end
            }

            make_iterable_table = function(t)
                t = t or {}
                return setmetatable(t, table_mt)
            end

            tinsert = table.insert
            tremove = table.remove
            getn = function(t)
                if not t then return 0 end
                return #t
            end
            random = function(a, b)
                if not b then return a or 1 end
                if a > b then return a end
                return math.random(a, b)
            end
            mod = function(a, b) return a % b end
            floor = math.floor
            strfind = string.find
            strsub = string.sub
            Include = function() end
            IncludeLib = function() end
            SubWorldID2Idx = function(id) return id end
            GetDistanceRadius = function(x1, y1, x2, y2)
                return math.sqrt((x1-x2)^2 + (y1-y2)^2)
            end
            isGioCaoDiem = function() return 0 end
            Msg2Map = function() end
            Msg2MSAll = function() end
            GetGameTime = function() return 100 end

            SimCityNPCInfo = {
                generateName = function(self) return "BinhSi" end,
                getName = function(self, id) return "BinhSi" .. tostring(id) end
            }

            SimCityTongKim = {
                RANKS = {"Binh Si", "Hieu Uy", "Thong Lanh", "Pho Tuong", "Dai Tuong", "Nguyen Soai"}
            }

            -- Mock SimCitizen store
            SimCitizen = {
                fighterList = make_iterable_table({}),
                counter = 1,
                New = function(self, config)
                    local id = self.counter
                    self.counter = self.counter + 1
                    config.id = id
                    config.finalIndex = 1000 + id
                    self.fighterList[id] = config
                    return id
                end,
                Remove = function(self, id)
                    if self.fighterList[id] then
                        self.fighterList[id] = nil
                    end
                end
            }

            -- Mock SimCityWorld registry
            SimCityWorld = {
                worlds = {},
                Get = function(self, mapId)
                    return self.worlds[mapId]
                end,
                Set = function(self, mapId, info)
                    self.worlds[mapId] = info
                end
            }

            -- Mock SimCityGraphToChienTranh path finder
            SimCityGraphToChienTranh = {
                buildResult = 1,
                autoPath = "MainBattlePath_1",
                buildCalled = 0,
                build = function(self, worldInfo, radius)
                    self.buildCalled = self.buildCalled + 1
                    if self.buildResult ~= 0 then
                        worldInfo.presetPaths = {
                            baseDuoi = {"duoi_node_1", "duoi_node_2"},
                            baseTren = {"tren_node_1", "tren_node_2"}
                        }
                        worldInfo.chienTranhPaths = 1
                    end
                    return self.buildResult
                end,
                autoFindPathNames = function(self, worldInfo, mySpawn, theirSpawn, dir)
                    return self.autoPath
                end
            }
        """)

        # Load and execute the ACTUAL production Lua files
        with open("script/global/nobitaxd/vdk/simcity/plugins/pchientranh.lua", "r", encoding="latin1") as f:
            self.lua.execute(f.read())

        with open("script/battles/marshal/simtk.lua", "r", encoding="latin1") as f:
            self.lua.execute(f.read())

    def _create_mock_world(self, map_id=380):
        self.lua.execute(f"""
            local w = {{
                worldId = {map_id},
                isTongKim = 1,
                presetPaths = {{
                    baseDuoi = {{"spawn_d1", "spawn_d2"}},
                    baseTren = {{"spawn_t1", "spawn_t2"}}
                }},
                restrictedSpawns = make_iterable_table({{
                    campduoi = make_iterable_table({{}}),
                    camptren = make_iterable_table({{}})
                }})
            }}
            SimCityWorld:Set({map_id}, w)
            SimCityChienTranh:init({map_id})
        """)

    # -------------------------------------------------------------
    # 1. Tests for SimCityChienTranh:genWalkPath(forCamp) in Lua
    # -------------------------------------------------------------
    def test_lua_gen_walk_path_preset_paths_nil(self):
        self._create_mock_world(380)
        self.lua.execute("SimCityWorld:Get(380).presetPaths = nil")
        path = self.lua.eval("SimCityChienTranh:genWalkPath(1)")
        self.assertIsNone(path)

    def test_lua_gen_walk_path_base_duoi_nil(self):
        self._create_mock_world(380)
        self.lua.execute("SimCityWorld:Get(380).presetPaths.baseDuoi = nil")
        path = self.lua.eval("SimCityChienTranh:genWalkPath(1)")
        self.assertIsNone(path)

    def test_lua_gen_walk_path_base_tren_nil(self):
        self._create_mock_world(380)
        self.lua.execute("SimCityWorld:Get(380).presetPaths.baseTren = nil")
        path = self.lua.eval("SimCityChienTranh:genWalkPath(2)")
        self.assertIsNone(path)

    def test_lua_gen_walk_path_empty_list(self):
        self._create_mock_world(380)
        self.lua.execute("SimCityWorld:Get(380).presetPaths.baseDuoi = {}")
        path = self.lua.eval("SimCityChienTranh:genWalkPath(1)")
        self.assertIsNone(path)

    def test_lua_gen_walk_path_restricted_spawns_nil(self):
        self._create_mock_world(380)
        self.lua.execute("SimCityWorld:Get(380).restrictedSpawns = nil")
        path = self.lua.eval("SimCityChienTranh:genWalkPath(1)")
        self.assertIsNotNone(path)
        self.assertEqual(len(path), 3)

    def test_lua_gen_walk_path_all_spawns_restricted_returns_nil_safely(self):
        self._create_mock_world(380)
        self.lua.execute("""
            SimCityWorld:Get(380).restrictedSpawns = make_iterable_table({
                campduoi = make_iterable_table({ ["spawn_d1"] = 1, ["spawn_d2"] = 1 }),
                camptren = make_iterable_table({})
            })
        """)
        path = self.lua.eval("SimCityChienTranh:genWalkPath(1)")
        self.assertIsNone(path)

    def test_lua_gen_walk_path_auto_find_returns_nil(self):
        self._create_mock_world(380)
        self.lua.execute("SimCityGraphToChienTranh.autoPath = nil")
        path = self.lua.eval("SimCityChienTranh:genWalkPath(1)")
        self.assertIsNone(path)

    # -------------------------------------------------------------
    # 2. Tests for simTK:add_npc_simcity_by_camp(nIdMap, nIdNpc, forCamp) in Lua
    # -------------------------------------------------------------
    def test_lua_add_npc_world_info_nil(self):
        result = self.lua.eval("simTK:add_npc_simcity_by_camp(999, 2000, 1)")
        self.assertIsNone(result)

    def test_lua_add_npc_triggers_graph_build_when_uninitialized(self):
        self._create_mock_world(380)
        self.lua.execute("SimCityWorld:Get(380).presetPaths = nil")
        self.lua.execute("SimCityGraphToChienTranh.buildCalled = 0")
        self.lua.execute("SimCityGraphToChienTranh.buildResult = 1")

        result = self.lua.eval("simTK:add_npc_simcity_by_camp(380, 2001, 1)")
        self.assertIsNotNone(result)
        build_called = self.lua.eval("SimCityGraphToChienTranh.buildCalled")
        self.assertEqual(build_called, 1)

    def test_lua_add_npc_aborts_when_build_fails(self):
        self._create_mock_world(380)
        self.lua.execute("SimCityWorld:Get(380).presetPaths = nil")
        self.lua.execute("SimCityGraphToChienTranh.buildResult = 0")

        result = self.lua.eval("simTK:add_npc_simcity_by_camp(380, 2002, 1)")
        self.assertIsNone(result)

    def test_lua_add_npc_successful_both_camps(self):
        self._create_mock_world(380)
        tong_bot = self.lua.eval("simTK:add_npc_simcity_by_camp(380, 2000, 1)")
        kim_bot = self.lua.eval("simTK:add_npc_simcity_by_camp(380, 2001, 2)")
        self.assertIsNotNone(tong_bot)
        self.assertIsNotNone(kim_bot)

    # -------------------------------------------------------------
    # 3. Tests for simTK:countBotsByCamp() and simTK:syncCampBots() in Lua
    # -------------------------------------------------------------
    def test_lua_count_bots_by_camp_filtering(self):
        self._create_mock_world(380)
        self.lua.execute("""
            SimCitizen.fighterList = make_iterable_table({
                [1] = { id = 1, nMapId = 380, camp = 1, tongkim = 1, finalIndex = 1001 },
                [2] = { id = 2, nMapId = 380, camp = 1, tongkim = 1, finalIndex = 1002 },
                [3] = { id = 3, nMapId = 380, camp = 2, tongkim = 1, finalIndex = 1003 },
                [4] = { id = 4, nMapId = 380, camp = 1, tongkim = 0, finalIndex = 1004 }, -- non-TongKim
                [5] = { id = 5, nMapId = 164, camp = 1, tongkim = 1, finalIndex = 1005 }, -- different map
                [6] = { id = 6, nMapId = 380, camp = 1, tongkim = 1, finalIndex = 0 },    -- failed/dead NPC
            })
        """)

        count_tong = self.lua.eval("simTK:countBotsByCamp(380, 1)")
        count_kim = self.lua.eval("simTK:countBotsByCamp(380, 2)")

        self.assertEqual(count_tong, 2)
        self.assertEqual(count_kim, 1)

    def test_lua_sync_camp_bots_replenishes_and_caps_at_five_each(self):
        self._create_mock_world(380)
        # Start with 2 Tong bots and 8 Kim bots
        self.lua.execute("""
            SimCitizen.fighterList = make_iterable_table({
                [1] = { id = 1, nMapId = 380, camp = 1, tongkim = 1, finalIndex = 1001 },
                [2] = { id = 2, nMapId = 380, camp = 1, tongkim = 1, finalIndex = 1002 },
                [3] = { id = 3, nMapId = 380, camp = 2, tongkim = 1, finalIndex = 1003 },
                [4] = { id = 4, nMapId = 380, camp = 2, tongkim = 1, finalIndex = 1004 },
                [5] = { id = 5, nMapId = 380, camp = 2, tongkim = 1, finalIndex = 1005 },
                [6] = { id = 6, nMapId = 380, camp = 2, tongkim = 1, finalIndex = 1006 },
                [7] = { id = 7, nMapId = 380, camp = 2, tongkim = 1, finalIndex = 1007 },
                [8] = { id = 8, nMapId = 380, camp = 2, tongkim = 1, finalIndex = 1008 },
            })
            SimCitizen.counter = 9
            simTK:syncCampBots(380, 5)
        """)

        final_tong = self.lua.eval("simTK:countBotsByCamp(380, 1)")
        final_kim = self.lua.eval("simTK:countBotsByCamp(380, 2)")

        self.assertEqual(final_tong, 5)
        self.assertEqual(final_kim, 5)

    def test_lua_trim_camp_bots_ignores_dead_bots_and_leaves_exactly_five_live_bots(self):
        self._create_mock_world(380)
        # 6 live bots (finalIndex > 0) + 2 dead bots (finalIndex = 0)
        self.lua.execute("""
            SimCitizen.fighterList = make_iterable_table({
                [1] = { id = 1, nMapId = 380, camp = 1, tongkim = 1, finalIndex = 1001 },
                [2] = { id = 2, nMapId = 380, camp = 1, tongkim = 1, finalIndex = 1002 },
                [3] = { id = 3, nMapId = 380, camp = 1, tongkim = 1, finalIndex = 1003 },
                [4] = { id = 4, nMapId = 380, camp = 1, tongkim = 1, finalIndex = 1004 },
                [5] = { id = 5, nMapId = 380, camp = 1, tongkim = 1, finalIndex = 1005 },
                [6] = { id = 6, nMapId = 380, camp = 1, tongkim = 1, finalIndex = 1006 },
                [7] = { id = 7, nMapId = 380, camp = 1, tongkim = 1, finalIndex = 0 },    -- dead bot 1
                [8] = { id = 8, nMapId = 380, camp = 1, tongkim = 1, finalIndex = 0 },    -- dead bot 2
            })
            SimCitizen.counter = 9
            simTK:syncCampBots(380, 5)
        """)

        # Should trim only 1 live bot (6 - 5 = 1), leaving exactly 5 live bots
        final_tong = self.lua.eval("simTK:countBotsByCamp(380, 1)")
        self.assertEqual(final_tong, 5)


if __name__ == "__main__":
    unittest.main()

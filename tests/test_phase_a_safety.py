import unittest
import os
import re
import lupa
from lupa import LuaRuntime

class TestPhaseASafety(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        mock_env = """
        local function make_iter(t)
            return setmetatable(t or {}, {
                __call = function(tbl, state, var)
                    return next(tbl, var)
                end
            })
        end
        make_iterable_table = make_iter

        math.randomseed(12345)
        random = function(a, b)
            if not b then
                if not a or a <= 0 then return 0 end
                return math.random(1, a)
            end
            if a == b then return a end
            if a > b then return a end
            return a + math.random(0, b - a)
        end

        randomRange = function(arr, range)
            range = range or 4
            local rx = (arr[1] or 0) + random(-range, range)
            local ry = (arr[2] or 0) + random(-range, range)
            return {rx, ry}
        end

        floor = math.floor
        abs = math.abs
        sqrt = math.sqrt
        getn = function(t) return (t and table.getn and table.getn(t)) or (t and #t) or 0 end
        tinsert = table.insert
        tremove = table.remove
        format = string.format
        strsub = string.sub
        strfind = string.find
        mod = math.fmod

        objCopy = function(orig)
            local copy
            if type(orig) == 'table' then
                copy = make_iter({})
                for orig_key, orig_value in pairs(orig) do
                    copy[orig_key] = orig_value
                end
            else
                copy = orig
            end
            return copy
        end

        Include = function(path) end
        IncludeLib = function(lib) end
        Msg2Player = function(msg) end
        Msg2Map = function(map, msg) end
        Say = function(msg) end
        PutMessage = function(msg) end
        AddGlobalCountNews = function(msg, mode) end
        SetMissionV = function(a, b) end
        GetMissionV = function(a) return 0 end
        BT_SetData = function(a, b) end
        GetGameTime = function() return 1000 end
        -- JX1 engine contract: GetWorldPos returns (mapId, x, y)
        GetWorldPos = function() return 380, 1500, 3000 end
        GetCurCamp = function() return 1 end
        DelNpc = function(idx) end
        GetNpcPos = function(idx) return 3200, 3200, 380 end
        SetNpcRideHorse = function(idx, ride) end
        SetNpcLevel = function(idx, lv) end
        GetNpcKind = function(idx) return 0 end
        SetNpcKind = function(idx, k) end
        SetNpcCurCamp = function(idx, camp) end
        SetNpcParam = function(idx, p, v) end
        GetNpcName = function(idx) return "Bot" end
        SetNpcName = function(idx, n) end
        SetNpcScript = function(idx, s) end
        SetNpcFightState = function(idx, st) end
        SetNpcActiveRegion = function(idx, r) end
        SetNpcAI = function(idx, ai) end
        SetNpcDmgExtra = function(...) end
        SetNpcAuraSkill = function(...) end
        NPCINFO_GetNpcCurrentLife = function(idx) return 1000 end
        NPCINFO_GetNpcCurrentMaxLife = function(idx) return 1000 end
        NPCINFO_SetNpcCurrentLife = function(idx, hp) end
        NPCINFO_SetNpcCurrentMaxLife = function(idx, hp) end
        SetNpcAtkSpeed = function(idx, spd) end
        NpcRun = function(idx, x, y) end
        NpcWalk = function(idx, x, y) end
        NpcChat = function(idx, msg) end
        NpcCastSkill = function(idx, sk, lv, x, y) end
        isGioCaoDiem = function() return 0 end
        isCuoiTuan = function() return 0 end
        nodeNameToCoords = function(name) return 100, 100 end
        SubWorldID2Idx = function(id) return id end
        AddNpc = function(id, lv, mapIdx, x, y, a, name, b) return 1001 end
        AddNpcEx = function(...) return 1001 end
        GetDistanceRadius = function(x1, y1, x2, y2)
            local dx = (x1 or 0) - (x2 or 0)
            local dy = (y1 or 0) - (y2 or 0)
            return math.sqrt(dx * dx + dy * dy)
        end
        """
        self.lua.execute(mock_env)

    def load_lua_file(self, rel_path):
        with open(rel_path, 'r', encoding='latin1') as f:
            content = f.read()
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        return self.lua.execute(content)

    def init_simcity_environment(self):
        self.load_lua_file('script/global/nobitaxd/vdk/simcity/config.lua')
        self.load_lua_file('script/global/nobitaxd/vdk/simcity/libs/common.lua')
        
        self.lua.execute("""
        local defaultFac = { normalCast = { {318, 20} }, needCast = {}, noCast = {} }
        SimCityPhai = make_iterable_table({
            id2phai = make_iterable_table({}),
            thieulam = defaultFac,
            thienvuong = defaultFac,
            duongmon = defaultFac,
            ngudoc = defaultFac,
            ngami = defaultFac,
            thuyyen = defaultFac,
            caibang = defaultFac,
            tianren = defaultFac,
            vodang = defaultFac,
            conlon = defaultFac
        })

        SimCityTongKim = {
            RANKS = { "Binh Si", "Hieu Uy", "Thong Lanh", "Pho Tuong", "Dai Tuong", "Nguyen Soai" }
        }

        local defaultWorld380 = {
            worldId = 380,
            name = "TongKim_380",
            isTongKim = 1,
            showName = 1,
            allowFighting = 1,
            showFightingArea = 0,
            presetPaths = {
                baseDuoi = { "spawn_s1", "spawn_s2" },
                baseTren = { "spawn_j1", "spawn_j2" },
                main_path_1 = { "spawn_s1", "mid1", "mid2", "spawn_j1" },
                spawn_s1 = { "spawn_s1", "mid1" },
                spawn_s2 = { "spawn_s2", "mid1" },
                spawn_j1 = { "spawn_j1", "mid2" },
                spawn_j2 = { "spawn_j2", "mid2" }
            },
            restrictedSpawns = { campduoi = {}, camptren = {} },
            graphEdges = { 1 },
            nodes = {
                spawn_s1 = { x = 100, y = 100, linkedNodes = {"mid1"} },
                spawn_s2 = { x = 105, y = 105, linkedNodes = {"mid1"} },
                spawn_j1 = { x = 200, y = 200, linkedNodes = {"mid2"} },
                spawn_j2 = { x = 205, y = 205, linkedNodes = {"mid2"} },
                mid1 = { x = 150, y = 150, linkedNodes = {"mid2"} },
                mid2 = { x = 160, y = 160, linkedNodes = {"spawn_j1"} }
            }
        }

        local defaultWorld53 = {
            worldId = 53,
            name = "BaLangHuyen_53",
            isTongKim = 0,
            showName = 1,
            allowFighting = 1,
            showFightingArea = 0,
            presetPaths = {
                baseDuoi = { "spawn_s1", "spawn_s2" },
                baseTren = { "spawn_j1", "spawn_j2" },
                main_path_1 = { "spawn_s1", "mid1", "mid2", "spawn_j1" },
                spawn_s1 = { "spawn_s1", "mid1" },
                spawn_s2 = { "spawn_s2", "mid1" },
                spawn_j1 = { "spawn_j1", "mid2" },
                spawn_j2 = { "spawn_j2", "mid2" }
            },
            restrictedSpawns = { campduoi = {}, camptren = {} },
            graphEdges = { 1 },
            nodes = {
                spawn_s1 = { x = 100, y = 100, linkedNodes = {"mid1"} },
                spawn_s2 = { x = 105, y = 105, linkedNodes = {"mid1"} },
                spawn_j1 = { x = 200, y = 200, linkedNodes = {"mid2"} },
                spawn_j2 = { x = 205, y = 205, linkedNodes = {"mid2"} },
                mid1 = { x = 150, y = 150, linkedNodes = {"mid2"} },
                mid2 = { x = 160, y = 160, linkedNodes = {"spawn_j1"} }
            }
        }

        SimCityWorld = {
            data = {
                [380] = defaultWorld380,
                [53] = defaultWorld53
            }
        }
        function SimCityWorld:Get(mapId)
            return self.data[mapId]
        end

        SimCityNPCInfo = {
            ALLNPCs_INFO_COUNT = 100,
            getName = function(self, id) return "Bot_" .. tostring(id) end,
            generateName = function(self) return "Bot_NgoaiTrang" end,
            IsValidFighter = function(self, id) return 1 end,
            notFightingChar = function(self, id) return 0 end,
            getSpeed = function(self, id) return 10 end,
            getPoolByCap = function(self, cap) return { 2000, 2001, 2002, 2003, 2004 } end
        }

        SimCityGraphToChienTranh = {
            autoFindPathNames = function(self, worldInfo, startNode, endNode, dir)
                return "main_path_1"
            end,
            build = function(self, worldInfo, size)
                worldInfo.graphEdges = { 1 }
                worldInfo.chienTranhPaths = 1
                return 1
            end
        }
        """)

        self.load_lua_file('script/global/nobitaxd/vdk/simcity/components/sim.movement.lua')
        self.load_lua_file('script/global/nobitaxd/vdk/simcity/components/sim.entity.lua')
        self.load_lua_file('script/global/nobitaxd/vdk/simcity/components/sim.fight.lua')
        self.load_lua_file('script/global/nobitaxd/vdk/simcity/components/sim.fun.lua')
        self.load_lua_file('script/global/nobitaxd/vdk/simcity/components/sim.gear.lua')
        self.load_lua_file('script/global/nobitaxd/vdk/simcity/components/sim.party.lua')
        self.load_lua_file('script/global/nobitaxd/vdk/simcity/components/sim.progression.lua')
        self.load_lua_file('script/global/nobitaxd/vdk/simcity/components/sim.timer.lua')
        self.load_lua_file('script/global/nobitaxd/vdk/simcity/components/sim.core.lua')
        self.load_lua_file('script/global/nobitaxd/vdk/simcity/class/sim_citizen.lua')
        self.load_lua_file('script/global/nobitaxd/vdk/simcity/plugins/pchientranh.lua')
        self.load_lua_file('script/battles/marshal/simtk.lua')
        self.load_lua_file('script/global/nobitaxd/vdk/simcity/plugins/pluyencong.lua')

        self.lua.execute("""
        SimCitizen.fighterList = make_iterable_table(SimCitizen.fighterList or {})
        """)

    def test_centralized_configuration_values(self):
        self.load_lua_file('script/global/nobitaxd/vdk/simcity/config.lua')
        g = self.lua.globals()
        self.assertEqual(g.TONGKIM_SIMBOT_PER_CAMP, 5)
        self.assertEqual(g.TONGKIM_SIMBOT_TOTAL, 10)
        self.assertEqual(g.TRAIN_BOT_MAX_PER_MAP, 25)
        self.assertEqual(g.TRAIN_BOT_GLOBAL_BUDGET, 200)
        self.assertEqual(g.SIMBOT_MAX_LEVEL, 200)
        self.assertEqual(g.AOI_SCAN_INTERVAL, 15)
        self.assertEqual(g.AOI_HIBERNATE_TIMEOUT, 120)

    def test_tongkim_5v5_sync_and_trim_invariants(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local mapId = 380
        simTK:ensureBots(mapId)
        local tongCount = simTK:countBotsByCamp(mapId, 1)
        local kimCount = simTK:countBotsByCamp(mapId, 2)
        local totalCount = SimCityChienTranh:countMap(mapId)

        -- Repeated call must remain idempotent
        simTK:ensureBots(mapId)
        local tongCount2 = simTK:countBotsByCamp(mapId, 1)
        local kimCount2 = simTK:countBotsByCamp(mapId, 2)
        local totalCount2 = SimCityChienTranh:countMap(mapId)

        return tongCount, kimCount, totalCount, tongCount2, kimCount2, totalCount2
        """)
        tong1, kim1, total1, tong2, kim2, total2 = res
        self.assertEqual(tong1, 5)
        self.assertEqual(kim1, 5)
        self.assertEqual(total1, 10)
        self.assertEqual(tong2, 5)
        self.assertEqual(kim2, 5)
        self.assertEqual(total2, 10)

    def test_legacy_pchientranh_redirects_in_tongkim(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        SimCityChienTranh:init(380)
        
        -- Call legacy phe_quanbinh
        SimCityChienTranh:phe_quanbinh()
        local c1 = SimCityChienTranh:countMap(380)
        local t1 = simTK:countBotsByCamp(380, 1)
        local k1 = simTK:countBotsByCamp(380, 2)

        -- Call legacy phe_tudo
        SimCityChienTranh:phe_tudo(2000, 50, 0)
        local c2 = SimCityChienTranh:countMap(380)

        -- Call legacy phe_tudo_xe
        SimCityChienTranh:phe_tudo_xe(2000, 50, 0)
        local c3 = SimCityChienTranh:countMap(380)

        return c1, t1, k1, c2, c3
        """)
        c1, t1, k1, c2, c3 = res
        self.assertEqual(c1, 10)
        self.assertEqual(t1, 5)
        self.assertEqual(k1, 5)
        self.assertEqual(c2, 10)
        self.assertEqual(c3, 10)

    def test_get_player_count_in_map(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        -- JX1 standard: player positions as (mapId, x, y)
        local playerPositions = {
            [1] = { 53, 1000, 2000 },
            [2] = { 53, 1200, 2200 },
            [3] = { 380, 1500, 3000 }
        }
        GetPlayerCount = function() return 3 end
        CallPlayerFunction = function(pIdx, fn)
            local pos = playerPositions[pIdx]
            return pos[1], pos[2], pos[3]
        end

        local count53 = SimCityLuyenCong:GetPlayerCountInMap(53)
        local count380 = SimCityLuyenCong:GetPlayerCountInMap(380)
        local count999 = SimCityLuyenCong:GetPlayerCountInMap(999)

        return count53, count380, count999
        """)
        c53, c380, c999 = res
        self.assertEqual(c53, 2)
        self.assertEqual(c380, 1)
        self.assertEqual(c999, 0)

    def test_dynamic_aoi_idempotency_and_budget(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        SimCityLuyenCong:init()
        
        -- Spawn for map 1 (Ba Lang Huyen, count=15)
        SimCityLuyenCong:spawnForMap(1)
        local mapId = SimCityLuyenCong.TRAIN_MAPS[1].mapId
        local count1 = SimCityLuyenCong:countBotsInMap(mapId)

        -- Repeated call to spawnForMap should NOT double count
        SimCityLuyenCong:spawnForMap(1)
        local count2 = SimCityLuyenCong:countBotsInMap(mapId)

        -- Hibernate should clear map
        SimCityLuyenCong:hibernateMap(mapId)
        local count3 = SimCityLuyenCong:countBotsInMap(mapId)

        return count1, count2, count3
        """)
        count1, count2, count3 = res
        self.assertEqual(count1, 15)
        self.assertEqual(count2, 15)
        self.assertEqual(count3, 0)

    def test_aoi_atick_lifecycle_replenish_and_hibernate(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        SimCityLuyenCong:init()
        local mapId = SimCityLuyenCong.TRAIN_MAPS[1].mapId -- Ba Lang Huyen (53), target=15

        -- Mock player on map 53: (mapId, x, y)
        GetPlayerCount = function() return 1 end
        CallPlayerFunction = function(pIdx, fn) return 53, 1000, 2000 end

        local simTime = 100
        GetGameTime = function() return simTime end

        -- 1. First ATick spawns 15 bots
        SimCityLuyenCong:ATick()
        local initialCount = SimCityLuyenCong:countBotsInMap(mapId)

        -- 2. Simulate 5 bots dying/being removed
        local removed = 0
        for id, bot in pairs(SimCitizen.fighterList) do
            if bot.mode == "train" and bot.nMapId == mapId and removed < 5 then
                SimCitizen:Remove(id)
                removed = removed + 1
            end
        end
        local countAfterKill = SimCityLuyenCong:countBotsInMap(mapId)

        -- 3. Next ATick (player still present) replenishes back to 15
        simTime = simTime + 20
        SimCityLuyenCong:ATick()
        local countAfterReplenish = SimCityLuyenCong:countBotsInMap(mapId)

        -- 4. Player leaves map (count = 0)
        CallPlayerFunction = function(pIdx, fn) return 999, 1000, 2000 end

        -- Advance time within hibernate timeout (e.g. 50s < 120s) -> should NOT hibernate yet
        simTime = simTime + 50
        SimCityLuyenCong:ATick()
        local countBeforeHibernate = SimCityLuyenCong:countBotsInMap(mapId)

        -- Advance time past hibernate timeout (e.g. 150s >= 120s) -> should hibernate
        simTime = simTime + 100
        SimCityLuyenCong:ATick()
        local countAfterHibernate = SimCityLuyenCong:countBotsInMap(mapId)

        return initialCount, countAfterKill, countAfterReplenish, countBeforeHibernate, countAfterHibernate
        """)
        c_init, c_kill, c_rep, c_before_hib, c_after_hib = res
        self.assertEqual(c_init, 15)
        self.assertEqual(c_kill, 10)
        self.assertEqual(c_rep, 15)
        self.assertEqual(c_before_hib, 15)
        self.assertEqual(c_after_hib, 0)

    def test_sim_citizen_transactional_rollback(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local initialTotal = SimCitizen.totalFighters
        local initialCounter = SimCitizen.counter
        local initialRemoved = getn(SimCitizen.removedIds)

        -- 1. Invalid mapId (worldInfo == nil)
        local res1 = SimCitizen:New({ nMapId = 999999, nNpcId = 100 })
        local total1 = SimCitizen.totalFighters

        -- 2. Movement resetPos returns 0 (force failure)
        local orig_reset = SimMovement.Citizen.resetPos
        SimMovement.Citizen.resetPos = function() return 0 end
        local res2 = SimCitizen:New({ nMapId = 380, nNpcId = 100, faction = "thieulam" })
        local total2 = SimCitizen.totalFighters
        SimMovement.Citizen.resetPos = orig_reset

        -- 3. Entity CreateChar returns 0 (force failure)
        local orig_addnpc = AddNpcEx
        AddNpcEx = function(...) return 0 end
        local res3 = SimCitizen:New({ nMapId = 380, nNpcId = 100, faction = "thieulam" })
        local total3 = SimCitizen.totalFighters
        AddNpcEx = orig_addnpc

        -- 4. Successful creation
        local validId = SimCitizen:New({ nMapId = 380, nNpcId = 100, faction = "thieulam" })
        local total4 = SimCitizen.totalFighters

        -- 5. Remove verification
        SimCitizen:Remove(validId)
        local total5 = SimCitizen.totalFighters

        return res1 == nil, total1 == initialTotal, res2 == nil, total2 == initialTotal, res3 == nil, total3 == initialTotal, validId ~= nil, total4 == initialTotal + 1, total5 == initialTotal
        """)
        r1_nil, t1_ok, r2_nil, t2_ok, r3_nil, t3_ok, v_ok, t4_ok, t5_ok = res
        self.assertTrue(r1_nil)
        self.assertTrue(t1_ok)
        self.assertTrue(r2_nil)
        self.assertTrue(t2_ok)
        self.assertTrue(r3_nil)
        self.assertTrue(t3_ok)
        self.assertTrue(v_ok)
        self.assertTrue(t4_ok)
        self.assertTrue(t5_ok)

if __name__ == '__main__':
    unittest.main()

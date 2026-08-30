import unittest
import os
import re
import shutil
import lupa
from lupa import LuaRuntime

class TestPhaseBProgression(unittest.TestCase):
    def setUp(self):
        os.makedirs("save/simcity", exist_ok=True)
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.globals().os_replace = os.replace
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
        max = math.max
        min = math.min
        getn = function(t) return (t and table.getn and table.getn(t)) or (t and #t) or 0 end
        tinsert = table.insert
        tremove = table.remove
        format = string.format
        strsub = string.sub
        strlen = string.len
        strfind = string.find
        gsub = string.gsub
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
        GetNpcName = function(idx) return _G_NPC_NAMES[idx] or "Bot" end
        SetNpcName = function(idx, n) end
        SetNpcScript = function(idx, s) end
        SetNpcFightState = function(idx, st) end
        SetNpcActiveRegion = function(idx, r) end
        SetNpcAI = function(idx, ai) end
        SetNpcDmgExtra = function(...) end
        SetNpcAuraSkill = function(...) end
        _G_MOCK_HP = {}
        NPCINFO_GetNpcCurrentLife = function(idx) return _G_MOCK_HP[idx] or 5000 end
        NPCINFO_GetNpcCurrentMaxLife = function(idx) return 5000 end
        NPCINFO_SetNpcCurrentLife = function(idx, hp) _G_MOCK_HP[idx] = hp end
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
        _G_NPC_NAMES = {}
        AddNpc = function(id, lv, mapIdx, x, y, a, name, b) _G_NPC_NAMES[1001] = name; return 1001 end
        AddNpcEx = function(id, lv, series, mapIdx, x, y, a, name, b) _G_NPC_NAMES[1001] = name; return 1001 end
        GetDistanceRadius = function(x1, y1, x2, y2)
            local dx = (x1 or 0) - (x2 or 0)
            local dy = (y1 or 0) - (y2 or 0)
            return math.sqrt(dx * dx + dy * dy)
        end

        openfile = function(path, mode)
            return io.open(path, mode)
        end
        closefile = function(f)
            if f then f:close() end
        end
        read = function(f, mode)
            if f then return f:read(mode) end
            return nil
        end
        write = function(f, str)
            if f then f:write(str) end
        end
        renamefile = function(oldp, newp)
            if os_replace then
                local ok, err = pcall(os_replace, oldp, newp)
                if ok then return 1 else return nil, err end
            end
            local ok, err = os.rename(oldp, newp)
            if ok then return 1 else return nil, err end
        end
        """
        self.lua.execute(mock_env)

    def tearDown(self):
        if os.path.exists("save/simcity"):
            shutil.rmtree("save/simcity", ignore_errors=True)

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

        local defaultWorld11 = {
            worldId = 11,
            name = "PhucNguuSon_11",
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
                [53] = defaultWorld53,
                [11] = defaultWorld11
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

    def test_level_cap_200_exp_progression(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local exp100 = SimProgression:GetExpRequired(100)
        local exp150 = SimProgression:GetExpRequired(150)
        local exp200 = SimProgression:GetExpRequired(200)

        local bot = { level = 149, nExp = 0, faction = "thieulam" }
        local req149 = SimProgression:GetExpRequired(149)
        SimProgression:AddExp(bot, req149)
        local lv_150 = bot.level

        local req150 = SimProgression:GetExpRequired(150)
        SimProgression:AddExp(bot, req150)
        local lv_151 = bot.level

        -- Test level 199 -> 200
        bot.level = 199
        bot.nExp = 0
        local req199 = SimProgression:GetExpRequired(199)
        SimProgression:AddExp(bot, req199)
        local lv_200 = bot.level

        -- Bot at cap 200 must not exceed 200
        SimProgression:AddExp(bot, 1000000000)
        local lv_cap = bot.level

        return exp100, exp150, exp200, lv_150, lv_151, lv_200, lv_cap
        """)
        exp100, exp150, exp200, lv_150, lv_151, lv_200, lv_cap = res
        self.assertEqual(exp100, 210000000)
        self.assertGreater(exp150, exp100)
        self.assertGreater(exp200, exp150)
        self.assertEqual(lv_150, 150)
        self.assertEqual(lv_151, 151)
        self.assertEqual(lv_200, 200)
        self.assertEqual(lv_cap, 200)

    def test_skill_range_and_horselimit_semantics(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        -- Dat Ma Do Giang (318): Bo chien (HorseLimit = 0)
        local horse_318 = SimProgression:CanCastOnHorse(318)
        -- Vo Tuong Tram (321): Ky chien (HorseLimit = 1)
        local horse_321 = SimProgression:CanCastOnHorse(321)

        -- Attack Radius lookup
        local radTiles_melee = SimProgression:GetSkillAttackRadiusTiles(318) -- Dat Ma Do Giang (90px -> 2 tiles)
        local radTiles_range = SimProgression:GetSkillAttackRadiusTiles(302) -- Bao Vu Le Hoa (450px -> 14 tiles)

        local isMelee_318 = SimProgression:IsMeleeSkill(318)
        local isMelee_302 = SimProgression:IsMeleeSkill(302)

        return horse_318 == 0, horse_321 == 1, radTiles_melee, radTiles_range, isMelee_318 == true, isMelee_302 == false
        """)
        h318, h321, r_melee, r_range, m318, m302 = res
        self.assertTrue(h318)
        self.assertTrue(h321)
        self.assertEqual(r_melee, 2)
        self.assertEqual(r_range, 14)
        self.assertTrue(m318)
        self.assertTrue(m302)

    def test_gear_tiers_and_damage_gated_leech(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local tier_50 = SimGear:GetTierByLevel(50)
        local tier_150 = SimGear:GetTierByLevel(150)
        local tier_180 = SimGear:GetTierByLevel(180)

        local bot = {
            finalIndex = 1001,
            level = 150,
            maxHP = 5000,
            lastHP = 3000,
            virtualGear = { tier = 11 }
        }
        _G_MOCK_HP[1001] = 3000

        -- 1. Leech with valid target (targetIdx > 0)
        SimGear:ApplyCombatLeech(bot, 1002, "player")
        local hpAfterValid = _G_MOCK_HP[1001]

        -- 2. Leech with invalid target (targetIdx == 0) -> must not leech
        _G_MOCK_HP[1001] = 3000
        bot.lastHP = 3000
        SimGear:ApplyCombatLeech(bot, 0, "player")
        local hpAfterInvalid = _G_MOCK_HP[1001]

        return tier_50, tier_150, tier_180, hpAfterValid >= 3000, hpAfterInvalid == 3000
        """)
        t50, t150, t180, valid_ok, invalid_ok = res
        self.assertEqual(t50, 5)
        self.assertEqual(t150, 11)
        self.assertEqual(t180, 12)
        self.assertTrue(valid_ok)
        self.assertTrue(invalid_ok)

    def test_crash_safe_roster_persistence(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        -- Name sanitization test
        local dirtyName = "Bot\\nName|With/Traversal..\\0"
        local cleanName = SimProgression:SanitizeName(dirtyName)

        -- Save roster
        local mapId = 53
        local testRoster = {
            { szName = "KiemMa99", level = 125, nExp = 45000, faction = "vodang", series = 3, weaponBranch = "kiem", nNpcId = 105, camp = 0, personality = "aggressive" },
            { szName = "DocCo99", level = 150, nExp = 90000, faction = "thieulam", series = 1, weaponBranch = "dao", nNpcId = 106, camp = 5, personality = "cautious" }
        }

        local saveOk = SimProgression:SaveTrainBots(mapId, testRoster)
        local loadedRoster = SimProgression:LoadTrainBots(mapId)

        local count = getn(loadedRoster)
        local bot1 = loadedRoster[1]
        local bot2 = loadedRoster[2]

        return cleanName, saveOk >= 1, count, bot1.szName, bot1.level, bot1.faction, bot1.personality, bot2.szName, bot2.level, bot2.camp
        """)
        cleanName, saveOk, count, b1_name, b1_lv, b1_fac, b1_pers, b2_name, b2_lv, b2_camp = res
        self.assertEqual(cleanName, "BotNameWithTraversal")
        self.assertTrue(saveOk)
        self.assertEqual(count, 2)
        self.assertEqual(b1_name, "KiemMa99")
        self.assertEqual(b1_lv, 125)
        self.assertEqual(b1_fac, "vodang")
        self.assertEqual(b1_pers, "aggressive")
        self.assertEqual(b2_name, "DocCo99")
        self.assertEqual(b2_lv, 150)
        self.assertEqual(b2_camp, 5)

    def test_aoi_hibernation_roster_snapshot_and_migration(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        SimCityLuyenCong:init()
        local map1 = SimCityLuyenCong.TRAIN_MAPS[1].mapId -- 53 (Ba Lang Huyen, minLv=1, maxLv=20)
        local map2 = SimCityLuyenCong.TRAIN_MAPS[2].mapId -- 11 (Phuc Nguu Son, minLv=20, maxLv=40)

        -- 1. Spawn map 1
        SimCityLuyenCong:spawnForMap(1)
        local initialCount = SimCityLuyenCong:countBotsInMap(map1)

        -- 2. Level up one bot in map 1 to level 25 (> 20 -> should trigger migration to map 2 upon hibernation)
        for id, bot in pairs(SimCitizen.fighterList) do
            if bot.mode == "train" and bot.nMapId == map1 then
                bot.level = 25
                bot.szName = "MigratedHero"
                break
            end
        end

        -- 3. Hibernate Map 1 -> should save persistent roster and migrate the level 25 bot to Map 2's roster
        SimCityLuyenCong:hibernateMap(map1)
        local countAfterHib = SimCityLuyenCong:countBotsInMap(map1)

        -- Check Map 2 loaded roster
        local map2Roster = SimProgression:LoadTrainBots(map2)
        local map2MigratedCount = getn(map2Roster)
        local migratedName = (map2MigratedCount > 0) and map2Roster[1].szName or ""
        local migratedLv = (map2MigratedCount > 0) and map2Roster[1].level or 0

        -- 4. Spawn Map 2 -> should awaken with the migrated bot
        SimCityLuyenCong:spawnForMap(2)
        local map2BotCount = SimCityLuyenCong:countBotsInMap(map2)

        return initialCount, countAfterHib == 0, map2MigratedCount > 0, migratedName, migratedLv, map2BotCount
        """)
        init_cnt, hib_ok, mig_ok, mig_name, mig_lv, map2_cnt = res
        self.assertGreater(init_cnt, 0)
        self.assertTrue(hib_ok)
        self.assertTrue(mig_ok)
        self.assertEqual(mig_name, "MigratedHero")
        self.assertEqual(mig_lv, 25)
        self.assertGreater(map2_cnt, 0)

    def test_npc_target_combat_leech_invocation(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local targetIdxPassed = nil
        local targetTypePassed = nil
        SimGear.ApplyCombatLeech = function(self, tbNpc, targetIdx, targetType)
            targetIdxPassed = targetIdx
            targetTypePassed = targetType
        end

        local tbNpc = {
            finalIndex = 1001,
            faction = "vodang",
            weaponBranch = "kiem",
            level = 100,
            nMapId = 53,
            series = 3,
            mode = "train",
            ngoaitrang = 1,
            horse = 0,
            tick_breath = 100,
            tick_canCast = 0,
            isFighting = 1,
            goX32 = 1000,
            goY32 = 1000
        }

        GetNpcAroundNpcList = function(idx, radius)
            return { 2002 } -- Found NPC enemy 2002
        end
        IsPlayer = function(idx) return 0 end
        NPCINFO_GetNpcRelation = function(a, b) return 0 end -- 0 = enemy
        GetNpcPos = function(idx) return 1020, 1020 end
        NpcCastSkill = function(...) return 1 end

        local mockFightSys = {
            IsPlayerEnemyAround = function(self, inst, npc) return 0 end,
            IsNpcEnemyAround = function(self, inst, npc) return 2002 end,
            SetNpcEnemyTarget = function(self, inst, npc, target) end
        }
        execCastNormalSkill(mockFightSys, nil, tbNpc)
        return targetIdxPassed, targetTypePassed
        """)
        target_idx, target_type = res
        self.assertEqual(target_idx, 2002)
        self.assertEqual(target_type, "npc")

    def test_crash_safe_roster_failure_path_preserves_old_data(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local mapId = 53
        local initialRoster = {
            { szName = "OldHero1", level = 100, nExp = 1000, faction = "thieulam", series = 1, weaponBranch = "dao", nNpcId = 101, camp = 0, personality = "balanced" }
        }
        -- 1. Initial valid save
        local initialSaveOk = SimProgression:SaveTrainBots(mapId, initialRoster)

        -- 2. Mock rename failure for next save
        local old_rename = renamefile
        renamefile = function(oldp, newp)
            return nil, "Disk full / rename error"
        end

        local failedRoster = {
            { szName = "CorruptedHero", level = 999, nExp = 0, faction = "ngami", series = 2, weaponBranch = "kiem", nNpcId = 102, camp = 1, personality = "aggressive" }
        }
        local failedSaveRet = SimProgression:SaveTrainBots(mapId, failedRoster)

        -- Restore renamefile
        renamefile = old_rename

        -- 3. Verify that old valid roster remains intact on disk
        local currentRoster = SimProgression:LoadTrainBots(mapId)
        local count = getn(currentRoster)
        local bot1 = currentRoster[1]

        -- 4. Verify tmp file cleaned up
        local tmpFile = io.open("save/simcity/train_map_53.dat.tmp", "r")
        local tmpExists = tmpFile ~= nil
        if tmpFile then tmpFile:close() end

        return initialSaveOk == 1, failedSaveRet, count, bot1 and bot1.szName, tmpExists
        """)
        init_ok, failed_ret, count, bot1_name, tmp_exists = res
        self.assertTrue(init_ok)
        self.assertEqual(failed_ret, 0)
        self.assertEqual(count, 1)
        self.assertEqual(bot1_name, "OldHero1")
        self.assertFalse(tmp_exists)

    def test_crash_safe_roster_atomic_overwrite_of_existing_file(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local mapId = 53

        -- 1. Save Roster A
        local rosterA = {
            { szName = "HeroAlpha", level = 100, nExp = 5000, faction = "thieulam", series = 1, weaponBranch = "dao", nNpcId = 101, camp = 0, personality = "balanced" }
        }
        local saveOkA = SimProgression:SaveTrainBots(mapId, rosterA)

        -- 2. Confirm Roster A is readable
        local loadedA = SimProgression:LoadTrainBots(mapId)
        local countA = getn(loadedA)
        local nameA = countA > 0 and loadedA[1].szName or ""
        local lvA = countA > 0 and loadedA[1].level or 0

        -- 3. Save Roster B to the exact same mapId (replacing existing roster file atomically)
        local rosterB = {
            { szName = "HeroBeta", level = 150, nExp = 25000, faction = "vodang", series = 3, weaponBranch = "kiem", nNpcId = 105, camp = 5, personality = "aggressive" }
        }
        local saveOkB = SimProgression:SaveTrainBots(mapId, rosterB)

        -- 4. Confirm Roster B was loaded, count is 1, and only HeroBeta exists
        local loadedB = SimProgression:LoadTrainBots(mapId)
        local countB = getn(loadedB)
        local nameB = countB > 0 and loadedB[1].szName or ""
        local lvB = countB > 0 and loadedB[1].level or 0

        -- 5. Confirm no .tmp file remains on disk
        local tmpFile = io.open("save/simcity/train_map_53.dat.tmp", "r")
        local tmpExists = tmpFile ~= nil
        if tmpFile then tmpFile:close() end

        return saveOkA == 1, countA, nameA, lvA, saveOkB == 1, countB, nameB, lvB, tmpExists
        """)
        okA, cntA, nmA, lvA, okB, cntB, nmB, lvB, tmpExists = res
        self.assertTrue(okA)
        self.assertEqual(cntA, 1)
        self.assertEqual(nmA, "HeroAlpha")
        self.assertEqual(lvA, 100)
        self.assertTrue(okB)
        self.assertEqual(cntB, 1)
        self.assertEqual(nmB, "HeroBeta")
        self.assertEqual(lvB, 150)
        self.assertFalse(tmpExists)

if __name__ == '__main__':
    unittest.main()

"""Train combat engage, leave, target filtering, and decision table tests.

Verifies Phase 02b DoD:
- Case 2 decision table (train/outdoor vs city peace/stall vs timeout vs peace zone)
- Case 3 decision table (train scanned enemy vs blind join fallback vs city safe)
- Target scanning and monster filtering (self, simbot, dead, monster vs kind 0, camp, radius)
- JoinFight execution (SetFightState 9->1, SetNpcKind 0, SetNpcCombat, NpcRun, Update cast)
- Spawn fields, EXP contract in sim.core, and Kingsoft Lua 4.0 compatibility
"""
import os
import unittest
from lupa import LuaRuntime

ROOT = os.path.join(
    os.path.dirname(__file__),
    "..",
    "script",
    "global",
    "nobitaxd",
    "vdk",
    "simcity",
    "components",
)


class TestTrainCombatEngage(unittest.TestCase):
    def _read(self, name):
        path = os.path.join(ROOT, name)
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def _read_latin(self, relpath):
        path = os.path.join(ROOT, "..", relpath)
        with open(path, "r", encoding="latin1", errors="replace") as f:
            return f.read()

    def test_movement_case3_join_fight_fallback(self):
        src = self._read("sim.movement.lua")
        self.assertIn('JoinFight(simInstance, tbNpc, "I start a fight")', src)
        self.assertIn('tbNpc.mode == "train" or outdoorOk', src)
        self.assertIn("CHANCE_ATTACK_NPC > 1", src)

    def test_movement_case2_train_no_early_leave(self):
        src = self._read("sim.movement.lua")
        self.assertIn("train/outdoor keep AI fight", src)
        idx = src.find("train/outdoor keep AI fight")
        self.assertGreater(idx, 0)
        chunk = src[idx : idx + 600]
        self.assertIn('tbNpc.mode == "train" or outdoorOk', chunk)
        self.assertIn("goc: return without LeaveFight", chunk)

    def test_fight_prefers_monster_kind(self):
        src = self._read("sim.fight.lua")
        self.assertIn("bestMonster", src)
        self.assertIn("Prefer real monsters", src)
        self.assertIn("IsNpcEnemyAround(simInstance, tbNpc)", src)

    def test_train_joinfight_uses_engine_ai_not_mode0(self):
        """Regression: AI mode 0 left bots idle next to monsters (2026-09-04)."""
        src = self._read("sim.fight.lua")
        idx = src.find('JoinFight = function(self, simInstance, tbNpc, reason)')
        self.assertGreater(idx, 0)
        chunk = src[idx : idx + 4500]
        self.assertIn('tbNpc.mode == "train" or outdoorOk', chunk)
        self.assertIn("SetFightState(tbNpc, 9", chunk)
        self.assertNotIn(
            "AI mode 0: Lua owns cast",
            chunk,
            "train JoinFight must not use AI mode 0 commentary/path",
        )
        train_branch = chunk.find('if tbNpc.mode == "train" or outdoorOk then')
        self.assertGreater(train_branch, 0)
        after = chunk[train_branch : train_branch + 1200]
        self.assertIn("SetFightState(tbNpc, 9", after)
        self.assertNotIn("SetFightState(tbNpc, 0", after)
        self.assertIn("SetNpcCombat", after)
        self.assertIn("self:Update", after)

    def test_train_joinfight_npcrun_on_found_enemy(self):
        src = self._read("sim.fight.lua")
        idx = src.find('JoinFight = function(self, simInstance, tbNpc, reason)')
        self.assertGreater(idx, 0)
        chunk = src[idx : idx + 4500]
        self.assertIn("tbNpc.foundNpcEnemy and tbNpc.foundNpcEnemy > 0 and NpcRun", chunk)

    def test_train_cast_prefers_botdoskill_and_short_cd(self):
        src = self._read("sim.fight.lua")
        self.assertIn("TRAIN_SKILL_CAST_CD_TICKS", src)
        self.assertIn("BotDoSkill(tbNpc.finalIndex, skillId, skillLevel, target.npcIndex)", src)
        with open(os.path.join(ROOT, "..", "config.lua"), encoding="utf-8", errors="replace") as f:
            cfg = f.read()
        self.assertIn("TRAIN_SKILL_CAST_CD_TICKS = 1", cfg)
        self.assertIn("SIMBOT_COMBAT_DEBUG", cfg)

    def test_pluyencong_spawn_fields(self):
        src = self._read_latin("plugins/pluyencong.lua")
        self.assertIn('mode = "train"', src)
        self.assertIn("CHANCE_ATTACK_NPC = 2", src)
        self.assertIn("leaveFightWhenNoEnemy = 0", src)
        self.assertIn("RADIUS_FIGHT_SCAN", src)
        self.assertIn("worldInfo.allowFighting = 1", src)

    def test_pthanhthi_train_map_early_return(self):
        src = self._read_latin("plugins/pthanhthi.lua")
        self.assertIn("SimCityLuyenCong:findMapIndex(nW)", src)
        self.assertIn("worldInfo.allowFighting = 1", src)
        self.assertIn("worldInfo.isTrainMap = 1", src)
        self.assertIn("SimCityLuyenCong:spawnForMap(trainIdx)", src)

    def test_sim_core_train_exp_contract(self):
        src = self._read("sim.core.lua")
        self.assertIn('tbNpc.mode == "train" and tbNpc.isFighting == 1', src)
        self.assertIn("tbNpc.trainExpTick", src)
        self.assertIn("SimProgression:AddExp", src)


class TestTrainCombatDecisionTables(unittest.TestCase):
    """Executable decision table tests using Lua runtime."""

    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        env_init = """
        random = function(a, b) return a or 1 end
        floor = math.floor
        sqrt = math.sqrt
        getn = function(t) if not t then return 0 end return #t end
        table.getn = getn
        GetNpcAroundNpcList = function(idx, radius) return {}, 0 end
        format = string.format
        tostring = tostring
        GetNpcPos = function(idx) return 3200, 3200, 319 end
        SetNpcAI = function(idx, mode) _G_ai = mode end
        SetNpcKind = function(idx, k) _G_kind = k end
        SetNpcCombat = function(idx, on, sk) _G_combat = {on, sk} end
        SetNpcRideHorse = function(idx, r) end
        NpcRun = function(idx, x, y) _G_run = {idx, x, y} end
        GetDistanceRadius = function(x1, y1, x2, y2) return math.abs(x1-x2) + math.abs(y1-y2) end
        IsAttackableCamp = function(c1, c2) return (c1 ~= c2 and c2 ~= 0) and 1 or 0 end
        TIME_FIGHTING = { minTs = 10, maxTs = 20 }
        TIME_RESTING = { minTs = 5, maxTs = 10 }
        """
        self.lua.execute(env_init)
        with open(os.path.join(ROOT, "sim.fight.lua"), "r", encoding="utf-8") as f:
            fight_src = f.read()
        self.lua.execute(fight_src)

    def test_decision_table_case2_leave_fight(self):
        """Case 2 decision table:
        Row 1: train mode, CanLeave=1 -> stays (does not call LeaveFight)
        Row 2: outdoor grind (allowFighting=1, cityPeace~=1), CanLeave=1 -> stays
        Row 3: city peace bot (allowFighting=0, cityPeace=1), CanLeave=1 -> LeaveFight('khong tim thay quai')
        Row 4: peace zone (SimCityIsPeaceZone=1) -> LeaveFight('vao vung hoa binh -> ngung danh')
        Row 5: tick expired -> LeaveFight('toi gio thay doi trang thai')
        """
        case2_lua = """
        function evalCase2(mode, allowFighting, cityPeace, canLeave, isPeaceZone, tickExpired)
            local leftReason = nil
            local fakeFightSys = {
                CanLeaveFight = function(self, sim, npc) return canLeave end,
                LeaveFight = function(self, sim, npc, dead, reason) leftReason = reason; return 0 end,
                IsNpcEnemyAround = function() return 0 end
            }
            local tbNpc = {
                isFighting = 1,
                mode = mode,
                fightSys = fakeFightSys,
                worldInfo = {
                    allowFighting = allowFighting,
                    cityPeace = cityPeace
                }
            }
            SimCityIsPeaceZone = function(npc) return isPeaceZone end

            if tbNpc.isFighting == 1 then
                if SimCityIsPeaceZone and SimCityIsPeaceZone(tbNpc) == 1 then
                    return tbNpc.fightSys:LeaveFight(nil, tbNpc, 0, 'vao vung hoa binh -> ngung danh'), leftReason
                end
                if tickExpired == 1 then
                    return tbNpc.fightSys:LeaveFight(nil, tbNpc, 0, 'toi gio thay doi trang thai'), leftReason
                end
                if tbNpc.fightSys:CanLeaveFight(nil, tbNpc) == 1 then
                    local outdoorOk = tbNpc.worldInfo and tbNpc.worldInfo.allowFighting == 1 and tbNpc.worldInfo.cityPeace ~= 1
                    if tbNpc.mode == 'train' or outdoorOk then
                        -- keep fighting like goc
                    else
                        return tbNpc.fightSys:LeaveFight(nil, tbNpc, 0, 'khong tim thay quai'), leftReason
                    end
                end
                return 1, nil
            end
            return -1, nil
        end
        """
        self.lua.execute(case2_lua)
        eval_fn = self.lua.globals()["evalCase2"]

        # Row 1: Train bot
        ret, reason = eval_fn("train", 1, 0, 1, 0, 0)
        self.assertEqual(ret, 1)
        self.assertIsNone(reason)

        # Row 2: Outdoor grind
        ret, reason = eval_fn("citizen", 1, 0, 1, 0, 0)
        self.assertEqual(ret, 1)
        self.assertIsNone(reason)

        # Row 3: City peace bot
        ret, reason = eval_fn("citizen", 0, 1, 1, 0, 0)
        self.assertEqual(ret, 0)
        self.assertEqual(reason, "khong tim thay quai")

        # Row 4: Peace zone
        ret, reason = eval_fn("train", 1, 0, 1, 1, 0)
        self.assertEqual(ret, 0)
        self.assertEqual(reason, "vao vung hoa binh -> ngung danh")

        # Row 5: Timeout
        ret, reason = eval_fn("train", 1, 0, 1, 0, 1)
        self.assertEqual(ret, 0)
        self.assertEqual(reason, "toi gio thay doi trang thai")

    def test_decision_table_case3_engage(self):
        """Case 3 decision table:
        Row 1: train bot with scanned enemy -> TriggerFightWithNPC returns 1, JoinFight('enemy around')
        Row 2: train bot with empty scan, but CHANCE_ATTACK_NPC=2 (>1) -> JoinFight('I start a fight')
        Row 3: outdoor grind bot with empty scan, CHANCE_ATTACK_NPC=2 (>1) -> JoinFight('I start a fight')
        Row 4: city bot with SimCityCanFight=0 -> does not fight
        Row 5: city bot with CHANCE_ATTACK_NPC=1 and countFighting=0 -> does not start fight alone
        """
        case3_lua = """
        function evalCase3(mode, outdoorOk, canFight, hasEnemy, chanceAttackNpc, countFighting)
            local joinReason = nil
            local fakeFightSys = {
                TriggerFightWithNPC = function(self, sim, npc)
                    if hasEnemy == 1 then
                        joinReason = 'enemy around'
                        return 1
                    end
                    return 0
                end,
                JoinFight = function(self, sim, npc, reason)
                    joinReason = reason
                    return 1
                end,
                GetFightingNPCs = function() return countFighting end
            }
            local tbNpc = {
                mode = mode,
                isFighting = 0,
                isAttractionAround = 0,
                CHANCE_ATTACK_NPC = chanceAttackNpc,
                fightSys = fakeFightSys,
                worldInfo = {
                    allowFighting = outdoorOk and 1 or 0,
                    cityPeace = outdoorOk and 0 or 1,
                    showFightingArea = 0
                }
            }

            if canFight ~= 1 then
                return 0, nil
            end

            -- Case 3 block from sim.movement.lua
            if tbNpc.CHANCE_ATTACK_NPC and tbNpc.CHANCE_ATTACK_NPC >= 1 then
                local outdoor = tbNpc.worldInfo and tbNpc.worldInfo.allowFighting == 1 and tbNpc.worldInfo.cityPeace ~= 1
                if tbNpc.mode == 'train' or outdoor then
                    if tbNpc.fightSys:TriggerFightWithNPC(nil, tbNpc) == 1 then
                        return 1, joinReason
                    end
                    if countFighting > 0 or tbNpc.CHANCE_ATTACK_NPC > 1 then
                        tbNpc.fightSys:JoinFight(nil, tbNpc, 'I start a fight')
                        return 1, joinReason
                    end
                elseif countFighting > 0 or tbNpc.CHANCE_ATTACK_NPC > 1 then
                    tbNpc.fightSys:JoinFight(nil, tbNpc, 'I start a fight')
                    return 1, joinReason
                end
            end
            return 0, nil
        end
        """
        self.lua.execute(case3_lua)
        eval_fn = self.lua.globals()["evalCase3"]

        # Row 1: Train bot with scanned enemy
        ret, reason = eval_fn("train", True, 1, 1, 2, 0)
        self.assertEqual(ret, 1)
        self.assertEqual(reason, "enemy around")

        # Row 2: Train bot with empty scan, but CHANCE_ATTACK_NPC=2 > 1 -> fallback join
        ret, reason = eval_fn("train", True, 1, 0, 2, 0)
        self.assertEqual(ret, 1)
        self.assertEqual(reason, "I start a fight")

        # Row 3: Outdoor grind with empty scan, CHANCE_ATTACK_NPC=2 > 1 -> fallback join
        ret, reason = eval_fn("citizen", True, 1, 0, 2, 0)
        self.assertEqual(ret, 1)
        self.assertEqual(reason, "I start a fight")

        # Row 4: City peace (SimCityCanFight == 0)
        ret, reason = eval_fn("citizen", False, 0, 0, 2, 0)
        self.assertEqual(ret, 0)
        self.assertIsNone(reason)

        # Row 5: City bot with chance=1 and count=0
        ret, reason = eval_fn("citizen", False, 1, 0, 1, 0)
        self.assertEqual(ret, 0)
        self.assertIsNone(reason)

    def test_target_scanning_filtering_decision_table(self):
        """IsNpcEnemyAround decision table:
        1. Skips self
        2. Skips other SimBot (GetNpcParam 4 == 1)
        3. Skips dead entity (life <= 0)
        4. Train mode: prefers real monster (kind ~= 0) over kind == 0
        5. Train mode: accepts kind == 0 when no kind ~= 0 exists
        6. City mode: ignores monster (kind ~= 0), only attacks kind == 0 with hostile camp
        7. City mode: ignores kind == 0 with friendly camp
        """
        test_scan = """
        function setupScenario(hasMonster, hasHostileHuman, hasFriendlyHuman)
            -- 100: self, 201: dead, 202: simbot, 203: monster (kind 1), 204: human (kind 0)
            local npcs = { 100, 201, 202 }
            if hasMonster then table.insert(npcs, 203) end
            if hasHostileHuman or hasFriendlyHuman then table.insert(npcs, 204) end

            NPCINFO_GetNpcCurrentLife = function(idx)
                if idx == 201 then return 0 end
                return 1000
            end
            GetNpcParam = function(idx, p)
                if idx == 202 and p == 4 then return 1 end
                return 0
            end
            GetNpcKind = function(idx)
                if idx == 203 then return 1 end
                return 0
            end
            GetNpcCurCamp = function(idx)
                if idx == 204 then
                    return hasHostileHuman and 2 or 1
                end
                return 0
            end
            GetNpcAroundNpcList = function(idx, radius)
                return npcs, table.getn(npcs)
            end
        end

        function runScan(mode)
            local tbNpc = {
                finalIndex = 100,
                mode = mode,
                camp = 1,
                RADIUS_FIGHT_SCAN = 20,
                worldInfo = {
                    allowFighting = (mode == 'train' and 1 or 0),
                    cityPeace = (mode == 'train' and 0 or 1)
                }
            }
            return SimFight.Citizen:IsNpcEnemyAround(nil, tbNpc)
        end
        """
        self.lua.execute(test_scan)
        setup_fn = self.lua.globals()["setupScenario"]
        scan_fn = self.lua.globals()["runScan"]

        # 1. Train mode with both monster (203) and hostile human (204): prefers monster (203)
        setup_fn(True, True, False)
        self.assertEqual(scan_fn("train"), 203)

        # 2. Train mode with only human (204): picks human (204)
        setup_fn(False, True, False)
        self.assertEqual(scan_fn("train"), 204)

        # 3. City mode with monster (203) and hostile human (204): ignores monster, picks human (204)
        setup_fn(True, True, False)
        self.assertEqual(scan_fn("citizen"), 204)

        # 4. City mode with only monster (203): returns 0 (never attacks monsters in city)
        setup_fn(True, False, False)
        self.assertEqual(scan_fn("citizen"), 0)

        # 5. City mode with friendly human (204): returns 0
        setup_fn(False, False, True)
        self.assertEqual(scan_fn("citizen"), 0)

        # 6. Self, dead, other simbot only: returns 0 in both modes
        setup_fn(False, False, False)
        self.assertEqual(scan_fn("train"), 0)
        self.assertEqual(scan_fn("citizen"), 0)

    def test_join_fight_execution_and_run(self):
        """Verify JoinFight sets combat state, AI mode 9->1, attackable kind 0,
        skill combat binding, and executes NpcRun to enemy."""
        test_join = """
        function runJoin(hasTarget)
            _G_ai = nil
            _G_kind = nil
            _G_combat = nil
            _G_run = nil
            local updated = 0

            GetNpcPos = function(idx)
                if idx == 100 then return 3200, 3200, 319
                elseif idx == 203 then return 3300, 3300, 319 end
                return 3200, 3200, 319
            end

            local tbNpc = {
                id = 1,
                finalIndex = 100,
                mode = 'train',
                isFighting = 0,
                skillCastBua = { 380, 20 },
                foundNpcEnemy = hasTarget and 203 or nil,
                tick_breath = 100,
                worldInfo = { allowFighting = 1, cityPeace = 0 }
            }

            local oldUpdate = SimFight.Citizen.Update
            SimFight.Citizen.Update = function() updated = 1 end

            SimFight.Citizen:JoinFight(nil, tbNpc, 'test_engage')

            SimFight.Citizen.Update = oldUpdate
            return tbNpc.isFighting, _G_ai, _G_kind, (_G_combat and _G_combat[2]), (_G_run and _G_run[2]), updated
        end
        """
        self.lua.execute(test_join)
        join_fn = self.lua.globals()["runJoin"]

        # With target: should NpcRun to tile 3300/32 = 103
        isFighting, ai, kind, skill, runX, updated = join_fn(True)
        self.assertEqual(isFighting, 1)
        self.assertEqual(ai, 1)  # SetFightState mode 9 translates to AI 1
        self.assertEqual(kind, 0)  # Attackable
        self.assertEqual(skill, 380)
        self.assertEqual(runX, 103)
        self.assertEqual(updated, 1)

        # Without target: still enters combat, AI 1, but no NpcRun
        isFighting2, ai2, kind2, skill2, runX2, updated2 = join_fn(False)
        self.assertEqual(isFighting2, 1)
        self.assertEqual(ai2, 1)
        self.assertEqual(kind2, 0)
        self.assertEqual(skill2, 380)
        self.assertIsNone(runX2)
        self.assertEqual(updated2, 1)


if __name__ == "__main__":
    unittest.main()

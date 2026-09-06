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

try:
    import lupa
    from lupa import LuaRuntime
    HAS_LUPA = True
except ImportError:
    HAS_LUPA = False
    LuaRuntime = None

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

    def test_production_call_path(self):
        """Verify production call path executes SimMovement.Citizen:Move directly."""
        src = self._read("sim.movement.lua")
        self.assertIn("SimMovement.Citizen", src)
        self.assertIn("Move = function(self, simInstance, tbNpc)", src)
        self.assertIn("CanLeaveFight", src)
        self.assertIn("TriggerFightWithNPC", src)
        self.assertIn("JoinFight", src)

    def test_monster_first_filtering(self):
        """Verify monster-first priority in Citizen and KeoXe target scanning."""
        src = self._read("sim.fight.lua")
        self.assertIn("bestMonster", src)
        self.assertIn("if bestMonster > 0 then return bestMonster end", src)
        self.assertIn("if bestKind0 > 0 then return bestKind0 end", src)

    def test_no_neutral_kind0_train_fallback(self):
        """Verify train bots do NOT fall back to peaceful/neutral kind-0 entities."""
        src = self._read("sim.fight.lua")
        self.assertIn("Only allow kind-0 player/PvP targets through explicit DoSat/hostile-PvP rules", src)
        self.assertIn("tbNpc.isDoSat == 1 or tbNpc.camp == 5", src)
        self.assertIn("IsAttackableCamp(tbNpc.camp, fighter2Camp) == 1", src)

    def test_canonical_branch_resolution(self):
        """Verify deterministic branch resolution via SimFight:ResolveCanonicalBranch."""
        src = self._read("sim.fight.lua")
        self.assertIn("function SimFight:ResolveCanonicalBranch(tbNpc, fac)", src)
        self.assertIn("tbNpc.nNewWeaponType", src)
        self.assertIn("SimBotNpc and tbNpc.nNpcId and SimBotNpc[tbNpc.nNpcId]", src)

    def test_no_arbitrary_branch_mutation(self):
        """Verify sim.fight.lua never iterates facTable or mutates weaponBranch arbitrarily."""
        src = self._read("sim.fight.lua")
        self.assertNotIn("for bName, list in facTable do", src)
        self.assertNotIn("tbNpc.weaponBranch = bName", src)

    def test_no_unconditional_hardcoded_selectedskill_fallback(self):
        """Verify execCastNormalSkill does not have unconditional {53, 1} fallback."""
        src = self._read("sim.fight.lua")
        cast_idx = src.find("function execCastNormalSkill(self, simInstance, tbNpc)")
        self.assertGreater(cast_idx, 0)
        cast_chunk = src[cast_idx : src.find("function ", cast_idx + 10)]
        self.assertNotIn("selectedSkill = { 53, 1 }", cast_chunk)
        self.assertIn("execCastNormalSkill resolution failed for bot", cast_chunk)

    def test_ranged_classification_fallback_when_skill_meta_missing(self):
        """Verify ranged classification falls back to SimFight:IsRangedFaction."""
        src = self._read("sim.fight.lua")
        cast_idx = src.find("function execCastNormalSkill(self, simInstance, tbNpc)")
        self.assertGreater(cast_idx, 0)
        cast_chunk = src[cast_idx : src.find("function ", cast_idx + 10)]
        self.assertIn("isRanged = SimFight:IsRangedFaction(tbNpc.faction, tbNpc.weaponBranch)", cast_chunk)

    def test_dead_target_rescan(self):
        """Verify SelectBestTarget clears dead enemy (life <= 0) and rescans."""
        src = self._read("sim.fight.lua")
        select_idx = src.find("function SimFight:SelectBestTarget")
        self.assertGreater(select_idx, 0)
        select_chunk = src[select_idx : select_idx + 3000]
        self.assertIn("NPCINFO_GetNpcCurrentLife(foundNpcEnemy)", select_chunk)
        self.assertIn("tbNpc.foundNpcEnemy = nil", select_chunk)


@unittest.skipUnless(HAS_LUPA, "lupa is not installed or not supported in this Python environment")
class TestTrainCombatDecisionTables(unittest.TestCase):
    """Executable decision table tests using Lua runtime."""

    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        env_init = """
        REFRESH_RATE = 18
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
        SubWorldIdx2ID = function(w) return w end
        SimCityCanFight = function(npc) return 1 end
        NPCINFO_GetNpcCurrentLife = function(idx) return 1000 end
        NPCINFO_GetNpcCurrentMaxLife = function(idx) return 1000 end
        NpcCastSkill = function() end
        BotDoSkill = function() return 1 end
        """
        self.lua.execute(env_init)
        with open(os.path.join(ROOT, "sim.fight.lua"), "r", encoding="utf-8") as f:
            fight_src = f.read()
        self.lua.execute(fight_src)
        with open(os.path.join(ROOT, "sim.movement.lua"), "r", encoding="utf-8") as f:
            mov_src = f.read()
        self.lua.execute(mov_src)

    def test_decision_table_case2_leave_fight(self):
        """Case 2 decision table executed via production SimMovement.Citizen:Move:
        Row 1: train mode, CanLeave=1 -> stays (does not call LeaveFight)
        Row 2: outdoor grind (allowFighting=1, cityPeace~=1), CanLeave=1 -> stays
        Row 3: city peace bot (allowFighting=0, cityPeace=1), CanLeave=1 -> LeaveFight('khong tim thay quai')
        Row 4: peace zone (SimCityIsPeaceZone=1) -> LeaveFight('vao vung hoa binh -> ngung danh')
        Row 5: tick expired -> LeaveFight('toi gio thay doi trang thai')
        """
        eval_script = """
        function evalCase2(mode, allowFighting, cityPeace, canLeave, isPeaceZone, tickExpired)
            local leftReason = nil
            local fakeFightSys = {
                CanLeaveFight = function(self, sim, npc) return canLeave end,
                LeaveFight = function(self, sim, npc, dead, reason) leftReason = reason; return 0 end,
                IsNpcEnemyAround = function() return 0 end
            }
            local tbNpc = {
                id = 1,
                finalIndex = 100,
                isFighting = 1,
                mode = mode,
                fightSys = fakeFightSys,
                tick_breath = 100,
                tick_canswitch = (tickExpired == 1 and 90 or 200),
                worldInfo = {
                    allowFighting = allowFighting,
                    cityPeace = cityPeace
                }
            }
            SimCityIsPeaceZone = function(npc) return isPeaceZone end
            local ret = SimMovement.Citizen:Move(nil, tbNpc)
            return ret, leftReason
        end
        """
        self.lua.execute(eval_script)
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
        """Case 3 decision table executed via production SimMovement.Citizen:Move:
        Row 1: train bot with scanned enemy -> TriggerFightWithNPC returns 1, JoinFight('enemy around')
        Row 2: train bot with empty scan, but CHANCE_ATTACK_NPC=2 (>1) -> JoinFight('I start a fight')
        Row 3: outdoor grind bot with empty scan, CHANCE_ATTACK_NPC=2 (>1) -> JoinFight('I start a fight')
        Row 4: city bot with SimCityCanFight=0 -> does not fight
        Row 5: city bot with CHANCE_ATTACK_NPC=1 and countFighting=0 -> does not start fight alone
        """
        eval_script = """
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
                GetFightingNPCs = function() return countFighting end,
                TriggerFightWithPlayer = function() return 0 end
            }
            SimCityCanFight = function(npc) return canFight end
            local tbNpc = {
                id = 1,
                finalIndex = 100,
                mode = mode,
                isFighting = 0,
                isAttractionAround = 0,
                CHANCE_ATTACK_NPC = chanceAttackNpc,
                fightSys = fakeFightSys,
                tick_breath = 100,
                tick_canswitch = 50,
                worldInfo = {
                    allowFighting = outdoorOk and 1 or 0,
                    cityPeace = outdoorOk and 0 or 1,
                    showFightingArea = 0
                }
            }
            local ret = SimMovement.Citizen:Move(nil, tbNpc)
            return ret, joinReason
        end
        """
        self.lua.execute(eval_script)
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
        function setupScenario(hasMonster, hasHostileHuman, hasFriendlyHuman, hasNeutralHuman)
            -- 100: self, 201: dead, 202: simbot, 203: monster (kind 1), 204: human (kind 0)
            local npcs = { 100, 201, 202 }
            if hasMonster then table.insert(npcs, 203) end
            if hasHostileHuman or hasFriendlyHuman or hasNeutralHuman then table.insert(npcs, 204) end

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
                    if hasHostileHuman then return 2
                    elseif hasFriendlyHuman then return 1
                    elseif hasNeutralHuman then return 0
                    end
                end
                return 0
            end
            GetNpcAroundNpcList = function(idx, radius)
                return npcs, table.getn(npcs)
            end
        end

        function runScan(mode, isDoSat)
            local tbNpc = {
                finalIndex = 100,
                mode = mode,
                camp = (isDoSat == 1 and 5 or 1),
                isDoSat = isDoSat or 0,
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
        setup_fn(True, True, False, False)
        self.assertEqual(scan_fn("train"), 203)

        # 2. Train mode with only hostile human (204): picks human (204)
        setup_fn(False, True, False, False)
        self.assertEqual(scan_fn("train"), 204)

        # 2b. Train mode with only friendly human (204): returns 0 (never attacks friendly player)
        setup_fn(False, False, True, False)
        self.assertEqual(scan_fn("train"), 0)

        # 2c. Train mode with only neutral human (204, camp 0): returns 0 (never attacks neutral player)
        setup_fn(False, False, False, True)
        self.assertEqual(scan_fn("train"), 0)

        # 2d. Train mode with DoSat bot (camp 5 / isDoSat 1) vs friendly human: attacks human (204)
        setup_fn(False, False, True, False)
        self.assertEqual(scan_fn("train", 1), 204)

        # 3. City mode with monster (203) and hostile human (204): ignores monster, picks human (204)
        setup_fn(True, True, False, False)
        self.assertEqual(scan_fn("citizen"), 204)

        # 4. City mode with only monster (203): returns 0 (never attacks monsters in city)
        setup_fn(True, False, False, False)
        self.assertEqual(scan_fn("citizen"), 0)

        # 5. City mode with friendly human (204): returns 0
        setup_fn(False, False, True, False)
        self.assertEqual(scan_fn("citizen"), 0)

        # 6. Self, dead, other simbot only: returns 0 in both modes
        setup_fn(False, False, False, False)
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

    def test_select_best_target_clears_dead_enemy_and_rescans(self):
        """When previously found enemy dies (curLife <= 0), SelectBestTarget clears
        foundNpcEnemy and dynamically scans for the next living enemy."""
        test_script = """
        function evalTargetSelection()
            -- 201 is dead monster, 202 is newly spawned living monster
            NPCINFO_GetNpcCurrentLife = function(idx)
                if idx == 201 then return 0 end
                if idx == 202 then return 800 end
                return 1000
            end
            GetNpcPos = function(idx)
                if idx == 100 then return 3200, 3200, 319
                elseif idx == 201 then return 3250, 3250, 319
                elseif idx == 202 then return 3260, 3260, 319 end
                return nil
            end
            GetNpcParam = function(idx, p) return 0 end
            GetNpcKind = function(idx) return 1 end -- monster
            GetNpcCurCamp = function(idx) return 0 end
            GetNpcAroundNpcList = function(idx, radius)
                return { 202 }, 1 -- returns new living monster
            end

            local tbNpc = {
                finalIndex = 100,
                mode = 'train',
                foundNpcEnemy = 201, -- previously locked onto 201
                worldInfo = { allowFighting = 1, cityPeace = 0 }
            }

            local target = SimFight:SelectBestTarget(nil, tbNpc, SimFight.Citizen)
            return target and target.npcIndex, tbNpc.foundNpcEnemy
        end
        """
        self.lua.execute(test_script)
        selected_idx, saved_enemy = self.lua.globals()["evalTargetSelection"]()
        self.assertEqual(selected_idx, 202)
        self.assertEqual(saved_enemy, 202)

    def test_ranged_classification_faction_fallback_when_skill_meta_unusable(self):
        """When SimSkillMeta.Get exists but returns nil for a skill,
        ranged classification falls back to SimFight:IsRangedFaction:
        - Nga Mi -> ranged (1), triggers KITE state when target.dist < 4
        - Thieu Lam -> melee (0), triggers COMBO state when in range
        """
        test_script = """
        function evalRangedFallback(fac)
            SimSkillMeta = {
                Get = function(self, id) return nil end
            }
            SimCityPhai = {
                ngami = { normalCast = { 9999 } },
                thieulam = { normalCast = { 9999 } }
            }
            GetNpcPos = function(idx)
                if idx == 100 then return 3200, 3200, 319 end
                if idx == 200 then return 3264, 3200, 319 end -- tile distance 2 (< 4)
                return 3200, 3200, 319
            end
            local tbNpc = {
                id = 1,
                finalIndex = 100,
                faction = fac,
                mode = 'train',
                isFighting = 1,
                fighting = 1,
                tick_breath = 100,
                tick_canCast = 50,
                skillCastBua = { 9999, 20 },
                isPlayerEnemyAround = 0
            }
            SimFight.SelectBestTarget = function()
                return {
                    targetType = 'monster',
                    npcIndex = 200,
                    worldX = 3264,
                    worldY = 3200,
                    tileX = 102,
                    tileY = 100,
                    dist = 2
                }
            end
            execCastNormalSkill(SimFight.Citizen, nil, tbNpc)
            return SimFight:GetCombatState(tbNpc)
        end
        """
        self.lua.execute(test_script)
        eval_fn = self.lua.globals()["evalRangedFallback"]
        self.assertEqual(eval_fn("ngami"), "KITE")
        self.assertEqual(eval_fn("thieulam"), "COMBO")

    def test_canonical_faction_skill_fallback_resolves_without_hardcoded_ids(self):
        """When tbNpc.skillCastBua is nil, canonical SimProgression.FACTION_SKILLS
        metadata resolves the skill matching faction, weapon branch, and level,
        without relying on unsafe hardcoded skill ID tables."""
        test_script = """
        function evalSkillResolution(fac, branch, lv)
            SimProgression = {
                FACTION_SKILLS = {
                    thieulam = {
                        dao = {
                            { reqLv = 90, id = 321 },
                            { reqLv = 10, id = 13 },
                            { reqLv = 1, id = 53 }
                        }
                    }
                },
                CalcSkillLevel = function(self, botLv, req) return 20 end
            }
            SimCityPhai = {
                thieulam = { normalCast = {} }
            }
            GetNpcPos = function(idx)
                return 3200, 3200, 319
            end
            local tbNpc = {
                id = 1,
                finalIndex = 100,
                faction = fac,
                weaponBranch = branch,
                level = lv,
                mode = 'train',
                isFighting = 1,
                fighting = 1,
                tick_breath = 100,
                tick_canCast = 50,
                skillCastBua = nil,
                isPlayerEnemyAround = 0
            }
            local castedSkillId = nil
            NpcCastSkill = function(idx, sid, slv, x, y)
                castedSkillId = sid
            end
            BotDoSkill = function(idx, sid, slv, targetIdx)
                castedSkillId = sid
                return 1
            end
            SimFight.SelectBestTarget = function()
                return {
                    targetType = 'monster',
                    npcIndex = 200,
                    worldX = 3200,
                    worldY = 3200,
                    tileX = 100,
                    tileY = 100,
                    dist = 1
                }
            end
            execCastNormalSkill(SimFight.Citizen, nil, tbNpc)
            return castedSkillId
        end
        """
        self.lua.execute(test_script)
        eval_fn = self.lua.globals()["evalSkillResolution"]
        # Level 90 Thieu Lam Dao should resolve 321 (Vo Tuong Tram)
        self.assertEqual(eval_fn("thieulam", "dao", 95), 321)
        # Level 15 Thieu Lam Dao should resolve 13 (Hang Long Bat Vu)
        self.assertEqual(eval_fn("thieulam", "dao", 15), 13)
        # Level 5 Thieu Lam Dao (< 10) should resolve 53 (basic attack)
        self.assertEqual(eval_fn("thieulam", "dao", 5), 53)
        # Unknown faction should NOT resolve any skill and return None
        self.assertIsNone(eval_fn("unknown_faction", "dao", 95))
        # Unknown branch without gear metadata should NOT resolve any skill and return None
        self.assertIsNone(eval_fn("thieulam", "unknown_branch", 95))

    def test_canonical_branch_resolution_and_no_arbitrary_mutation(self):
        """SimFight:ResolveCanonicalBranch deterministically resolves branch from
        assigned branch, gear metadata (nNewWeaponType), or NPC template (SimBotNpc).
        When resolution fails, tbNpc.weaponBranch is never mutated to an arbitrary branch."""
        test_script = """
        function evalBranchResolution()
            SimProgression = {
                FACTION_SKILLS = {
                    thieulam = { quyen = {}, con = {}, dao = {} },
                    vodang = { kiem = {}, chuong = {} },
                    thienvuong = { thuong = {}, dao = {}, chuy = {} }
                }
            }
            SimBotNpc = {
                [1907] = { 323, "thuong" }
            }
            -- 1. Assigned branch directly matching
            local b1 = SimFight:ResolveCanonicalBranch({ faction = "thieulam", weaponBranch = "dao" })
            -- 2. Assigned branch alias ("taykhong" -> "quyen")
            local b2 = SimFight:ResolveCanonicalBranch({ faction = "thieulam", weaponBranch = "taykhong" })
            -- 3. Derived from gear nNewWeaponType = 20 (sword) for vodang -> "kiem"
            local b3 = SimFight:ResolveCanonicalBranch({ faction = "vodang", nNewWeaponType = 20 })
            -- 4. Derived from template SimBotNpc[1907] for thienvuong -> "thuong"
            local b4 = SimFight:ResolveCanonicalBranch({ faction = "thienvuong", nNpcId = 1907 })
            -- 5. Unresolvable branch: missing branch, no gear, no template -> nil
            local npc5 = { faction = "thieulam", weaponBranch = nil }
            local b5 = SimFight:ResolveCanonicalBranch(npc5)
            local mutatedBranch5 = npc5.weaponBranch
            return b1, b2, b3, b4, b5, mutatedBranch5
        end
        """
        self.lua.execute(test_script)
        b1, b2, b3, b4, b5, mutated5 = self.lua.globals()["evalBranchResolution"]()
        self.assertEqual(b1, "dao")
        self.assertEqual(b2, "quyen")
        self.assertEqual(b3, "kiem")
        self.assertEqual(b4, "thuong")
        self.assertIsNone(b5)
        self.assertIsNone(mutated5)


if __name__ == "__main__":
    unittest.main()

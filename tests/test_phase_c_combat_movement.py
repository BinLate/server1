def _convert_kingsoft_for_loops(src):
    import re
    def repl(m):
        target = m.group(2).strip()
        if '(' in target or target.startswith('pairs') or target.startswith('ipairs') or target.startswith('next'):
            return m.group(0)
        return f'for {m.group(1)} in pairs({target}) do'
    return re.sub(r'\bfor\s+([a-zA-Z0-9_,\s]+)\s+in\s+([^()\r\n]+?)\s+do\b', repl, src)

import unittest
import os
import shutil
import lupa
from lupa import LuaRuntime

class TestPhaseCCombatMovement(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        if not os.path.exists("save/simcity"):
            os.makedirs("save/simcity")

    def tearDown(self):
        if os.path.exists("save/simcity"):
            shutil.rmtree("save/simcity", ignore_errors=True)

    def init_simcity_environment(self):
        mock_env = """
        random = function(a, b)
            if not a then return 0 end
            if not b then return a end
            return a
        end
        randomRange = function(pos, variance)
            return { pos[1] + (variance or 0), pos[2] + (variance or 0) }
        end
        floor = math.floor
        sqrt = math.sqrt
        max = math.max
        min = math.min
        mod = math.fmod
        strlower = string.lower
        getn = function(t)
            if not t then return 0 end
            return table.getn and table.getn(t) or #t
        end

        REFRESH_RATE = 18
        DISTANCE_SUPPORT_PLAYER = 15
        RADIUS_FIGHT_SCAN = 10
        RADIUS_FIGHT_PLAYER = 12
        SIMBOT_CHASE_MAX_TILES = 20
        SIMBOT_AGGRO_PLAYER = 1
        TIME_RESTING = { minTs = 10, maxTs = 20 }
        SimCityPhai = {
            thieulam = { normalCast = {{318, 20}} },
            vodang = { normalCast = {{267, 20}} },
            ngami = { normalCast = {{92, 20}} },
            duongmon = { normalCast = {{180, 20}} },
            caibang = { normalCast = {{200, 20}} },
            thienvuong = { normalCast = {{50, 20}} }
        }

        SubWorldID2Idx = function(id) return id end
        SubWorldIdx2ID = function(idx) return idx end
        GetNpcPos = function(idx) return 3200, 3200, 53 end
        CallPlayerFunction = function(pId, fn, ...) return 53, 100, 100 end
        GetDistanceRadius = function(x1, y1, x2, y2)
            local dx = x1 - x2
            local dy = y1 - y2
            return math.sqrt(dx*dx + dy*dy)
        end
        IsAttackableCamp = function(c1, c2) return (c1 ~= c2) and 1 or 0 end
        GetNpcKind = function(idx) return 0 end
        GetNpcCurCamp = function(idx) return 2 end
        GetNpcParam = function(idx, p) return 0 end
        SetNpcKind = function(idx, k) end
        NpcRun = function(idx, x, y) end
        NpcCastSkill = function(idx, sk, lv, x, y) end
        SimCityIsPeaceZone = function(npc) return 0 end
        SimCityCanFight = function(npc) return 1 end
        SimPickSkill = function(npc) return { npc.skillId or 318, npc.skillLevel or 20 } end
        IncludeLib = function(...) end
        Include = function(...) end
        """
        self.lua.execute(mock_env)
        self.load_lua_file("script/global/nobitaxd/vdk/simcity/components/sim.movement.lua")
        self.load_lua_file("script/global/nobitaxd/vdk/simcity/components/sim.fight.lua")
        self.load_lua_file("script/global/nobitaxd/vdk/simcity/components/sim.gear.lua")
        self.load_lua_file("script/global/nobitaxd/vdk/simcity/components/sim.progression.lua")

    def load_lua_file(self, rel_path):
        import re
        with open(rel_path, "r", encoding="latin1") as f:
            code = f.read()
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        code = _convert_kingsoft_for_loops(code)
        return self.lua.execute(code)

    def test_movement_fsm_initial_state_and_transitions(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local tbNpc = {
            id = 1,
            finalIndex = 101,
            moveState = SIM_MOVE_STATE.WANDER,
            tick_breath = 50
        }
        local initial = SimMovement:GetState(tbNpc)

        SimMovement:SetState(tbNpc, SIM_MOVE_STATE.CHASE, "spotted target")
        local chased = SimMovement:GetState(tbNpc)
        local reason1 = tbNpc.moveStateReason
        local changeTick1 = tbNpc.moveStateChangeTick

        SimMovement:SetState(tbNpc, SIM_MOVE_STATE.KITE, "spacing retreat")
        local kited = SimMovement:GetState(tbNpc)
        local reason2 = tbNpc.moveStateReason

        return initial, chased, reason1, changeTick1, kited, reason2
        """)
        initial, chased, reason1, changeTick1, kited, reason2 = res
        self.assertEqual(initial, "WANDER")
        self.assertEqual(chased, "CHASE")
        self.assertEqual(reason1, "spotted target")
        self.assertEqual(changeTick1, 50)
        self.assertEqual(kited, "KITE")
        self.assertEqual(reason2, "spacing retreat")

    def test_movement_stuck_detection_increments_and_resets(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local tbNpc = {
            id = 1,
            finalIndex = 101,
            moveState = SIM_MOVE_STATE.WANDER,
            isFighting = 0
        }

        -- Initial call records baseline coords
        local s0 = SimMovement:CheckStuck(tbNpc, 100, 100)

        -- 5 consecutive stationary ticks
        local s1 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s2 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s3 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s4 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s5 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local ticksBeforeMove = tbNpc.stuckTicks

        -- Position changes significantly -> stuck resets
        local s6 = SimMovement:CheckStuck(tbNpc, 115, 115)
        local ticksAfterMove = tbNpc.stuckTicks

        return s0, s1, s2, s3, s4, s5, ticksBeforeMove, s6, ticksAfterMove
        """)
        s0, s1, s2, s3, s4, s5, ticksBefore, s6, ticksAfter = res
        self.assertEqual(s0, 0)
        self.assertEqual(s1, 0)
        self.assertEqual(s2, 0)
        self.assertEqual(s3, 0)
        self.assertEqual(s4, 0)
        self.assertEqual(s5, 1) # Triggered stuck at 5 ticks
        self.assertEqual(ticksBefore, 5)
        self.assertEqual(s6, 0)
        self.assertEqual(ticksAfter, 0)

    def test_movement_stuck_recovery_triggers_and_repaths(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local dashCalled = 0
        local dashX, dashY = 0, 0
        BotDashTo = function(idx, x, y, speed)
            dashCalled = dashCalled + 1
            dashX = x
            dashY = y
        end

        local tbNpc = {
            id = 1,
            finalIndex = 101,
            moveState = SIM_MOVE_STATE.WANDER,
            stuckTicks = 5,
            stuckRecoveries = 0
        }

        local recovered = SimMovement:HandleStuck(nil, tbNpc, 100, 100)
        local ticksAfter = tbNpc.stuckTicks
        local countAfter = tbNpc.stuckRecoveries

        return recovered, dashCalled, countAfter, ticksAfter
        """)
        recovered, dashCalled, countAfter, ticksAfter = res
        self.assertEqual(recovered, 1)
        self.assertEqual(dashCalled, 1)
        self.assertEqual(countAfter, 1)
        self.assertEqual(ticksAfter, 0)

    def test_combat_fsm_initial_state_and_transitions(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local tbNpc = {
            finalIndex = 101,
            combatState = SIM_COMBAT_STATE.PEACE,
            tick_breath = 120
        }
        local initial = SimFight:GetCombatState(tbNpc)

        SimFight:SetCombatState(tbNpc, SIM_COMBAT_STATE.ENGAGING, "closing in")
        local engaging = SimFight:GetCombatState(tbNpc)

        SimFight:SetCombatState(tbNpc, SIM_COMBAT_STATE.COMBO, "casting skills")
        local combo = SimFight:GetCombatState(tbNpc)

        SimFight:SetCombatState(tbNpc, SIM_COMBAT_STATE.RETREAT_HEAL, "low hp panic")
        local retreat = SimFight:GetCombatState(tbNpc)

        return initial, engaging, combo, retreat
        """)
        initial, engaging, combo, retreat = res
        self.assertEqual(initial, "PEACE")
        self.assertEqual(engaging, "ENGAGING")
        self.assertEqual(combo, "COMBO")
        self.assertEqual(retreat, "RETREAT_HEAL")

    def test_combat_ranged_faction_detection(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local r1 = SimFight:IsRangedFaction("ngami", "chuong")
        local r2 = SimFight:IsRangedFaction("duongmon", "tieu")
        local r3 = SimFight:IsRangedFaction("vodang", "khi")
        local r4 = SimFight:IsRangedFaction("ngudoc", "chuong")
        local m1 = SimFight:IsRangedFaction("thieulam", "dao")
        local m2 = SimFight:IsRangedFaction("thienvuong", "thuong")
        local m3 = SimFight:IsRangedFaction("caibang", "bong")

        return r1, r2, r3, r4, m1, m2, m3
        """)
        r1, r2, r3, r4, m1, m2, m3 = res
        self.assertEqual(r1, 1)
        self.assertEqual(r2, 1)
        self.assertEqual(r3, 1)
        self.assertEqual(r4, 1)
        self.assertEqual(m1, 0)
        self.assertEqual(m2, 0)
        self.assertEqual(m3, 0)

    def test_combat_ranged_kiting_vector_calculation(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        -- Bot at (100, 100), Enemy at (104, 100) -> Enemy is East, Bot should kite West (dx = -4, dest = 94, 100)
        local kx, ky = SimFight:CalculateKiteTile(100, 100, 104, 100, 6)
        return kx, ky
        """)
        kx, ky = res
        self.assertEqual(kx, 94)
        self.assertEqual(ky, 100)

    def test_combat_ranged_kiting_execution_in_update(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local runCalled = 0
        local runTargetX, runTargetY = 0, 0
        NpcRun = function(idx, x, y)
            runCalled = runCalled + 1
            runTargetX = x
            runTargetY = y
        end

        local tbNpc = {
            finalIndex = 1001,
            faction = "ngami",
            level = 100,
            nMapId = 53,
            fighting = 1,
            isFighting = 1,
            tick_breath = 100,
            tick_canCast = 0,
            combatState = SIM_COMBAT_STATE.PEACE,
            foundNpcEnemy = 2002
        }

        GetNpcPos = function(idx)
            if idx == 1001 then
                return 3200, 3200, 53 -- Bot at tile (100, 100)
            else
                return 3264, 3200, 53 -- Enemy at tile (102, 100), dist = 2 < 4 -> Trigger Kite
            end
        end

        execCastNormalSkill(SimFight.Citizen, nil, tbNpc)
        local stateAfter = tbNpc.combatState

        return runCalled > 0, runTargetX, runTargetY, stateAfter
        """)
        runCalled, rx, ry, stateAfter = res
        self.assertTrue(runCalled)
        self.assertEqual(stateAfter, "KITE")
        self.assertEqual(rx, 94)
        self.assertEqual(ry, 100)

    def test_combat_melee_closing_and_combo(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local runCalled = 0
        local castCalled = 0
        NpcRun = function(idx, x, y) runCalled = runCalled + 1 end
        NpcCastSkill = function(idx, sk, lv, x, y) castCalled = castCalled + 1 end

        local tbNpc = {
            finalIndex = 1001,
            faction = "thieulam",
            weaponBranch = "dao",
            level = 100,
            nMapId = 53,
            fighting = 1,
            isFighting = 1,
            tick_breath = 100,
            tick_canCast = 0,
            combatState = SIM_COMBAT_STATE.PEACE,
            foundNpcEnemy = 2002
        }

        -- Step 1: Enemy at tile (108, 100), dist = 8 > maxCastTiles (2) -> Engaging
        GetNpcPos = function(idx)
            if idx == 1001 then return 3200, 3200, 53
            else return 3456, 3200, 53 end
        end

        execCastNormalSkill(SimFight.Citizen, nil, tbNpc)
        local stateEngaging = tbNpc.combatState
        local run1 = runCalled

        -- Step 2: Enemy at tile (101, 100), dist = 1 <= maxCastTiles (2) -> Combo
        tbNpc.tick_canCast = 0
        GetNpcPos = function(idx)
            if idx == 1001 then return 3200, 3200, 53
            else return 3232, 3200, 53 end
        end

        execCastNormalSkill(SimFight.Citizen, nil, tbNpc)
        local stateCombo = tbNpc.combatState
        local cast1 = castCalled

        return stateEngaging, run1 > 0, stateCombo, cast1 > 0
        """)
        stateEngaging, ran, stateCombo, cast = res
        self.assertEqual(stateEngaging, "ENGAGING")
        self.assertTrue(ran)
        self.assertEqual(stateCombo, "COMBO")
        self.assertTrue(cast)

    def test_combat_target_prioritization_player_over_npc(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local tbNpc = {
            finalIndex = 1001,
            nMapId = 53,
            isPlayerEnemyAround = 5,
            foundNpcEnemy = 2002
        }

        GetNpcPos = function(idx) return 3200, 3200, 53 end
        CallPlayerFunction = function(pId, fn) return 53, 102, 102 end

        local target = SimFight:SelectBestTarget(nil, tbNpc)
        return target.targetType, target.targetId
        """)
        targetType, targetId = res
        self.assertEqual(targetType, "player")
        self.assertEqual(targetId, 5)

    def test_combat_low_hp_retreat_heal(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local healCalled = 0
        EnforceBotHp = function(idx, amount)
            healCalled = healCalled + 1
        end
        NPCINFO_GetNpcCurrentLife = function(idx) return 200 end
        NPCINFO_GetNpcCurrentMaxLife = function(idx) return 1000 end -- 20% HP

        local tbNpc = {
            finalIndex = 1001,
            faction = "vodang",
            level = 100,
            nMapId = 53,
            fighting = 1,
            isFighting = 1,
            tick_breath = 100,
            tick_canCast = 0,
            combatState = SIM_COMBAT_STATE.PEACE,
            foundNpcEnemy = 2002
        }
        GetNpcPos = function(idx) return 3200, 3200, 53 end

        execCastNormalSkill(SimFight.Citizen, nil, tbNpc)
        return tbNpc.combatState, healCalled > 0
        """)
        combatState, healed = res
        self.assertEqual(combatState, "RETREAT_HEAL")
        self.assertTrue(healed)

    def test_combat_stuck_recovery_while_chasing(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local dashCalled = 0
        BotDashTo = function(idx, x, y, speed) dashCalled = dashCalled + 1 end

        local tbNpc = {
            id = 1,
            finalIndex = 1001,
            moveState = SIM_MOVE_STATE.CHASE,
            isFighting = 1,
            stuckTicks = 0,
            stuckRecoveries = 0
        }

        -- Baseline
        local s0 = SimMovement:CheckStuck(tbNpc, 100, 100)
        -- 5 consecutive stationary ticks while chasing in combat
        local s1 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s2 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s3 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s4 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s5 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local ticksBefore = tbNpc.stuckTicks

        local recovered = 0
        if s5 == 1 then
            recovered = SimMovement:HandleStuck(nil, tbNpc, 100, 100)
        end
        local ticksAfter = tbNpc.stuckTicks
        local countAfter = tbNpc.stuckRecoveries

        return s5 == 1, ticksBefore, recovered == 1, dashCalled, ticksAfter, countAfter
        """)
        s5_stuck, tBefore, rec_ok, dashes, tAfter, cntAfter = res
        self.assertTrue(s5_stuck)
        self.assertEqual(tBefore, 5)
        self.assertTrue(rec_ok)
        self.assertGreater(dashes, 0)
        self.assertEqual(tAfter, 0)
        self.assertEqual(cntAfter, 1)

    def test_combat_stuck_recovery_while_kiting(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local dashCalled = 0
        BotDashTo = function(idx, x, y, speed) dashCalled = dashCalled + 1 end

        local tbNpc = {
            id = 1,
            finalIndex = 1001,
            moveState = SIM_MOVE_STATE.KITE,
            isFighting = 1,
            stuckTicks = 0,
            stuckRecoveries = 0
        }

        local s0 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s1 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s2 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s3 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s4 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s5 = SimMovement:CheckStuck(tbNpc, 100, 100)

        local recovered = 0
        if s5 == 1 then
            recovered = SimMovement:HandleStuck(nil, tbNpc, 100, 100)
        end

        return s5 == 1, recovered == 1, tbNpc.stuckTicks, tbNpc.stuckRecoveries
        """)
        s5_stuck, rec_ok, tAfter, cntAfter = res
        self.assertTrue(s5_stuck)
        self.assertTrue(rec_ok)
        self.assertEqual(tAfter, 0)
        self.assertEqual(cntAfter, 1)

    def test_combat_no_false_stuck_while_casting_in_place(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local tbNpc = {
            id = 1,
            finalIndex = 1001,
            moveState = SIM_MOVE_STATE.IDLE,
            combatState = "COMBO",
            isFighting = 1,
            stuckTicks = 0
        }

        local s0 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s1 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s2 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s3 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s4 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s5 = SimMovement:CheckStuck(tbNpc, 100, 100)

        return s0, s1, s2, s3, s4, s5, tbNpc.stuckTicks
        """)
        s0, s1, s2, s3, s4, s5, tTicks = res
        self.assertEqual(s0, 0)
        self.assertEqual(s1, 0)
        self.assertEqual(s2, 0)
        self.assertEqual(s3, 0)
        self.assertEqual(s4, 0)
        self.assertEqual(s5, 0)
        self.assertEqual(tTicks, 0)

    def test_combat_chase_to_combo_suppresses_stuck_recovery(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local dashCalled = 0
        BotDashTo = function(idx, x, y, speed) dashCalled = dashCalled + 1 end

        local tbNpc = {
            finalIndex = 1001,
            faction = "thieulam",
            weaponBranch = "dao",
            level = 100,
            nMapId = 53,
            fighting = 1,
            isFighting = 1,
            moveState = SIM_MOVE_STATE.CHASE,
            combatState = SIM_COMBAT_STATE.ENGAGING,
            tick_breath = 100,
            tick_canCast = 0,
            foundNpcEnemy = 2002,
            stuckTicks = 0
        }

        -- Step 1: Enemy is within cast range (tile 101, 100) -> execCastNormalSkill enters COMBO
        GetNpcPos = function(idx)
            if idx == 1001 then return 3200, 3200, 53
            else return 3232, 3200, 53 end
        end

        execCastNormalSkill(SimFight.Citizen, nil, tbNpc)
        local cState = tbNpc.combatState
        local mState = tbNpc.moveState

        -- Step 2: 5 subsequent checks while casting/cooling down at same coordinate (100, 100)
        local s1 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s2 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s3 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s4 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s5 = SimMovement:CheckStuck(tbNpc, 100, 100)

        return cState, mState, s5, dashCalled, tbNpc.stuckTicks
        """)
        cState, mState, s5, dashes, stuckTicks = res
        self.assertEqual(cState, "COMBO")
        self.assertEqual(mState, "IDLE")
        self.assertEqual(s5, 0)
        self.assertEqual(dashes, 0)
        self.assertEqual(stuckTicks, 0)

    def test_combat_kite_to_combo_suppresses_stuck_recovery(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local dashCalled = 0
        BotDashTo = function(idx, x, y, speed) dashCalled = dashCalled + 1 end

        local tbNpc = {
            finalIndex = 1001,
            faction = "ngami",
            weaponBranch = "chuong",
            level = 100,
            nMapId = 53,
            fighting = 1,
            isFighting = 1,
            moveState = SIM_MOVE_STATE.KITE,
            combatState = SIM_COMBAT_STATE.KITE,
            tick_breath = 100,
            tick_canCast = 0,
            foundNpcEnemy = 2002,
            stuckTicks = 0
        }

        -- Step 1: Enemy is at distance 6 (within max cast range, safe distance >= 4) -> enters COMBO
        SimProgression.GetSkillAttackRadiusTiles = function(self, sk) return 6 end
        GetNpcPos = function(idx)
            if idx == 1001 then return 3200, 3200, 53
            else return 3392, 3200, 53 end
        end

        execCastNormalSkill(SimFight.Citizen, nil, tbNpc)
        local cState = tbNpc.combatState
        local mState = tbNpc.moveState

        -- Step 2: 5 checks while stationary casting
        local s1 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s2 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s3 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s4 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s5 = SimMovement:CheckStuck(tbNpc, 100, 100)

        return cState, mState, s5, dashCalled, tbNpc.stuckTicks
        """)
        cState, mState, s5, dashes, stuckTicks = res
        self.assertEqual(cState, "COMBO")
        self.assertEqual(mState, "IDLE")
        self.assertEqual(s5, 0)
        self.assertEqual(dashes, 0)
        self.assertEqual(stuckTicks, 0)

    def test_combat_chase_with_tick_can_cast_cooling_triggers_stuck_recovery(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local dashCalled = 0
        BotDashTo = function(idx, x, y, speed) dashCalled = dashCalled + 1 end

        local tbNpc = {
            finalIndex = 1001,
            moveState = SIM_MOVE_STATE.CHASE,
            combatState = SIM_COMBAT_STATE.ENGAGING,
            isFighting = 1,
            tick_breath = 100,
            tick_canCast = 101, -- throttling/cooling active during chase
            stuckTicks = 0,
            stuckRecoveries = 0
        }

        local s0 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s1 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s2 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s3 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s4 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s5 = SimMovement:CheckStuck(tbNpc, 100, 100)

        local recovered = 0
        if s5 == 1 then
            recovered = SimMovement:HandleStuck(nil, tbNpc, 100, 100)
        end

        return s5 == 1, recovered == 1, dashCalled, tbNpc.stuckTicks, tbNpc.stuckRecoveries
        """)
        s5_stuck, rec_ok, dashes, tAfter, cntAfter = res
        self.assertTrue(s5_stuck)
        self.assertTrue(rec_ok)
        self.assertGreater(dashes, 0)
        self.assertEqual(tAfter, 0)
        self.assertEqual(cntAfter, 1)

    def test_combat_kite_with_tick_can_cast_cooling_triggers_stuck_recovery(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local dashCalled = 0
        BotDashTo = function(idx, x, y, speed) dashCalled = dashCalled + 1 end

        local tbNpc = {
            finalIndex = 1001,
            moveState = SIM_MOVE_STATE.KITE,
            combatState = SIM_COMBAT_STATE.KITE,
            isFighting = 1,
            tick_breath = 100,
            tick_canCast = 101, -- throttling/cooling active during kite
            stuckTicks = 0,
            stuckRecoveries = 0
        }

        local s0 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s1 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s2 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s3 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s4 = SimMovement:CheckStuck(tbNpc, 100, 100)
        local s5 = SimMovement:CheckStuck(tbNpc, 100, 100)

        local recovered = 0
        if s5 == 1 then
            recovered = SimMovement:HandleStuck(nil, tbNpc, 100, 100)
        end

        return s5 == 1, recovered == 1, dashCalled, tbNpc.stuckTicks, tbNpc.stuckRecoveries
        """)
        s5_stuck, rec_ok, dashes, tAfter, cntAfter = res
        self.assertTrue(s5_stuck)
        self.assertTrue(rec_ok)
        self.assertGreater(dashes, 0)
        self.assertEqual(tAfter, 0)
        self.assertEqual(cntAfter, 1)

if __name__ == '__main__':
    unittest.main()

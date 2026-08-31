import unittest
import os
import shutil
import re
import lupa
from lupa import LuaRuntime

class TestPhaseDSocialParty(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        if not os.path.exists("save/simcity"):
            os.makedirs("save/simcity")

    def tearDown(self):
        if os.path.exists("save/simcity"):
            shutil.rmtree("save/simcity", ignore_errors=True)

    def load_lua_file(self, rel_path):
        with open(rel_path, "r", encoding="latin1") as f:
            code = f.read()
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        return self.lua.execute(code)

    def init_simcity_environment(self):
        mock_env = """
        random = function(a, b)
            if not a then return 0 end
            if not b then return a end
            return a
        end
        objCopy = function(orig)
            if type(orig) == 'table' then
                local copy = {}
                for k, v in pairs(orig) do copy[k] = v end
                return copy
            end
            return orig
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
        tinsert = table.insert
        getn = function(t)
            if not t then return 0 end
            return table.getn and table.getn(t) or #t
        end

        REFRESH_RATE = 18
        CHANCE_CHAT = 1000 -- Guarantee for deterministic testing
        CHANCE_DROP_MONEY = 0
        LIFE_RESTORE_PERCENT = 1
        SIMBOT_CHAT_COOLDOWN = 30
        SIMBOT_HP_MIN = 60000
        SIMBOT_HP_MAX = 120000

        SimCityPhai = {
            id2phai = { [100] = "thieulam", [101] = "ngami", [102] = "vodang" },
            thieulam = { normalCast = {{318, 20}} },
            ngami = { normalCast = {{92, 20}} },
            vodang = { normalCast = {{267, 20}} }
        }

        SubWorldID2Idx = function(id) return id end
        SubWorldIdx2ID = function(idx) return idx end
        GetNpcPos = function(idx) return 3200, 3200, 53 end
        GetDistanceRadius = function(x1, y1, x2, y2)
            local dx = (x1 or 0) - (x2 or 0)
            local dy = (y1 or 0) - (y2 or 0)
            return math.sqrt(dx*dx + dy*dy)
        end
        NpcChat = function(idx, msg) end
        SetNpcAction = function(idx, act) end
        NpcRun = function(idx, x, y) end
        NpcCastSkill = function(idx, sk, lv, x, y) end
        NPCINFO_GetNpcCurrentLife = function(idx) return 1000 end
        NPCINFO_GetNpcCurrentMaxLife = function(idx) return 1000 end
        NPCINFO_SetNpcCurrentLife = function(idx, v) end
        SimMovementSys = function(c) return {} end
        SimFunSys = function(c) return {} end
        SimEntitySys = function(c) return {} end
        SimFightSys = function(c) return {} end
        DelNpcSafe = function(idx) end
        IncludeLib = function(...) end
        Include = function(...) end
        """
        self.lua.execute(mock_env)
        self.load_lua_file("script/global/nobitaxd/vdk/simcity/components/sim.movement.lua")
        self.load_lua_file("script/global/nobitaxd/vdk/simcity/components/sim.fight.lua")
        self.load_lua_file("script/global/nobitaxd/vdk/simcity/plugins/pchat.lua")
        self.load_lua_file("script/global/nobitaxd/vdk/simcity/components/sim.fun.lua")
        self.load_lua_file("script/global/nobitaxd/vdk/simcity/components/sim.party.lua")
        self.load_lua_file("script/global/nobitaxd/vdk/simcity/components/sim.core.lua")

    def test_personality_dialogue_trees_and_fallback(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local c1 = SimCityChat:GetChatByPersonality("aggressive", "fight")
        local c2 = SimCityChat:GetChatByPersonality("cautious", "low_hp")
        local c3 = SimCityChat:GetChatByPersonality("friendly", "idle")
        local c4 = SimCityChat:GetChatByPersonality("chatty", "kill")
        local c5 = SimCityChat:GetChatByPersonality("loner", "taunt")
        local c_fallback = SimCityChat:GetChatByPersonality("unknown_type", "non_existent_context")

        return c1 ~= nil and c1 ~= "", c2 ~= nil and c2 ~= "", c3 ~= nil and c3 ~= "", c4 ~= nil and c4 ~= "", c5 ~= nil and c5 ~= "", c_fallback ~= nil and c_fallback ~= ""
        """)
        c1, c2, c3, c4, c5, cf = res
        self.assertTrue(c1)
        self.assertTrue(c2)
        self.assertTrue(c3)
        self.assertTrue(c4)
        self.assertTrue(c5)
        self.assertTrue(cf)

    def test_chat_throttle_and_cooldown_debounce(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local chatCount = 0
        local lastMsg = ""
        NpcChat = function(idx, msg)
            chatCount = chatCount + 1
            lastMsg = msg
        end

        local tbNpc = {
            id = 1,
            finalIndex = 1001,
            personality = "friendly",
            isFighting = 0,
            tick_breath = 100,
            lastChatTick = 0,
            worldInfo = { allowChat = 1 }
        }

        -- Call 1 at tick 100 -> should chat and set lastChatTick = 100
        execChat(tbNpc, 0)
        local c1_count = chatCount
        local c1_lastTick = tbNpc.lastChatTick

        -- Call 2 at tick 102 (within 10s cooldown) -> should be throttled (no new chat)
        tbNpc.tick_breath = 102
        execChat(tbNpc, 0)
        local c2_count = chatCount

        -- Call 3 at tick 300 (past 10s cooldown: 10 * 18 = 180 ticks) -> should chat again
        tbNpc.tick_breath = 300
        execChat(tbNpc, 0)
        local c3_count = chatCount
        local c3_lastTick = tbNpc.lastChatTick

        return c1_count == 1, c1_lastTick == 100, c2_count == 1, c3_count == 2, c3_lastTick == 300
        """)
        c1_ok, c1_tick_ok, c2_throttled, c3_ok, c3_tick_ok = res
        self.assertTrue(c1_ok)
        self.assertTrue(c1_tick_ok)
        self.assertTrue(c2_throttled)
        self.assertTrue(c3_ok)
        self.assertTrue(c3_tick_ok)

    def test_nearby_player_speech_reply(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local chatMsg = ""
        NpcChat = function(idx, msg)
            chatMsg = msg
        end

        HasPlayerSay = function() return 1 end
        PollSayForBot = function(idx) return 3 end -- Category 3 -> rep_chao

        SimCityChat.rep_chao = { "Chao dai hiep, rat vui duoc gap!" }

        local tbNpc = {
            id = 1,
            finalIndex = 1001,
            personality = "friendly",
            isFighting = 0,
            tick_breath = 50,
            lastChatTick = 0
        }

        execChat(tbNpc, 0)

        return chatMsg, tbNpc.lastChatTick
        """)
        msg, lastTick = res
        self.assertEqual(msg, "Chao dai hiep, rat vui duoc gap!")
        self.assertEqual(lastTick, 50)

    def test_low_hp_panic_chat_trigger(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local chatMsg = ""
        NpcChat = function(idx, msg) chatMsg = msg end
        NPCINFO_GetNpcCurrentLife = function(idx) return 200 end
        NPCINFO_GetNpcCurrentMaxLife = function(idx) return 1000 end -- 20% HP

        local tbNpc = {
            id = 1,
            finalIndex = 1001,
            personality = "cautious",
            combatState = "RETREAT_HEAL",
            isFighting = 1,
            tick_breath = 100,
            lastChatTick = 0
        }

        execChat(tbNpc, 0)
        return chatMsg ~= "", tbNpc.lastChatTick == 100
        """)
        has_msg, tick_ok = res
        self.assertTrue(has_msg)
        self.assertTrue(tick_ok)

    def test_social_micro_emote_sitting_and_standing(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local lastAction = -1
        SetNpcAction = function(idx, act) lastAction = act end

        local tbNpc = {
            finalIndex = 1001,
            mode = "train",
            isFighting = 0,
            moveState = "IDLE",
            isSitting = 0
        }

        -- Force sitting trigger
        random = function(a, b) return 1 end
        execEmote(tbNpc)
        local isSittingAfter = tbNpc.isSitting
        local sitAction = lastAction

        -- Bot starts moving -> stands up
        tbNpc.moveState = "WANDER"
        execEmote(tbNpc)
        local standAction = lastAction
        local isSittingEnd = tbNpc.isSitting

        return isSittingAfter == 1, sitAction == 2, standAction == 1, isSittingEnd == 0
        """)
        sat_ok, act2_ok, act1_ok, stand_ok = res
        self.assertTrue(sat_ok)
        self.assertTrue(act2_ok)
        self.assertTrue(act1_ok)
        self.assertTrue(stand_ok)

    def test_virtual_party_creation_and_membership(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local leader = { id = 1, finalIndex = 1001, nMapId = 53, goX32 = 3200, goY32 = 3200 }
        local mem1 = { id = 2, finalIndex = 1002, nMapId = 53 }
        local mem2 = { id = 3, finalIndex = 1003, nMapId = 53 }

        local p = SimParty:CreateParty(leader)
        local pId = p.id
        local initialMemCount = getn(p.members)

        local join1 = SimParty:JoinParty(pId, mem1)
        local join2 = SimParty:JoinParty(pId, mem2)
        local memCountAfterJoin = getn(p.members)

        -- Test Cap (Max 8 members)
        for i = 4, 8 do
            SimParty:JoinParty(pId, { id = i, finalIndex = 1000 + i })
        end
        local countAtMax = getn(p.members)
        local join9 = SimParty:JoinParty(pId, { id = 9, finalIndex = 1009 }) -- Should fail (0)

        -- Test Leaving & Leader Re-election
        SimParty:LeaveParty(mem1)
        local countAfterMem1Leave = getn(p.members)

        SimParty:LeaveParty(leader)
        local newLeaderId = p.leaderId

        -- Empty party cleanup
        for i = 3, 8 do
            SimParty:LeaveParty({ id = i, virtualPartyId = pId })
        end
        local partyCleared = (SimParty:GetParty(pId) == nil)

        return initialMemCount == 1, join1 == 1, join2 == 1, memCountAfterJoin == 3, countAtMax == 8, join9 == 0, countAfterMem1Leave == 7, newLeaderId == 3, partyCleared
        """)
        c1, j1, j2, c3, c8, j9_fail, c7, new_lead, cleared = res
        self.assertTrue(c1)
        self.assertTrue(j1)
        self.assertTrue(j2)
        self.assertTrue(c3)
        self.assertTrue(c8)
        self.assertTrue(j9_fail)
        self.assertTrue(c7)
        self.assertTrue(new_lead)
        self.assertTrue(cleared)

    def test_virtual_party_formation_tethering(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local runCalled = 0
        local runTargetX, runTargetY = 0, 0
        NpcRun = function(idx, x, y)
            runCalled = runCalled + 1
            runTargetX = x
            runTargetY = y
        end

        local leader = { id = 1, finalIndex = 1001, isDead = 0, isFighting = 0 }
        local follower = { id = 2, finalIndex = 1002, isDead = 0, isFighting = 0, moveState = "IDLE" }

        GetNpcPos = function(idx)
            if idx == 1001 then
                return 3200, 3200, 53 -- Leader at (100, 100)
            else
                return 3840, 3200, 53 -- Follower at (120, 100), dist = 20 > 8 -> Tether
            end
        end

        local simMock = {
            Get = function(self, id)
                if id == 1 then return leader
                elseif id == 2 then return follower end
                return nil
            end
        }

        local p = SimParty:CreateParty(leader)
        SimParty:JoinParty(p.id, follower)

        SimParty:UpdatePartyMovement(simMock, p.id)

        return runCalled > 0, follower.moveState == "FOLLOW", math.abs(runTargetX - 100) <= 2
        """)
        ran, follow_state, target_near_leader = res
        self.assertTrue(ran)
        self.assertTrue(follow_state)
        self.assertTrue(target_near_leader)

    def test_virtual_party_shared_aggro_focus_fire(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local mem1 = { id = 1, finalIndex = 1001, isDead = 0, isFighting = 0 }
        local mem2 = { id = 2, finalIndex = 1002, isDead = 0, isFighting = 0 }
        local mem3 = { id = 3, finalIndex = 1003, isDead = 0, isFighting = 0 }

        local simMock = {
            Get = function(self, id)
                if id == 1 then return mem1
                elseif id == 2 then return mem2
                elseif id == 3 then return mem3 end
                return nil
            end
        }

        local p = SimParty:CreateParty(mem1)
        SimParty:JoinParty(p.id, mem2)
        SimParty:JoinParty(p.id, mem3)

        -- Mem1 is attacked by enemy NPC 5005 -> broadcast aggro
        SimParty:ShareAggroTarget(simMock, p.id, 5005, mem1)

        return p.focusTarget == 5005, mem2.foundNpcEnemy == 5005, mem2.isFighting == 1, mem3.foundNpcEnemy == 5005, mem3.isFighting == 1
        """)
        f_target, m2_target, m2_fight, m3_target, m3_fight = res
        self.assertTrue(f_target)
        self.assertTrue(m2_target)
        self.assertTrue(m2_fight)
        self.assertTrue(m3_target)
        self.assertTrue(m3_fight)

    def test_virtual_party_ngami_support_heal(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local skillCast = 0
        local skillIdCast = 0
        local skillX, skillY = 0, 0
        NpcCastSkill = function(idx, sk, lv, x, y)
            skillCast = skillCast + 1
            skillIdCast = sk
            skillX = x
            skillY = y
        end

        local ngamiBot = { id = 1, finalIndex = 1001, faction = "ngami", isDead = 0, tick_breath = 100 }
        local lowHpAlly = { id = 2, finalIndex = 1002, faction = "thieulam", isDead = 0, maxHP = 1000 }

        NPCINFO_GetNpcCurrentLife = function(idx)
            if idx == 1002 then return 400 -- 40% HP < 65% threshold
            else return 1000 end
        end
        NPCINFO_GetNpcCurrentMaxLife = function(idx) return 1000 end
        GetNpcPos = function(idx)
            if idx == 1002 then return 3300, 3300, 53
            else return 3200, 3200, 53 end
        end

        local simMock = {
            Get = function(self, id)
                if id == 1 then return ngamiBot
                elseif id == 2 then return lowHpAlly end
                return nil
            end
        }

        local p = SimParty:CreateParty(ngamiBot)
        SimParty:JoinParty(p.id, lowHpAlly)

        SimParty:OnPartyTick(simMock, p.id)

        return skillCast == 1, skillIdCast == 93, skillX == 3300, skillY == 3300, p.lastHealTick > 100
        """)
        cast_ok, sk93_ok, x_ok, y_ok, heal_tick_ok = res
        self.assertTrue(cast_ok)
        self.assertTrue(sk93_ok)
        self.assertTrue(x_ok)
        self.assertTrue(y_ok)
        self.assertTrue(heal_tick_ok)

    def test_sim_core_remove_cleans_up_party_membership(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local simCore = objCopy(SimCore)
        simCore.fighterList = {}
        simCore.removedIds = {}
        simCore.totalFighters = 3

        local leader = { id = 1, finalIndex = 1001, nMapId = 53 }
        local mem1 = { id = 2, finalIndex = 1002, nMapId = 53 }
        local mem2 = { id = 3, finalIndex = 1003, nMapId = 53 }

        simCore.fighterList[1] = leader
        simCore.fighterList[2] = mem1
        simCore.fighterList[3] = mem2

        local p = SimParty:CreateParty(leader)
        SimParty:JoinParty(p.id, mem1)
        SimParty:JoinParty(p.id, mem2)

        local initialCount = getn(p.members)

        -- 1. Remove ordinary member 2 -> member removed, party still has 2 members
        simCore:Remove(2)
        local countAfterMem1 = getn(p.members)
        local mem1PartyId = mem1.virtualPartyId

        -- 2. Remove leader 1 -> leader re-elected to member 3, party has 1 member
        simCore:Remove(1)
        local countAfterLeader = getn(p.members)
        local newLeaderId = p.leaderId
        local leaderPartyId = leader.virtualPartyId

        -- 3. Remove final member 3 -> party cleaned up from SimParty.parties
        simCore:Remove(3)
        local partyExists = (SimParty:GetParty(p.id) ~= nil)

        return initialCount == 3, countAfterMem1 == 2, mem1PartyId == nil, countAfterLeader == 1, newLeaderId == 3, leaderPartyId == nil, partyExists == false
        """)
        c3, c2, m1_nil, c1, new_lead_3, l_nil, p_none = res
        self.assertTrue(c3)
        self.assertTrue(c2)
        self.assertTrue(m1_nil)
        self.assertTrue(c1)
        self.assertTrue(new_lead_3)
        self.assertTrue(l_nil)
        self.assertTrue(p_none)

    def test_sim_citizen_live_update_drives_party_movement_and_healing(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local runCalled = 0
        local skillCast = 0
        local skillIdCast = 0

        NpcRun = function(idx, x, y)
            runCalled = runCalled + 1
        end

        NpcCastSkill = function(idx, sk, lv, x, y)
            skillCast = skillCast + 1
            skillIdCast = sk
        end

        NPCINFO_GetNpcCurrentLife = function(idx)
            if idx == 1002 then return 400 else return 1000 end
        end
        NPCINFO_GetNpcCurrentMaxLife = function(idx) return 1000 end
        GetNpcPos = function(idx)
            if idx == 1001 then return 3200, 3200, 53 -- Leader at (100, 100)
            else return 3840, 3200, 53 end -- Follower at (120, 100)
        end

        local simCitizen = objCopy(SimCore)
        simCitizen.fighterList = {}
        simCitizen.removedIds = {}
        simCitizen.totalFighters = 2
        simCitizen.currentProcessGroup = 1

        local leader = {
            id = 1,
            finalIndex = 1001,
            faction = "ngami",
            isDead = 0,
            isFighting = 0,
            tick_breath = 100,
            processGroup = 1,
            movementSys = { Move = function() end, IsActive = function() return 1 end },
            fightSys = { Update = function() end },
            funSys = { Update = function() end },
            entitySys = { Update = function() end }
        }

        local follower = {
            id = 2,
            finalIndex = 1002,
            faction = "thieulam",
            isDead = 0,
            isFighting = 0,
            tick_breath = 100,
            moveState = "IDLE",
            processGroup = 1,
            movementSys = { Move = function() end, IsActive = function() return 1 end },
            fightSys = { Update = function() end },
            funSys = { Update = function() end },
            entitySys = { Update = function() end }
        }

        simCitizen.fighterList[1] = leader
        simCitizen.fighterList[2] = follower

        local p = SimParty:CreateParty(leader)
        SimParty:JoinParty(p.id, follower)

        -- Execute standard production tick: SimCitizen:ATick()
        simCitizen:ATick(18)

        return runCalled > 0, follower.moveState == "FOLLOW", skillCast == 1, skillIdCast == 93, p.lastHealTick > 100
        """)
        ran, follow_st, cast_ok, sk93, heal_adv = res
        self.assertTrue(ran)
        self.assertTrue(follow_st)
        self.assertTrue(cast_ok)
        self.assertTrue(sk93)
        self.assertTrue(heal_adv)

    def test_sim_citizen_live_combat_drives_party_shared_aggro(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local simCitizen = objCopy(SimCore)
        simCitizen.fighterList = {}
        simCitizen.removedIds = {}
        simCitizen.totalFighters = 2
        simCitizen.currentProcessGroup = 1

        SimPickSkill = function(tbNpc) return { 318, 20 } end

        local mem1 = {
            id = 1,
            finalIndex = 1001,
            faction = "thieulam",
            isDead = 0,
            isFighting = 0,
            tick_breath = 100,
            foundNpcEnemy = 6006,
            processGroup = 1,
            movementSys = { Move = function() end },
            fightSys = SimFight.Citizen,
            funSys = { Update = function() end },
            entitySys = { Update = function() end }
        }

        local mem2 = {
            id = 2,
            finalIndex = 1002,
            faction = "vodang",
            isDead = 0,
            isFighting = 0,
            tick_breath = 100,
            foundNpcEnemy = nil,
            processGroup = 1,
            movementSys = { Move = function() end },
            fightSys = SimFight.Citizen,
            funSys = { Update = function() end },
            entitySys = { Update = function() end }
        }

        simCitizen.fighterList[1] = mem1
        simCitizen.fighterList[2] = mem2

        GetNpcPos = function(idx)
            return 3200, 3200, 53
        end

        local p = SimParty:CreateParty(mem1)
        SimParty:JoinParty(p.id, mem2)

        -- Execute fighting update on mem1
        mem1.fightSys:Update(simCitizen, mem1)

        return p.focusTarget == 6006, mem2.foundNpcEnemy == 6006, mem2.isFighting == 1, mem2.combatState == "AGGRO"
        """)
        f_target, m2_target, m2_fight, m2_aggro = res
        self.assertTrue(f_target)
        self.assertTrue(m2_target)
        self.assertTrue(m2_fight)
        self.assertTrue(m2_aggro)

    def test_phase_d_core_initialization_defaults(self):
        self.init_simcity_environment()
        res = self.lua.execute("""
        local cfg = {
            id = 1,
            finalIndex = 1001,
            nNpcId = 100
        }
        SimCore:initCharConfig(cfg)

        return cfg.personality, cfg.lastChatTick, cfg.isSitting, cfg.virtualPartyId
        """)
        personality, lastChat, sitting, partyId = res
        self.assertEqual(personality, "friendly")
        self.assertEqual(lastChat, 0)
        self.assertEqual(sitting, 0)
        self.assertIsNone(partyId)

if __name__ == '__main__':
    unittest.main()

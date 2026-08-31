--========================================================
-- SIMBOT VIRTUAL PARTY SUBSYSTEM (PHASE D)
-- Pure ANSI / Windows-1258 Encoding
--========================================================

SimParty = {}
SimParty.parties = {}
SimParty.nextPartyId = 1

-- Create a new virtual party
function SimParty:CreateParty(leaderNpc)
    if not leaderNpc then return nil end
    local pId = self.nextPartyId
    self.nextPartyId = self.nextPartyId + 1

    local newParty = {
        id = pId,
        leaderId = leaderNpc.id,
        leaderIndex = leaderNpc.finalIndex,
        members = { leaderNpc.id },
        mapId = leaderNpc.nMapId,
        camp = leaderNpc.camp,
        focusTarget = nil,
        anchorX = leaderNpc.goX32 or 0,
        anchorY = leaderNpc.goY32 or 0,
        lastHealTick = 0,
        formationRadius = 6
    }

    self.parties[pId] = newParty
    leaderNpc.virtualPartyId = pId
    return newParty
end

-- Add member to existing party
function SimParty:JoinParty(partyId, tbNpc)
    if not tbNpc or not partyId then return 0 end
    local p = self.parties[partyId]
    if not p then return 0 end
    if getn(p.members) >= 8 then return 0 end -- Max 8 members like JX1 party

    for i = 1, getn(p.members) do
        if p.members[i] == tbNpc.id then return 1 end
    end

    tinsert(p.members, tbNpc.id)
    tbNpc.virtualPartyId = partyId
    return 1
end

-- Leave party (supports tbNpc table or (nListId, partyId))
function SimParty:LeaveParty(tbNpc, partyId)
    if not tbNpc then return end
    local pId = (type(tbNpc) == "table" and tbNpc.virtualPartyId) or partyId
    local botId = (type(tbNpc) == "table" and tbNpc.id) or tbNpc
    if not pId then return end

    local p = self.parties[pId]
    if p then
        local newMems = {}
        for i = 1, getn(p.members) do
            if p.members[i] ~= botId then
                tinsert(newMems, p.members[i])
            end
        end
        p.members = newMems
        if getn(p.members) == 0 then
            self.parties[pId] = nil
        elseif p.leaderId == botId then
            p.leaderId = p.members[1]
        end
    end
    if type(tbNpc) == "table" then
        tbNpc.virtualPartyId = nil
    end
end

function SimParty:GetParty(partyId)
    if not partyId then return nil end
    return self.parties[partyId]
end

-- Auto-form or join party for unpartied bots on the same map and camp
function SimParty:AutoFormParty(simInstance, tbNpc)
    if not tbNpc or tbNpc.virtualPartyId or tbNpc.isDead == 1 or not tbNpc.nMapId then
        return nil
    end

    for pId, p in self.parties do
        if p.mapId == tbNpc.nMapId and getn(p.members) < 8 then
            local leader = simInstance and simInstance.Get and simInstance:Get(p.leaderId)
            if leader and leader.isDead == 0 and (not tbNpc.camp or leader.camp == tbNpc.camp) then
                self:JoinParty(pId, tbNpc)
                return p
            end
        end
    end

    return self:CreateParty(tbNpc)
end

-- Broadcast aggro target across party
function SimParty:ShareAggroTarget(simInstance, partyId, attackerIdx, victimNpc)
    if not partyId or not attackerIdx or attackerIdx <= 0 then return end
    local p = self.parties[partyId]
    if not p or not simInstance then return end

    if p.focusTarget == attackerIdx then return end
    p.focusTarget = attackerIdx

    for i = 1, getn(p.members) do
        local mem = simInstance:Get(p.members[i])
        if mem and mem.isDead == 0 and mem.finalIndex and mem.finalIndex > 0 then
            if not mem.foundNpcEnemy or mem.foundNpcEnemy <= 0 then
                mem.foundNpcEnemy = attackerIdx
                mem.isFighting = 1
                if SimFight and SimFight.SetCombatState then
                    SimFight:SetCombatState(mem, "AGGRO", "party assist focus fire")
                end
            end
        end
    end
end

-- Party formation tethering
function SimParty:UpdatePartyMovement(simInstance, partyId)
    if not partyId or not simInstance then return end
    local p = self.parties[partyId]
    if not p then return end

    local leader = simInstance:Get(p.leaderId)
    if not leader or leader.isDead == 1 or not leader.finalIndex then return end

    local lx32, ly32, lw = GetNpcPos(leader.finalIndex)
    if not lx32 then return end
    local lTileX = floor(lx32 / 32)
    local lTileY = floor(ly32 / 32)

    p.anchorX = lx32
    p.anchorY = ly32

    for i = 1, getn(p.members) do
        local memId = p.members[i]
        if memId ~= leader.id then
            local mem = simInstance:Get(memId)
            if mem and mem.isDead == 0 and mem.finalIndex and mem.finalIndex > 0 and mem.isFighting == 0 then
                local mx32, myY32, mw = GetNpcPos(mem.finalIndex)
                if mx32 and mw == lw then
                    local mTileX = floor(mx32 / 32)
                    local mTileY = floor(myY32 / 32)
                    local dist = GetDistanceRadius(mTileX, mTileY, lTileX, lTileY)
                    -- If follower drifted away from leader (> 8 tiles), walk back to leader formation
                    if dist > 8 then
                        if SimMovement and SimMovement.SetState then
                            SimMovement:SetState(mem, "FOLLOW", "party tethering")
                        end
                        if NpcRun then
                            local offsetX = mod(i * 3, 5) - 2
                            local offsetY = mod(i * 2, 5) - 2
                            NpcRun(mem.finalIndex, lTileX + offsetX, lTileY + offsetY)
                        end
                    end
                end
            end
        end
    end
end

-- Party update tick: Focus fire target & Nga Mi support heal
function SimParty:OnPartyTick(simInstance, partyId)
    local p = self.parties[partyId]
    if not p or not simInstance then return end

    -- Find leader
    local leader = simInstance:Get(p.leaderId)
    if not leader or leader.isDead == 1 then return end

    -- Shared target: If leader has a target, members share it
    if leader.foundNpcEnemy and leader.foundNpcEnemy > 0 then
        p.focusTarget = leader.foundNpcEnemy
    end

    -- Support heal: If party has a Nga Mi member, heal low-HP allies
    local nowTick = leader.tick_breath or 0
    local refreshRate = REFRESH_RATE or 18
    if (p.lastHealTick or 0) <= nowTick then
        for i = 1, getn(p.members) do
            local mem = simInstance:Get(p.members[i])
            if mem and mem.faction == "ngami" and mem.isDead == 0 and mem.finalIndex and mem.finalIndex > 0 then
                -- Look for lowest HP member
                for j = 1, getn(p.members) do
                    local ally = simInstance:Get(p.members[j])
                    if ally and ally.isDead == 0 and ally.finalIndex and ally.finalIndex > 0 then
                        local curLife = (NPCINFO_GetNpcCurrentLife and NPCINFO_GetNpcCurrentLife(ally.finalIndex)) or ally.lastHP or ally.maxHP or 1000
                        local maxLife = (NPCINFO_GetNpcCurrentMaxLife and NPCINFO_GetNpcCurrentMaxLife(ally.finalIndex)) or ally.maxHP or 2000
                        if maxLife > 0 and (curLife / maxLife) < 0.65 then
                            -- Cast Tu Hang Pho Do (Skill 93) or Nga Mi support
                            local ax32, ay32, aw = GetNpcPos(ally.finalIndex)
                            if ax32 and NpcCastSkill then
                                NpcCastSkill(mem.finalIndex, 93, 20, ax32, ay32)
                                p.lastHealTick = nowTick + (5 * 18 / refreshRate)
                                if SimCityChat and SimCityChat.GetContextChat and NpcChat then
                                    NpcChat(mem.finalIndex, "Tu Hang Pho Do!")
                                end
                                break
                            end
                        end
                    end
                end
            end
        end
    end
end

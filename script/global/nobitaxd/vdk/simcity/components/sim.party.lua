--========================================================
-- SIMBOT VIRTUAL PARTY SUBSYSTEM (PHASE 6)
-- Pure ASCII / ANSI Encoding
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
        focusTarget = nil,
        anchorX = leaderNpc.goX32 or 0,
        anchorY = leaderNpc.goY32 or 0,
        lastHealTick = 0
    }

    self.parties[pId] = newParty
    leaderNpc.virtualPartyId = pId
    return newParty
end

-- Add member to existing party
function SimParty:JoinParty(partyId, tbNpc)
    if not tbNpc then return 0 end
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

-- Leave party
function SimParty:LeaveParty(tbNpc)
    if not tbNpc or not tbNpc.virtualPartyId then return end
    local p = self.parties[tbNpc.virtualPartyId]
    if p then
        local newMems = {}
        for i = 1, getn(p.members) do
            if p.members[i] ~= tbNpc.id then
                tinsert(newMems, p.members[i])
            end
        end
        p.members = newMems
        if getn(p.members) == 0 then
            self.parties[tbNpc.virtualPartyId] = nil
        elseif p.leaderId == tbNpc.id then
            p.leaderId = p.members[1]
        end
    end
    tbNpc.virtualPartyId = nil
end

-- Party update tick: Focus fire target & Nga Mi support heal
function SimParty:OnPartyTick(simInstance, partyId)
    local p = self.parties[partyId]
    if not p then return end

    -- Find leader
    local leader = simInstance:Get(p.leaderId)
    if not leader or leader.isDead == 1 then return end

    -- Shared target: If leader has a target, members share it
    if leader.targetEnemy and leader.targetEnemy > 0 then
        p.focusTarget = leader.targetEnemy
    end

    -- Support heal: If party has a Nga Mi member, heal low-HP allies
    local nowTick = leader.tick_breath or 0
    if p.lastHealTick <= nowTick then
        for i = 1, getn(p.members) do
            local mem = simInstance:Get(p.members[i])
            if mem and mem.faction == "ngami" and mem.isDead == 0 and mem.finalIndex then
                -- Look for lowest HP member
                for j = 1, getn(p.members) do
                    local ally = simInstance:Get(p.members[j])
                    if ally and ally.isDead == 0 and ally.finalIndex then
                        local curLife = (NPCINFO_GetNpcCurrentLife and NPCINFO_GetNpcCurrentLife(ally.finalIndex)) or ally.lastHP or ally.maxHP
                        local maxLife = ally.maxHP or 2000
                        if (curLife / maxLife) < 0.65 then
                            -- Cast Tu Hang Pho Do (Skill 93) or Nga Mi buff
                            local ax32, ay32 = GetNpcPos(ally.finalIndex)
                            if ax32 and NpcCastSkill then
                                NpcCastSkill(mem.finalIndex, 93, 20, ax32, ay32)
                                p.lastHealTick = nowTick + 5*18/REFRESH_RATE
                                break
                            end
                        end
                    end
                end
            end
        end
    end
end

--========================================================
-- SIMBOT SOCIAL, FUN & CHAT SUBSYSTEM (PHASE D)
-- Pure ANSI / Windows-1258 Encoding
--========================================================

SIM_SAY_REPLY = {[0]="rep_chung",[1]="rep_ok",[2]="rep_no",[3]="rep_chao",[4]="rep_giaodich",[5]="rep_boss"}

function execChat(tbNpc, isKeoXe)
    if not tbNpc or not tbNpc.finalIndex or tbNpc.finalIndex <= 0 or tbNpc.isDead == 1 then
        return
    end

    local nowBreath = tbNpc.tick_breath or 0

    -- 1. Nearby player speech reply (Keyword response from C layer)
    if HasPlayerSay and HasPlayerSay() == 1 then
        local cat = PollSayForBot(tbNpc.finalIndex)
        if cat and cat >= 0 and SimCityChat then
            local t = SIM_SAY_REPLY[cat] or "rep_chung"
            if SimCityChat[t] and getn(SimCityChat[t]) > 0 then
                local msg = SimCityChat[t][random(1, getn(SimCityChat[t]))]
                if NpcChat then NpcChat(tbNpc.finalIndex, msg) end
                tbNpc.lastChatTick = nowBreath
                return
            end
        end
    end

    -- 2. Local Chat Throttle (Minimum 10s between random chats)
    local localCooldownTicks = 10 * 18 / (REFRESH_RATE or 18)
    if tbNpc.lastChatTick and (tbNpc.lastChatTick + localCooldownTicks > nowBreath) then
        return
    end

    -- 3. Context & Personality-driven Chat
    local allowChat = (isKeoXe == 1) or (not tbNpc.worldInfo) or (tbNpc.worldInfo.allowChat == 1)
    if allowChat then
        -- Low HP panic shout
        if NPCINFO_GetNpcCurrentLife and NPCINFO_GetNpcCurrentMaxLife then
            local cl = NPCINFO_GetNpcCurrentLife(tbNpc.finalIndex)
            local ml = NPCINFO_GetNpcCurrentMaxLife(tbNpc.finalIndex)
            if cl and ml and ml > 0 and (cl / ml) < 0.25 and (tbNpc.combatState == "RETREAT_HEAL" or tbNpc.isFighting == 1) then
                if random(1, 100) <= 30 then
                    local msg = (SimCityChat and SimCityChat.GetContextChat and SimCityChat:GetContextChat(tbNpc, "low_hp")) or "Cuu voi!"
                    if NpcChat then NpcChat(tbNpc.finalIndex, msg) end
                    tbNpc.lastChatTick = nowBreath
                    return
                end
            end
        end

        -- Combat shouts
        if tbNpc.isFighting == 1 or tbNpc.tongkim == 1 or tbNpc.mode == "chiendau" or tbNpc.combatState == "ENGAGING" or tbNpc.combatState == "COMBO" then
            local fightChance = (tbNpc.personality == "aggressive" and 25) or (tbNpc.personality == "chatty" and 20) or (CHANCE_CHAT or 10)
            if random(1, 1000) <= fightChance then
                local msg = (SimCityChat and SimCityChat.GetContextChat and SimCityChat:GetContextChat(tbNpc, "fight")) or (SimCityChat and SimCityChat.getChatFight and SimCityChat:getChatFight()) or "Nhao vo!"
                if NpcChat then NpcChat(tbNpc.finalIndex, msg) end
                tbNpc.lastChatTick = nowBreath
                return
            end
        else
            -- Idle chatter
            local idleChance = (tbNpc.personality == "chatty" and 30) or (tbNpc.personality == "loner" and 2) or (CHANCE_CHAT or 10)
            if random(1, 1000) <= idleChance then
                local msg = (SimCityChat and SimCityChat.GetContextChat and SimCityChat:GetContextChat(tbNpc, "idle")) or (SimCityChat and SimCityChat.getChat and SimCityChat:getChat()) or "Chao ban!"
                if NpcChat then NpcChat(tbNpc.finalIndex, msg) end
                tbNpc.lastChatTick = nowBreath
                return
            end
        end
    end

    -- 4. Debug showing ID
    if not isKeoXe and tbNpc.worldInfo and (tbNpc.worldInfo.showingId == 1) then
        if NpcChat then NpcChat(tbNpc.finalIndex, (tbNpc.id or 0) .. " " .. (tbNpc.nNpcId or 0)) end
    end
end

function execEmote(tbNpc)
    if not tbNpc or not tbNpc.finalIndex or tbNpc.finalIndex <= 0 or tbNpc.isDead == 1 then
        return
    end

    -- Idle sitting / resting in safe zones
    if tbNpc.isFighting == 0 and tbNpc.mode ~= "chiendau" then
        if (tbNpc.moveState == "IDLE" or tbNpc.moveState == "REST") and random(1, 1000) <= 5 then
            tbNpc.isSitting = 1
            if SetNpcAction then SetNpcAction(tbNpc.finalIndex, 2) end -- 2 = Sit / Rest action in JX1
        elseif tbNpc.isSitting == 1 and (tbNpc.moveState ~= "IDLE" and tbNpc.moveState ~= "REST") then
            tbNpc.isSitting = 0
            if SetNpcAction then SetNpcAction(tbNpc.finalIndex, 1) end -- 1 = Stand / Walk
        end
    end
end

function execRotDropMoney(tbNpc)
    if not tbNpc or not tbNpc.finalIndex or tbNpc.finalIndex <= 0 then return end
    if random(1, 10000) <= (CHANCE_DROP_MONEY or 1) then
        if NpcDropMoney then NpcDropMoney(tbNpc.finalIndex, random(1000, 10000), -1) end
    end

    if tbNpc.isAttractionAround == 203 then
        if random(1, 10000) <= (CHANCE_DROP_MONEY or 1) then
            local nX, nY, nMapIndex = GetNpcPos(tbNpc.finalIndex)
            if nX and DropItem and SubWorldID2Idx then
                for i = 1, 10 do 
                    DropItem(SubWorldID2Idx(nMapIndex), nX, nY, -1, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                end
            end
        end
    end

    if tbNpc.isAttractionAround == 384 then
        if random(1, 10000) <= (CHANCE_DROP_MONEY or 1) then
            local nX, nY, nMapIndex = GetNpcPos(tbNpc.finalIndex)
            if nX and DropItem and SubWorldID2Idx then
                for i = 1, 3 do 
                    DropItem(SubWorldID2Idx(nMapIndex), nX, nY, -1, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                end
            end
        end
    end 
end

function execRestoreLife(tbNpc)
    if not tbNpc or tbNpc.isDead == 1 or not tbNpc.finalIndex or tbNpc.finalIndex <= 0 then
        return
    end

    local refreshRate = REFRESH_RATE or 18
    if (tbNpc.tick_breath or 0) > 0 and (LIFE_RESTORE_PERCENT or 1) > 0 and mod(tbNpc.tick_breath, 10*18/refreshRate) == 0 then
        local currentLife = (NPCINFO_GetNpcCurrentLife and NPCINFO_GetNpcCurrentLife(tbNpc.finalIndex))
        local maxLife = (NPCINFO_GetNpcCurrentMaxLife and NPCINFO_GetNpcCurrentMaxLife(tbNpc.finalIndex))

        if tbNpc.faction == "ngami" and tbNpc.fightSys and tbNpc.fightSys.execCastOnSelf then
            return tbNpc.fightSys:execCastOnSelf(tbNpc)            
        end 

        if currentLife and maxLife and currentLife < maxLife then
            local restoreAmount = 3000
            local newLife = currentLife + restoreAmount
            if newLife > maxLife then newLife = maxLife end
            if NPCINFO_SetNpcCurrentLife then
                NPCINFO_SetNpcCurrentLife(tbNpc.finalIndex, newLife)
            end
        end
    end
end

function execAddScoreToAroundNPC(self, fighter, finalIndex)
    if not fighter or not finalIndex then return end
    local currRank = fighter.rank or 1
    local scoreTotal = currRank * 1000

    if not GetNpcAroundNpcList then return end
    local allNpcs, nCount = GetNpcAroundNpcList(finalIndex, 15)
    local found = {}
    nCount = nCount or (allNpcs and getn and getn(allNpcs)) or 0
    if nCount > 0 then
        for i = 1, nCount do
            local fighter2Kind = (GetNpcKind and GetNpcKind(allNpcs[i])) or 0
            local fighter2Camp = (GetNpcCurCamp and GetNpcCurCamp(allNpcs[i])) or 0
            if fighter2Kind == 0 and fighter2Camp ~= fighter.camp then
                local nListId2 = (GetNpcParam and GetNpcParam(allNpcs[i], PARAM_LIST_ID or 1)) or 0
                if nListId2 > 0 then
                    tinsert(found, nListId2)
                end
            end
        end
    end

    local N = getn(found)
    for i = 1, N do
        local fighter2 = self and self.fighterList and self.fighterList[found[i]]
        if fighter2 and fighter2.id ~= fighter.id and fighter2.isFighting == 1 then
            fighter2.fightingScore = ceil(fighter2.fightingScore + (scoreTotal / N) + (scoreTotal / N) * (fighter2.rank or 1) / 10)
            if SimCityTongKim and SimCityTongKim.updateRank then
                SimCityTongKim:updateRank(fighter2)
            end
        end
    end
end
 
function execFindDialogNpcAround(tbNpc)
    if not tbNpc or tbNpc.mode ~= "thanhthi" then   
        if tbNpc then tbNpc.isAttractionAround = 0 end
        return 0
    end

    if (tbNpc.walkMode == "preset" or tbNpc.walkMode == "formation") and tbNpc.worldInfo and tbNpc.worldInfo.presetPaths and tbNpc.currentPathIndex and tbNpc.currentPointIndex then    
        local pt = tbNpc.worldInfo.presetPaths[tbNpc.currentPathIndex][tbNpc.currentPointIndex]
        if pt and getNodeInfoByNodeName then
            tbNpc.isAttractionAround = getNodeInfoByNodeName(tbNpc, pt).isNearAtraction or 0
            return tbNpc.isAttractionAround
        end
    elseif tbNpc.nPosId and tbNpc.nPosId ~= "none" and tbNpc.worldInfo and tbNpc.worldInfo.nodes and tbNpc.worldInfo.nodes[tbNpc.nPosId] then
        if getNodeInfoByNodeName then
            tbNpc.isAttractionAround = getNodeInfoByNodeName(tbNpc, tbNpc.nPosId).isNearAtraction or 0
            return tbNpc.isAttractionAround
        end
    end 

    tbNpc.isAttractionAround = 0
    return 0
end

SimFun = {}

SimFun.Base = {
    Update = function(self, tbNpc)
    end,
    OnDeath = function(self, tbNpc, finalIndex)
    end
}

SimFun.Citizen = {
    Update = function(self, tbNpc)
        if not tbNpc or tbNpc.isDead == 1 then return end

        if tbNpc.mode ~= "chiendau" then
            execFindDialogNpcAround(tbNpc)
            execRotDropMoney(tbNpc)
            execEmote(tbNpc)
        end
                
        execChat(tbNpc, 0)
        execRestoreLife(tbNpc)
    end,

    OnDeath = function(self, simInstance, tbNpc, finalIndex, attackerIndex)
        if not tbNpc then return end

        -- Kill taunt from attacker if bot
        if attackerIndex and attackerIndex > 0 and simInstance and simInstance.Get then
            local killer = simInstance:Get(attackerIndex)
            if killer and killer.finalIndex and killer.finalIndex > 0 and killer.isDead == 0 then
                local kMsg = (SimCityChat and SimCityChat.GetContextChat and SimCityChat:GetContextChat(killer, "kill")) or "Xong viec!"
                if NpcChat then NpcChat(killer.finalIndex, kMsg) end
            end
        end

        if tbNpc.tongkim == 1 then
            if not PlayerIndex or PlayerIndex == 0 then
                execAddScoreToAroundNPC(simInstance, tbNpc, finalIndex)            
            else
                if SimCityTongKim and SimCityTongKim.OnDeath then
                    SimCityTongKim:OnDeath(tbNpc.finalIndex, tbNpc.rank or 1, attackerIndex)
                end
            end
        elseif tbNpc.mode ~= "chiendau" then
            if random(1, 1000) <= (CHANCE_DROP_MONEY or 1) then
                if NpcDropMoney then NpcDropMoney(tbNpc.finalIndex, random(1000, 100000), -1) end
            end
        end
    end
}

SimFun.KeoXe = {
    Update = function(self, tbNpc)
        if not tbNpc or tbNpc.isDead == 1 then return end
        execChat(tbNpc, 1)
        execRestoreLife(tbNpc)
    end,
    OnDeath = function(self, simInstance, tbNpc, finalIndex, attackerIndex)
    end
} 

function SimFunSys(tbNpc)    
    if not tbNpc then return SimFun.Base end
    if tbNpc.role == "citizen" then
        return SimFun.Citizen
    end
    if tbNpc.role == "keoxe" then
        return SimFun.KeoXe
    end
    return SimFun.Base
end

SIM_COMBAT_STATE = {
    PEACE = "PEACE",
    AGGRO = "AGGRO",
    ENGAGING = "ENGAGING",
    COMBO = "COMBO",
    COOLDOWN = "COOLDOWN",
    KITE = "KITE",
    RETREAT_HEAL = "RETREAT_HEAL"
}

SimFight = SimFight or {}

function SimFight:SetCombatState(tbNpc, newState, reason)
    if not tbNpc then return end
    local oldState = tbNpc.combatState or SIM_COMBAT_STATE.PEACE
    if oldState ~= newState then
        tbNpc.combatState = newState
        tbNpc.combatStateChangeTick = tbNpc.tick_breath or 0
        tbNpc.combatStateReason = reason
    end
    return newState
end

function SimFight:GetCombatState(tbNpc)
    if not tbNpc then return SIM_COMBAT_STATE.PEACE end
    return tbNpc.combatState or SIM_COMBAT_STATE.PEACE
end

function SimFight:IsRangedFaction(faction, weaponBranch)
    if not faction then return 0 end
    local f = faction
    if string and string.lower then
        f = string.lower(faction)
    elseif strlower then
        f = strlower(faction)
    end
    if f == "ngami" then return 1 end
    if f == "duongmon" then return 1 end
    if f == "ngudoc" then return 1 end
    if f == "vodang" and (not weaponBranch or weaponBranch == "khi" or weaponBranch == "phap") then return 1 end
    if f == "thiennhan" and (weaponBranch == "dao" or weaponBranch == "bua") then return 1 end
    if f == "conlon" and (weaponBranch == "dao" or weaponBranch == "set" or weaponBranch == "bua") then return 1 end
    return 0
end

function SimFight:ResolveCanonicalBranch(tbNpc, fac)
    if not tbNpc then return nil end
    local facName = fac or tbNpc.faction
    if not facName then return nil end

    local facTable = nil
    if SimProgression and SimProgression.FACTION_SKILLS then
        facTable = SimProgression.FACTION_SKILLS[facName]
    end

    -- 1. Use canonical branch already assigned to bot (if valid and not "any")
    local b = tbNpc.weaponBranch
    if b and b ~= "" and b ~= "any" then
        if not facTable then
            return b
        end
        if facTable[b] then
            return b
        end
        -- Canonical branch alias mapping
        local mapped = nil
        if b == "taykhong" then
            if facTable["taykhong"] then mapped = "taykhong"
            elseif facTable["quyen"] then mapped = "quyen"
            elseif facTable["amkhi"] then mapped = "amkhi"
            elseif facTable["chuong"] then mapped = "chuong" end
        elseif b == "con" and facTable["bong"] then
            mapped = "bong"
        elseif b == "bong" and facTable["con"] then
            mapped = "con"
        elseif b == "dao" and facTable["phi_dao"] and facName == "duongmon" then
            mapped = "phi_dao"
        elseif (b == "khi" or b == "phap") and facName == "vodang" and facTable["chuong"] then
            mapped = "chuong"
        end
        if mapped then return mapped end
        -- facTable exists and b is neither in facTable nor a recognized alias
        return nil
    end

    -- 2. Derive deterministically from existing canonical skill metadata on tbNpc
    local skillId = nil
    if tbNpc.skillCastBua then
        if type(tbNpc.skillCastBua) == "table" then
            skillId = tbNpc.skillCastBua[1]
        elseif type(tbNpc.skillCastBua) == "number" then
            skillId = tbNpc.skillCastBua
        end
    elseif tbNpc.skillCastBuaNoDebuff then
        if type(tbNpc.skillCastBuaNoDebuff) == "table" then
            skillId = tbNpc.skillCastBuaNoDebuff[1]
        elseif type(tbNpc.skillCastBuaNoDebuff) == "number" then
            skillId = tbNpc.skillCastBuaNoDebuff
        end
    end
    if skillId and skillId ~= 53 and facTable then
        local matchedBranch = nil
        local matchCount = 0
        for bName, skillList in facTable do
            if type(skillList) == "table" then
                for i = 1, getn(skillList) do
                    if skillList[i] and skillList[i].id == skillId then
                        matchedBranch = bName
                        matchCount = matchCount + 1
                        break
                    end
                end
            end
        end
        if matchCount == 1 then
            return matchedBranch
        end
    end

    -- 3. Derive deterministically from existing canonical gear metadata (tbNpc.nNewWeaponType)
    local wType = tbNpc.nNewWeaponType
    if wType ~= nil then
        if wType == 20 and (not facTable or facTable["kiem"]) then return "kiem" end
        if wType == 23 then
            if not facTable or facTable["dao"] then return "dao"
            elseif facTable["phi_dao"] and facName == "duongmon" then return "phi_dao" end
        end
        if wType == 24 and (not facTable or facTable["thuong"]) then return "thuong" end
        if wType == 26 then
            if not facTable or facTable["con"] then return "con"
            elseif facTable["bong"] then return "bong" end
        end
        if wType == 28 and (not facTable or facTable["songdao"]) then return "songdao" end
        if wType == 30 and (not facTable or facTable["chuy"]) then return "chuy" end
        if wType == 0 and facTable then
            if facTable["taykhong"] then return "taykhong"
            elseif facTable["quyen"] then return "quyen"
            elseif facName == "caibang" and facTable["chuong"] then return "chuong"
            elseif facName == "ngudoc" and facTable["chuong"] then return "chuong"
            elseif facName == "duongmon" and facTable["amkhi"] then return "amkhi"
            elseif facName == "ngami" and facTable["chuong"] then return "chuong"
            elseif facName == "vodang" and facTable["chuong"] then return "chuong"
            elseif facName == "thiennhan" and facTable["chuong"] then return "chuong"
            end
        end
    end

    -- 4. Derive deterministically from existing canonical NPC template metadata (SimBotNpc)
    if SimBotNpc and tbNpc.nNpcId and SimBotNpc[tbNpc.nNpcId] then
        local t = SimBotNpc[tbNpc.nNpcId]
        local tSkillId = t[1]
        local tb = t[2]
        if tb and tb ~= "" and tb ~= "any" then
            if not facTable or facTable[tb] then return tb end
            if tb == "taykhong" then
                if facTable["taykhong"] then return "taykhong" end
                if facTable["quyen"] then return "quyen" end
                if facTable["amkhi"] then return "amkhi" end
                if facTable["chuong"] then return "chuong" end
            elseif tb == "con" and facTable["bong"] then
                return "bong"
            elseif tb == "bong" and facTable["con"] then
                return "con"
            elseif tb == "dao" and facTable["phi_dao"] and facName == "duongmon" then
                return "phi_dao"
            elseif (tb == "khi" or tb == "phap") and facName == "vodang" and facTable["chuong"] then
                return "chuong"
            end
        end
        -- If template branch was "any" or unmapped, check template's canonical skill id (t[1])
        if tSkillId and tSkillId ~= 53 and facTable then
            local matchedBranch = nil
            local matchCount = 0
            for bName, skillList in facTable do
                if type(skillList) == "table" then
                    for i = 1, getn(skillList) do
                        if skillList[i] and skillList[i].id == tSkillId then
                            matchedBranch = bName
                            matchCount = matchCount + 1
                            break
                        end
                    end
                end
            end
            if matchCount == 1 then
                return matchedBranch
            end
        end
    end

    -- Never choose an arbitrary branch or iterate facTable blindly
    return nil
end

function SimFight:CalculateKiteTile(myTileX, myTileY, enemyTileX, enemyTileY, kiteDist)
    kiteDist = kiteDist or 6
    local dx = myTileX - enemyTileX
    local dy = myTileY - enemyTileY
    local dist = sqrt(dx*dx + dy*dy)
    if dist < 1 then
        dx = 1
        dy = 0
        dist = 1
    end
    local destX = myTileX + floor(dx * kiteDist / dist)
    local destY = myTileY + floor(dy * kiteDist / dist)
    return destX, destY
end

function SimFight:SelectBestTarget(simInstance, tbNpc, fightSys)
    if not tbNpc or not tbNpc.finalIndex or tbNpc.finalIndex <= 0 then return nil end
    local myX32, myY32, myW = GetNpcPos(tbNpc.finalIndex)
    if not myX32 then return nil end
    local myTileX = floor(myX32 / 32)
    local myTileY = floor(myY32 / 32)

    -- 1. Check direct player enemy (e.g. duel / self defense / aggro)
    local foundPlayerEnemy = tbNpc.isPlayerEnemyAround
    if foundPlayerEnemy and foundPlayerEnemy > 0 then
        local pW, pTileX, pTileY = CallPlayerFunction(foundPlayerEnemy, GetWorldPos)
        local pNpcIdx = PIdx2NpcIdx and PIdx2NpcIdx(foundPlayerEnemy)
        local curLife = (pNpcIdx and NPCINFO_GetNpcCurrentLife and NPCINFO_GetNpcCurrentLife(pNpcIdx)) or 1000
        if pW and pTileX and pTileY and pW == myW and curLife > 0 then
            local dist = GetDistanceRadius(myTileX, myTileY, pTileX, pTileY)
            local maxLife = (pNpcIdx and NPCINFO_GetNpcCurrentMaxLife and NPCINFO_GetNpcCurrentMaxLife(pNpcIdx)) or 1000
            return {
                targetType = "player",
                targetId = foundPlayerEnemy,
                npcIndex = pNpcIdx,
                tileX = pTileX,
                tileY = pTileY,
                worldX = pTileX * 32,
                worldY = pTileY * 32,
                dist = dist,
                curLife = curLife,
                maxLife = maxLife
            }
        else
            tbNpc.isPlayerEnemyAround = 0
        end
    end

    -- 2. Check NPC enemies around (support direct fightSys passed or tbNpc.foundNpcEnemy)
    local foundNpcEnemy = tbNpc.foundNpcEnemy
    if foundNpcEnemy and foundNpcEnemy > 0 then
        local targetX32, targetY32, targetW = GetNpcPos(foundNpcEnemy)
        local curLife = 1000
        if NPCINFO_GetNpcCurrentLife then
            local l = NPCINFO_GetNpcCurrentLife(foundNpcEnemy)
            if l ~= nil then curLife = l end
        end
        if not (targetX32 and targetY32 and targetW == myW and curLife > 0) then
            tbNpc.foundNpcEnemy = nil
            foundNpcEnemy = nil
        end
    end

    if not foundNpcEnemy or foundNpcEnemy <= 0 then
        local isNpcAround = (fightSys and fightSys.IsNpcEnemyAround) or (self and self.IsNpcEnemyAround) or (tbNpc.fightSys and tbNpc.fightSys.IsNpcEnemyAround) or (SimFight and SimFight.Citizen and SimFight.Citizen.IsNpcEnemyAround)
        if isNpcAround then
            foundNpcEnemy = isNpcAround(fightSys or self or tbNpc.fightSys or SimFight.Citizen, simInstance, tbNpc)
            if foundNpcEnemy and foundNpcEnemy > 0 then
                tbNpc.foundNpcEnemy = foundNpcEnemy
            end
        end
    end

    if foundNpcEnemy and foundNpcEnemy > 0 then
        local targetX32, targetY32, targetW = GetNpcPos(foundNpcEnemy)
        if targetX32 and targetY32 and targetW == myW then
            local targetTileX = floor(targetX32 / 32)
            local targetTileY = floor(targetY32 / 32)
            local dist = GetDistanceRadius(myTileX, myTileY, targetTileX, targetTileY)
            local curLife = (NPCINFO_GetNpcCurrentLife and NPCINFO_GetNpcCurrentLife(foundNpcEnemy)) or 1000
            local maxLife = (NPCINFO_GetNpcCurrentMaxLife and NPCINFO_GetNpcCurrentMaxLife(foundNpcEnemy)) or 1000
            return {
                targetType = "npc",
                targetId = foundNpcEnemy,
                npcIndex = foundNpcEnemy,
                tileX = targetTileX,
                tileY = targetTileY,
                worldX = targetX32,
                worldY = targetY32,
                dist = dist,
                curLife = curLife,
                maxLife = maxLife
            }
        end
    end

    return nil
end

--========================================================
-- HORSE COMBAT & DISMOUNT ENGINE
--========================================================
function SimApplyHorseCombat(tbNpc, skillId)
    if not tbNpc or not tbNpc.finalIndex or tbNpc.finalIndex <= 0 then return end
    local lv = tbNpc.level or 1
    if lv < 20 then
        if SetNpcRideHorse and tbNpc.isCurrentlyRiding ~= 0 then
            SetNpcRideHorse(tbNpc.finalIndex, 0)
        end
        tbNpc.isCurrentlyRiding = 0
        return
    end

    local canHorse = 0
    if SimSkillMeta and SimSkillMeta.CanCastOnHorse then
        canHorse = SimSkillMeta:CanCastOnHorse(skillId)
    elseif SimProgression and SimProgression.CanCastOnHorse then
        canHorse = SimProgression:CanCastOnHorse(skillId)
    end

    if canHorse == 0 then
        -- HorseLimit>=1: MUST dismount BEFORE cast
        if SetNpcRideHorse then SetNpcRideHorse(tbNpc.finalIndex, 0) end
        if BotMountSync then BotMountSync(tbNpc.finalIndex, 0) end
        tbNpc.isCurrentlyRiding = 0
        tbNpc.lastRideWant = 0
    else
        -- HorseLimit==0: may remain mounted
        if SetNpcRideHorse and tbNpc.isCurrentlyRiding ~= 1 then
            SetNpcRideHorse(tbNpc.finalIndex, 1)
        end
        tbNpc.isCurrentlyRiding = 1
        tbNpc.lastRideWant = 1
    end
end

function SimRestoreHorseMovement(tbNpc)
    if not tbNpc or not tbNpc.finalIndex or tbNpc.finalIndex <= 0 then return end
    local lv = tbNpc.level or 1
    if lv >= 20 then
        if SetNpcRideHorse and tbNpc.isCurrentlyRiding ~= 1 then
            SetNpcRideHorse(tbNpc.finalIndex, 1)
        end
        tbNpc.isCurrentlyRiding = 1
    else
        if SetNpcRideHorse and tbNpc.isCurrentlyRiding ~= 0 then
            SetNpcRideHorse(tbNpc.finalIndex, 0)
        end
        tbNpc.isCurrentlyRiding = 0
    end
end

function ChildrenLeaveFight(self, simInstance, tbNpc, code, reason)
    if not tbNpc.children then
        return 1
    end
    local size = getn(tbNpc.children)
    if size == 0 then
        return 1
    end

    for i = 1, size do
        local child = simInstance:Get(tbNpc.children[i])
        if child then
            LeaveFight(self, simInstance, child, code, reason)
        end
    end
    return 1
end

function LeaveFight(self, simInstance, tbNpc, isAllDead, reason)
    local nListId = tbNpc.id
    ChildrenLeaveFight(self, simInstance, tbNpc, isAllDead, reason)

    isAllDead = isAllDead or 0

    tbNpc.isFighting = 0
    SimRestoreHorseMovement(tbNpc)

    tbNpc.tick_canswitch = tbNpc.tick_breath +
        random(tbNpc.TIME_RESTING_minTs or TIME_RESTING.minTs,
            tbNpc.TIME_RESTING_maxTs or TIME_RESTING.maxTs)
    reason = reason or "no reason" 
    if SIMBOT_COMBAT_DEBUG == 1 and Msg2Player and simInstance then
        local pId = simInstance.GetPlayer and simInstance:GetPlayer(nListId)
        if pId and pId > 0 then
            Msg2Player(format("[SIMBOT_COMBAT_DEBUG] LeaveFight bot=%s mode=%s isAllDead=%s reason=%s",
                tostring(tbNpc.szName or tbNpc.finalIndex),
                tostring(tbNpc.mode),
                tostring(isAllDead or 0),
                tostring(reason or "none")))
        end
    end
    if (isAllDead ~= 1 and tbNpc.kind ~= 3 and (tbNpc.kind ~= 4 or tbNpc.isAttackable == 1)) then        
        self:SetFightState(tbNpc, 0)
    else
        tbNpc.entitySys:Respawn(simInstance, tbNpc, isAllDead, reason)
    end
end
 

function execCastNormalSkill(self, simInstance, tbNpc)
    if not tbNpc or not tbNpc.finalIndex or tbNpc.finalIndex <= 0 then return end
    if not tbNpc.faction and not tbNpc.skillCastBua then
        return
    end

    if tbNpc.fighting == 0 and tbNpc.isFighting ~= 1 then
        return
    end
    if (tbNpc.tick_canCast and tbNpc.tick_canCast > tbNpc.tick_breath) then
        return
    end

    local hasPhaiCast = (SimCityPhai and tbNpc.faction and SimCityPhai[tbNpc.faction] and SimCityPhai[tbNpc.faction].normalCast and getn(SimCityPhai[tbNpc.faction].normalCast) > 0)
    local hasProg = (SimProgression and tbNpc.faction and ((SimProgression.UpdateBotSkills ~= nil) or (SimProgression.FACTION_SKILLS and SimProgression.FACTION_SKILLS[tbNpc.faction])))
    if not hasPhaiCast and not tbNpc.skillCastBua and not hasProg and not SimPickSkill then
        return
    end

    if tbNpc.isPlayerEnemyAround == 0 and tbNpc.mode ~= "train" and (random(1, 1000) > 50) then
        return
    end

    -- Check low HP retreat / heal
    if NPCINFO_GetNpcCurrentLife and NPCINFO_GetNpcCurrentMaxLife then
        local cl = NPCINFO_GetNpcCurrentLife(tbNpc.finalIndex)
        local ml = NPCINFO_GetNpcCurrentMaxLife(tbNpc.finalIndex)
        if cl and ml and ml > 0 and (cl / ml) < 0.25 and tbNpc.tongkim ~= 1 then
            SimFight:SetCombatState(tbNpc, SIM_COMBAT_STATE.RETREAT_HEAL, "low hp panic")
            if EnforceBotHp then EnforceBotHp(tbNpc.finalIndex, 350) end
            tbNpc.tick_canCast = tbNpc.tick_breath + 2
            return
        end
    end

    local target = SimFight:SelectBestTarget(simInstance, tbNpc, self)
    if not target then
        SimFight:SetCombatState(tbNpc, SIM_COMBAT_STATE.PEACE, "no enemies")
        return
    end

    -- Broadcast to virtual party if member acquired target
    if tbNpc.virtualPartyId and SimParty and SimParty.ShareAggroTarget and target.npcIndex and target.npcIndex > 0 then
        SimParty:ShareAggroTarget(simInstance, tbNpc.virtualPartyId, target.npcIndex, tbNpc)
    end

    local selectedSkill = (SimPickSkill and SimPickSkill(tbNpc)) or tbNpc.skillCastBua or (tbNpc.faction and SimCityPhai and SimCityPhai[tbNpc.faction] and SimCityPhai[tbNpc.faction].normalCast and SimCityPhai[tbNpc.faction].normalCast[1])
    if not selectedSkill and tbNpc.faction then
        local canonicalBranch = SimFight:ResolveCanonicalBranch(tbNpc, tbNpc.faction)
        if canonicalBranch then
            tbNpc.weaponBranch = canonicalBranch
            if SimProgression and SimProgression.UpdateBotSkills then
                SimProgression:UpdateBotSkills(tbNpc)
                selectedSkill = tbNpc.skillCastBua
            end
            if not selectedSkill and SimProgression and SimProgression.FACTION_SKILLS and SimProgression.FACTION_SKILLS[tbNpc.faction] then
                local facTable = SimProgression.FACTION_SKILLS[tbNpc.faction]
                local skillList = facTable[canonicalBranch]
                if skillList and getn(skillList) > 0 then
                    local lv = tbNpc.level or 1
                    local chosenEntry = nil
                    if lv >= 10 then
                        for i = 1, getn(skillList) do
                            local entry = skillList[i]
                            if lv >= (entry.reqLv or 1) then
                                chosenEntry = entry
                                break
                            end
                        end
                    end
                    if not chosenEntry then
                        chosenEntry = skillList[getn(skillList)]
                    end
                    if chosenEntry and chosenEntry.id then
                        local skLv = (SimProgression.CalcSkillLevel and SimProgression:CalcSkillLevel(lv, chosenEntry.reqLv or 1)) or 20
                        selectedSkill = { chosenEntry.id, skLv }
                    end
                end
            end
        end
    end
    if not selectedSkill or not selectedSkill[1] then
        if SimLog then
            SimLog("[SimFight] execCastNormalSkill resolution failed for bot: " .. tostring(tbNpc.szName or tbNpc.finalIndex or tbNpc.id) .. " fac=" .. tostring(tbNpc.faction) .. " branch=" .. tostring(tbNpc.weaponBranch))
        end
        return
    end
    local skillId = selectedSkill[1]
    local baseSkillLv = selectedSkill[2] or 20
    local bonusSkillLv = (SimGear and SimGear.GetSkillLevelBonus and SimGear:GetSkillLevelBonus(tbNpc)) or 0
    local skillLevel = baseSkillLv + bonusSkillLv

    -- Get tile coords of Bot
    local myX32, myY32, myW = GetNpcPos(tbNpc.finalIndex)
    if not myX32 then return end
    local myTileX = floor(myX32 / 32)
    local myTileY = floor(myY32 / 32)

    local maxCastTiles = 2
    local combatMeta = nil
    if SimSkillMeta and SimSkillMeta.GetSkillCombatMeta then
        combatMeta = SimSkillMeta:GetSkillCombatMeta(skillId)
    end
    if combatMeta and combatMeta.attackRadiusTiles then
        maxCastTiles = combatMeta.attackRadiusTiles
    elseif SimSkillMeta and SimSkillMeta.GetAttackRadiusTiles then
        local t = SimSkillMeta:GetAttackRadiusTiles(skillId)
        if t then maxCastTiles = t end
    elseif SimProgression and SimProgression.GetSkillAttackRadiusTiles then
        local t = SimProgression:GetSkillAttackRadiusTiles(skillId)
        if t then maxCastTiles = t end
    end
    local maxChaseTiles = SIMBOT_CHASE_MAX_TILES or 20

    if target.dist > maxChaseTiles then
        if target.targetType == "player" then
            tbNpc.isPlayerEnemyAround = 0
        else
            tbNpc.foundNpcEnemy = nil
        end
        SimFight:SetCombatState(tbNpc, SIM_COMBAT_STATE.PEACE, "target out of chase range")
        return
    end

    -- Range class from THIS skill only (never faction-wide assumption)
    local isRanged = 0
    local classified = 0
    if combatMeta and combatMeta.skillType then
        if combatMeta.skillType == "ranged" then
            isRanged = 1
            classified = 1
        elseif combatMeta.skillType == "melee" then
            isRanged = 0
            classified = 1
        end
    end

    if classified == 0 and SimSkillMeta and SimSkillMeta.Get then
        local meta = SimSkillMeta:Get(skillId)
        if meta then
            if meta.melee == 1 then
                isRanged = 0
                classified = 1
            elseif (meta.tiles or 0) >= 6 or meta.typ == 0 then
                isRanged = 1
                classified = 1
            else
                isRanged = 0
                classified = 1
            end
        end
    end

    if classified == 0 and SimFight and SimFight.IsRangedFaction and tbNpc.faction then
        isRanged = SimFight:IsRangedFaction(tbNpc.faction, tbNpc.weaponBranch)
        classified = 1
    end

    -- Tactical kiting: If ranged bot and target is closer than 4 tiles
    if isRanged == 1 and target.dist < 4 and tbNpc.tongkim ~= 1 then
        SimFight:SetCombatState(tbNpc, SIM_COMBAT_STATE.KITE, "ranged spacing kite")
        local kiteX, kiteY = SimFight:CalculateKiteTile(myTileX, myTileY, target.tileX, target.tileY, 6)
        if NpcRun then NpcRun(tbNpc.finalIndex, kiteX, kiteY) end
        if BotDashTo and random(1, 3) == 1 then
            BotDashTo(tbNpc.finalIndex, kiteX, kiteY, 15)
        end
        if SimMovement then SimMovement:SetState(tbNpc, SIM_MOVE_STATE.KITE, "tactical kite") end
        tbNpc.tick_canCast = tbNpc.tick_breath + 1
        return
    elseif target.dist > maxCastTiles then
        SimFight:SetCombatState(tbNpc, SIM_COMBAT_STATE.ENGAGING, "closing distance")
        if NpcRun then NpcRun(tbNpc.finalIndex, target.tileX, target.tileY) end
        if SimMovement then SimMovement:SetState(tbNpc, SIM_MOVE_STATE.CHASE, "chasing enemy") end
        tbNpc.tick_canCast = tbNpc.tick_breath + 1
        return
    end

    -- Cast skill combo: horse state then SAME pending skill
    SimFight:SetCombatState(tbNpc, SIM_COMBAT_STATE.COMBO, "casting combo")
    if SimMovement then SimMovement:SetState(tbNpc, SIM_MOVE_STATE.IDLE, "casting combo stationary") end
    SimApplyHorseCombat(tbNpc, skillId)
    -- If skill forbids horse and we are still mounted, defer cast 1 tick
    if SimSkillMeta and SimSkillMeta.CanCastOnHorse and SimSkillMeta:CanCastOnHorse(skillId) ~= 1 then
        local stillRide = 0
        if GetNpcRideHorse then stillRide = GetNpcRideHorse(tbNpc.finalIndex) or 0 end
        if stillRide == 1 or tbNpc.isCurrentlyRiding == 1 then
            if SetNpcRideHorse then SetNpcRideHorse(tbNpc.finalIndex, 0) end
            if BotMountSync then BotMountSync(tbNpc.finalIndex, 0) end
            tbNpc.isCurrentlyRiding = 0
            tbNpc.lastRideWant = 0
            tbNpc.tick_canCast = tbNpc.tick_breath + 1
            return
        end
    end

    if target.targetType == "player" then
        if BotDoSkill and target.npcIndex and target.npcIndex > 0 then
            local _r = BotDoSkill(tbNpc.finalIndex, skillId, skillLevel, target.npcIndex)
        else
            NpcCastSkill(tbNpc.finalIndex, skillId, skillLevel, target.worldX, target.worldY)
        end
        if SimCommitSkillToggle then SimCommitSkillToggle(tbNpc) end
        local cdTicks = (SimGear and SimGear.GetCastCooldownTicks and SimGear:GetCastCooldownTicks(tbNpc)) or (2*18/REFRESH_RATE)
        -- Train: cast faction skills more often so Client shows VFX (engine AI alone often auto-attacks)
        if tbNpc.mode == "train" then
            local trainCd = TRAIN_SKILL_CAST_CD_TICKS or 1
            if trainCd < cdTicks then cdTicks = trainCd end
        end
        tbNpc.tick_canCast = tbNpc.tick_breath + cdTicks
        if SimGear and SimGear.ApplyCombatLeech then SimGear:ApplyCombatLeech(tbNpc, target.targetId, "player") end
        if SimProgression and SimProgression.AddExp and tbNpc.mode == "train" then
            SimProgression:AddExp(tbNpc, (tbNpc.level or 1) * 20)
        end
    else
        -- Prefer BotDoSkill(targetIndex) so Client plays skill anim/VFX; fallback NpcCastSkill
        if BotDoSkill and target.npcIndex and target.npcIndex > 0 then
            BotDoSkill(tbNpc.finalIndex, skillId, skillLevel, target.npcIndex)
        else
            NpcCastSkill(tbNpc.finalIndex, skillId, skillLevel, target.worldX, target.worldY)
        end
        if SimCommitSkillToggle then SimCommitSkillToggle(tbNpc) end
        local cdTicks = (SimGear and SimGear.GetCastCooldownTicks and SimGear:GetCastCooldownTicks(tbNpc)) or (2*18/REFRESH_RATE)
        if tbNpc.mode == "train" then
            local trainCd = TRAIN_SKILL_CAST_CD_TICKS or 1
            if trainCd < cdTicks then cdTicks = trainCd end
        end
        tbNpc.tick_canCast = tbNpc.tick_breath + cdTicks
        if SimGear and SimGear.ApplyCombatLeech then SimGear:ApplyCombatLeech(tbNpc, target.targetId, "npc") end
        if SimProgression and SimProgression.AddExp and tbNpc.mode == "train" then
            SimProgression:AddExp(tbNpc, (tbNpc.level or 1) * 20)
        end
    end
end

function execCastOnParent(self, simInstance, tbNpc, pId, pX, pY)
    if SIMBOT_BUFF_REALCAST ~= 1 then return end      
    if tbNpc.role ~= "keoxe" or tbNpc.faction ~= "ngami" then
        return
    end
    if (tbNpc.tick_canCast and tbNpc.tick_canCast > tbNpc.tick_breath) then
        return
    end

    local parentMax = NPCINFO_GetNpcCurrentMaxLife(PIdx2NpcIdx(pId))
    local parentCur = NPCINFO_GetNpcCurrentLife(PIdx2NpcIdx(pId))
    local parentPercent = parentCur / parentMax
    
    if parentPercent < 0.5 then
        NpcCastSkill(tbNpc.finalIndex, 93, 20, pX*32, pY*32)
        tbNpc.tick_canCast = tbNpc.tick_breath + 10*18/REFRESH_RATE
    end 
end
function execCastOnSelf(self, tbNpc)
    if SIMBOT_BUFF_REALCAST ~= 1 then return end     

    if tbNpc.faction ~= "ngami" then
        return
    end

    if (tbNpc.tick_canCast and tbNpc.tick_canCast > tbNpc.tick_breath) then
        return
    end

    local parentMax = NPCINFO_GetNpcCurrentMaxLife(tbNpc.finalIndex)
    local parentCur = NPCINFO_GetNpcCurrentLife(tbNpc.finalIndex)
    local parentPercent = parentCur / parentMax
    
    if parentPercent < 0.3 then
        local nX, nY, nW = GetNpcPos(tbNpc.finalIndex)
        NpcCastSkill(tbNpc.finalIndex, 93, random(10,20), nX, nY)
        tbNpc.tick_canCast = tbNpc.tick_breath + 10*18/REFRESH_RATE
    end 
end

SIMBOT_HP_CAP = SIMBOT_HP_CAP or 60000
SIMBOT_NGAMI_BUFF = 1 
SIMBOT_BUFF_REALCAST = SIMBOT_BUFF_REALCAST or 0
SIMBOT_DEBUFF = SIMBOT_DEBUFF or 1  
SIMBOT_TRANPHAI = 1  
SIMBOT_CITY_BUFF_PCT = SIMBOT_CITY_BUFF_PCT or 30 
function BuffChar(self, simInstance, tbNpc)
    if SIMBOT_NGAMI_BUFF ~= 1 then return end     
    if BotShowAura and not tbNpc.dhSet and tbNpc.tongkim ~= 1 then   
        tbNpc.dhSet = 1        
        g_oldTitleCount = g_oldTitleCount or 0
        if g_oldTitleCount < 10 then
            local _dhp = {82, 83, 84, 153, 154, 155, 156, 157, 158, 159}
            g_oldTitleCount = g_oldTitleCount + 1
            BotShowAura(tbNpc.finalIndex, _dhp[g_oldTitleCount])  
        else            
            local _sectTitle = { thieulam=3014, thienvuong=3015, duongmon=3016, ngudoc=3017, caibang=3018, thiennhan=3019, ngami=3020, thuyyen=3021, vodang=3022, conlon=3023 }
            local _st = _sectTitle[tbNpc.faction]
            if _st and random(1, 100) <= 2 then   
                BotShowAura(tbNpc.finalIndex, _st)
            end
        end
    end
  
    if not (SimCityCanFight and SimCityCanFight(tbNpc) == 1) then
        if tbNpc.cityBuffOn == nil then
            if random(1, 100) <= SIMBOT_CITY_BUFF_PCT then tbNpc.cityBuffOn = 1 else tbNpc.cityBuffOn = 0 end
        end
        if tbNpc.cityBuffOn == 0 and tbNpc.isFighting ~= 1 and tbNpc.faction ~= "ngami" and tbNpc.faction ~= "caibang" and tbNpc.faction ~= "ngudoc" then return end  
    end
    -- Ho tro
    if tbNpc.faction == "ngami" then        
        if AddNpcSkillState and (not tbNpc.ngamiAuraTick or tbNpc.ngamiAuraTick <= tbNpc.tick_breath) then
            tbNpc.ngamiAuraTick = tbNpc.tick_breath + 20*18/REFRESH_RATE
            AddNpcSkillState(tbNpc.finalIndex, 86, 20, 1, 24*60*60*18, 1)
            AddNpcSkillState(tbNpc.finalIndex, 89, 20, 1, 24*60*60*18, 1)
            AddNpcSkillState(tbNpc.finalIndex, 92, 20, 1, 24*60*60*18, 1)
            AddNpcSkillState(tbNpc.finalIndex, 282, 20, 1, 24*60*60*18, 1)
            AddNpcSkillState(tbNpc.finalIndex, 332, 20, 1, 24*60*60*18, 1)           
            if BotDoSkill then BotDoSkill(tbNpc.finalIndex, 92, 20, 0) end
            if SetNpcAuraSkill then SetNpcAuraSkill(tbNpc.finalIndex, 92, 20) end
        end
    elseif tbNpc.faction == "caibang" then        
        if BotShowAura and tbNpc.skillCastBua and tbNpc.skillCastBua[1] == 359
           and (not tbNpc.cbAuraTick or tbNpc.cbAuraTick <= tbNpc.tick_breath) then
            tbNpc.cbAuraTick = tbNpc.tick_breath + 5*18/REFRESH_RATE
            BotShowAura(tbNpc.finalIndex, 3013)
        end
    elseif tbNpc.skillHoTro and tbNpc.faction and tbNpc.skillHoTro > 0 then
       
        if SimCityPhai[tbNpc.faction] and SimCityPhai[tbNpc.faction].noCast and SimCityPhai[tbNpc.faction].noCast[tbNpc.skillHoTro]
           and not (tbNpc.faction == "ngudoc" and (SimCityIsPeaceZone and SimCityIsPeaceZone(tbNpc) == 1)) then  
            if (SimCityPhai[tbNpc.faction].noCast[tbNpc.skillHoTro][1] == -999 or tbNpc.faction == "ngudoc")  
                and tbNpc.isFighting == 0 and not tbNpc.partyPlayerId then   
                SetNpcAuraSkill(tbNpc.finalIndex, 1, 1)
            else
                SetNpcAuraSkill(tbNpc.finalIndex, 
                    SimCityPhai[tbNpc.faction].noCast[tbNpc.skillHoTro][1], 
                    tbNpc.role == "keoxe" and SimCityPhai[tbNpc.faction].noCast[tbNpc.skillHoTro][2] or 1
                )
            end
        end
    end

    -- Tran phai
    if SIMBOT_TRANPHAI == 1 and tbNpc.faction and SimCityPhai[tbNpc.faction] and SimCityPhai[tbNpc.faction].needCast
        and (SimCityCanFight and SimCityCanFight(tbNpc) == 1)  
        and (not tbNpc.tranPhaiTick or tbNpc.tranPhaiTick <= tbNpc.tick_breath) then   
        tbNpc.tranPhaiTick = tbNpc.tick_breath + 60*18/REFRESH_RATE 

        if tbNpc.skillTranPhai then
            local skillId = tbNpc.skillTranPhai[1]
            local skillLevel = tbNpc.skillTranPhai[2]
            if skillId > 0 then
                NpcCastSkill(tbNpc.finalIndex, skillId, skillLevel)                
                local currentMaxLife = NPCINFO_GetNpcCurrentMaxLife(tbNpc.finalIndex)               
                if tbNpc.isFighting == 0 and currentMaxLife > 0 and (not tbNpc.maxHP or tbNpc.maxHP < currentMaxLife) then
                    tbNpc.maxHP = currentMaxLife                    
                    NPCINFO_SetNpcCurrentLife(tbNpc.finalIndex, tbNpc.maxHP)
                end
            end
        else
            for i=1, getn(SimCityPhai[tbNpc.faction].needCast) do
                local skillId = SimCityPhai[tbNpc.faction].needCast[i][1]
                local skillLevel = tbNpc.role == "keoxe" and SimCityPhai[tbNpc.faction].needCast[i][2] or 1
                NpcCastSkill(tbNpc.finalIndex, skillId, skillLevel)

                local currentMaxLife = NPCINFO_GetNpcCurrentMaxLife(tbNpc.finalIndex)                
                if tbNpc.isFighting == 0 and currentMaxLife > 0 and (not tbNpc.maxHP or tbNpc.maxHP < currentMaxLife) then
                    tbNpc.maxHP = currentMaxLife                 
                    NPCINFO_SetNpcCurrentLife(tbNpc.finalIndex, tbNpc.maxHP)
                end

            end
        end
    end

    if BotDoSkill and tbNpc.skillCastBua and tbNpc.skillCastBua[1] == 372
        and (SimCityCanFight and SimCityCanFight(tbNpc) == 1)
        and (not tbNpc.clDaoBuffTick or tbNpc.clDaoBuffTick <= tbNpc.tick_breath) then
        tbNpc.clDaoBuffTick = tbNpc.tick_breath + 30*18/REFRESH_RATE
        if SetNpcLevel then SetNpcLevel(tbNpc.finalIndex, 95) end
        BotDoSkill(tbNpc.finalIndex, 178, 20, 0)
    end
end
-- Public functions
SimFight = SimFight or {}

SimFight.Base = {
}

SimFight.Citizen = {
    LeaveFight = LeaveFight,
    BuffChar = BuffChar,
    execCastOnParent = execCastOnParent,
    execCastOnSelf = execCastOnSelf,    
    TriggerFightWithNPC = function(self, simInstance, tbNpc)       
        -- Allow train / tongkim / outdoor grind / player-fighting
        local outdoorOk = tbNpc.worldInfo and tbNpc.worldInfo.allowFighting == 1 and tbNpc.worldInfo.cityPeace ~= 1
        if tbNpc.isPlayerFighting == 0 and tbNpc.mode ~= "train" and tbNpc.tongkim ~= 1 and not outdoorOk then   
            return 0
        end
        local enemy = self:IsNpcEnemyAround(simInstance, tbNpc)
        if enemy and enemy > 0 then
            tbNpc.foundNpcEnemy = enemy
            return self:JoinFight(simInstance, tbNpc, "enemy around")
        end
        return 0
    end,
    IsNpcEnemyAround = function(self, simInstance, tbNpc)
        local allNpcs = {}
        local nCount = 0
        local outdoorOk = tbNpc.worldInfo and tbNpc.worldInfo.allowFighting == 1 and tbNpc.worldInfo.cityPeace ~= 1
        local grind = (tbNpc.mode == "train" or outdoorOk)
        local radius = tbNpc.RADIUS_FIGHT_SCAN or RADIUS_FIGHT_SCAN
        if grind then
            radius = tbNpc.RADIUS_FIGHT_SCAN or 20
        end

        allNpcs, nCount = GetNpcAroundNpcList(tbNpc.finalIndex, radius)
        if not allNpcs or not nCount or nCount <= 0 then return 0 end

        local bestMonster = 0
        local bestKind0 = 0
        for i = 1, nCount do
            local idx = allNpcs[i]
            if idx and idx ~= tbNpc.finalIndex then
                local isSim = GetNpcParam and (GetNpcParam(idx, 4) == 1)
                if not isSim then
                    local fighter2Kind = GetNpcKind(idx)
                    local fighter2Camp = GetNpcCurCamp(idx)
                    local alive = 1
                    if NPCINFO_GetNpcCurrentLife then
                        local life = NPCINFO_GetNpcCurrentLife(idx)
                        if life ~= nil and life <= 0 then alive = 0 end
                    end
                    if alive == 1 then
                        if grind then
                            -- Prefer real monsters (kind ~= 0)
                            if fighter2Kind ~= nil and fighter2Kind ~= 0 then
                                if bestMonster == 0 then bestMonster = idx end
                            elseif fighter2Kind == 0 then
                                -- Only allow kind-0 player/PvP targets through explicit DoSat/hostile-PvP rules
                                local isHostileKind0 = 0
                                if tbNpc.isDoSat == 1 or tbNpc.camp == 5 then
                                    isHostileKind0 = 1
                                elseif tbNpc.camp ~= 0 and IsAttackableCamp and IsAttackableCamp(tbNpc.camp, fighter2Camp) == 1 then
                                    isHostileKind0 = 1
                                end
                                if isHostileKind0 == 1 and bestKind0 == 0 then
                                    bestKind0 = idx
                                end
                            end
                        elseif fighter2Kind == 0 and IsAttackableCamp and IsAttackableCamp(tbNpc.camp, fighter2Camp) == 1 then
                            return idx
                        end
                    end
                end
            end
        end
        if bestMonster > 0 then return bestMonster end
        if bestKind0 > 0 then return bestKind0 end
        return 0
    end,
    CanLeaveFight = function(self, simInstance, tbNpc)
        if tbNpc.isDead == 1 then
            return 0
        end

        -- No attacker around including NPC and Player ? Stop
        if (self:IsNpcEnemyAround(simInstance, tbNpc) == 0 and
                tbNpc.isPlayerEnemyAround == 0) then
            if (tbNpc.leaveFightWhenNoEnemy and tbNpc.leaveFightWhenNoEnemy > 0) then
                local realCanSwitchTick = tbNpc.tick_breath + tbNpc.leaveFightWhenNoEnemy - 1

                if tbNpc.tick_canswitch > realCanSwitchTick then
                    tbNpc.tick_canswitch = realCanSwitchTick
                end
            end

            return 1
        end
        return 0
    end,
    TriggerFightWithPlayer = function(self, simInstance, tbNpc)
        -- FIGHT other player
        if GetNpcAroundPlayerList then
            if tbNpc.isPlayerEnemyAround > 0 then
                if tbNpc.role == "citizen" then                
                    if tbNpc.worldInfo.showFightingArea == 1 then
                        local name = GetNpcName(tbNpc.finalIndex)
                        local lastPos
                        
                        if (tbNpc.walkMode == "preset" or tbNpc.walkMode == "formation") and tbNpc.worldInfo.presetPaths and tbNpc.currentPathIndex then
                            local path = tbNpc.worldInfo.presetPaths[tbNpc.currentPathIndex]
                            if path and tbNpc.currentPointIndex and tbNpc.currentPointIndex <= getn(path) then
                                lastPos = path[tbNpc.currentPointIndex]
                            end
                        else
                            lastPos = tbNpc.nPosId
                        end
                        
                        if lastPos ~= nil and lastPos ~= "none" then
                            local node = getNodeInfoByNodeName(tbNpc, lastPos)
                            Msg2Map(tbNpc.nMapId,
                                "<color=white>" .. name .. "<color> ??nh ng??i t?i " .. tbNpc.worldInfo.name .. " " ..
                                floor(node.x / 8) .. " " .. floor(node.y / 16) .. "")
                        end
                    end
                end
                return self:JoinFight(simInstance, tbNpc, "player around")
            end
        end

        return 0
    end,
    SetFightState = function(self, tbNpc, mode, nX, nY)
        if mode == 9 then
            mode = 1
        end
        --if mode == 9 then
        --    SetNpcAI(tbNpc.finalIndex, mode, 20, -1, -1, -1, -1, -1, 0, nX, nY)            
        --else
            SetNpcAI(tbNpc.finalIndex, mode)
        --end
    end,


    ChildrenJoinFight = function(self, simInstance, tbNpc, code)
        if not tbNpc.children then
            return 1
        end
        local size = getn(tbNpc.children)
        if size == 0 then
            return 1
        end

        for i = 1, size do
            local child = simInstance:Get(tbNpc.children[i])
            if child then
                self:JoinFight(simInstance, child, code)
            end
        end
        return 1
    end,

    JoinFight = function(self, simInstance, tbNpc, reason)
        local nListId = tbNpc.id
        self:ChildrenJoinFight(simInstance, tbNpc, reason)
        tbNpc.isFighting = 1
        if SetNpcCombat then SetNpcCombat(tbNpc.finalIndex, 1, tbNpc.skillCastBua and tbNpc.skillCastBua[1] or 0) end  

        
        tbNpc.tick_canswitch = tbNpc.tick_breath +
            random(tbNpc.TIME_FIGHTING_minTs or TIME_FIGHTING.minTs,
                tbNpc.TIME_FIGHTING_maxTs or TIME_FIGHTING.maxTs) -- trong trang thai pk 1 toi 2ph
        

        reason = reason or "no reason"


        -- If already having last fight pos, we may simply change AI
        local currX, currY, currW = GetNpcPos(tbNpc.finalIndex)
        if tbNpc.lastFightPos then
            if tbNpc.lastFightPos.W == currW then
                if (GetDistanceRadius(tbNpc.lastFightPos.X/32, tbNpc.lastFightPos.Y/32, currX/32, currY/32) < 16) then
                    local outdoorOkFast = tbNpc.worldInfo and tbNpc.worldInfo.allowFighting == 1 and tbNpc.worldInfo.cityPeace ~= 1
                    if tbNpc.mode == "train" or outdoorOkFast then
                        local sk = SimPickSkill and SimPickSkill(tbNpc)
                        local sid = (sk and sk[1]) or (tbNpc.skillCastBua and tbNpc.skillCastBua[1]) or 0
                        if sid > 0 and SimApplyHorseCombat then SimApplyHorseCombat(tbNpc, sid) end
                        self:SetFightState(tbNpc, 9, currX, currY)
                        if SetNpcKind then SetNpcKind(tbNpc.finalIndex, 0) end
                        -- Bind combat skill so engine AI prefers VFX skill, not bare auto-attack
                        if SetNpcCombat and sid > 0 then SetNpcCombat(tbNpc.finalIndex, 1, sid) end
                        if (not tbNpc.foundNpcEnemy) or tbNpc.foundNpcEnemy <= 0 then
                            local e = self:IsNpcEnemyAround(simInstance, tbNpc)
                            if e and e > 0 then tbNpc.foundNpcEnemy = e end
                        end
                        if tbNpc.foundNpcEnemy and tbNpc.foundNpcEnemy > 0 and NpcRun and GetNpcPos then
                            local _ex, _ey = GetNpcPos(tbNpc.foundNpcEnemy)
                            if _ex and _ey then
                                NpcRun(tbNpc.finalIndex, floor(_ex / 32), floor(_ey / 32))
                            end
                        end
                        if self.Update then self:Update(simInstance, tbNpc) end
                    else
                        self:SetFightState(tbNpc, 9, currX, currY)
                    end
                    return 1
                end
            end
        end
        
        local outdoorOk = tbNpc.worldInfo and tbNpc.worldInfo.allowFighting == 1 and tbNpc.worldInfo.cityPeace ~= 1
        if tbNpc.mode == "train" or outdoorOk then
            -- Engine AI hunts (9->1). Lua Update + SetNpcCombat(skillId) force visible faction skills.
            local sk = SimPickSkill and SimPickSkill(tbNpc)
            local sid = (sk and sk[1]) or (tbNpc.skillCastBua and tbNpc.skillCastBua[1]) or 0
            if sid > 0 and SimApplyHorseCombat then SimApplyHorseCombat(tbNpc, sid) end
            self:SetFightState(tbNpc, 9, currX, currY)
            if SetNpcKind then SetNpcKind(tbNpc.finalIndex, 0) end
            if SetNpcCombat and sid > 0 then SetNpcCombat(tbNpc.finalIndex, 1, sid) end
            if (not tbNpc.foundNpcEnemy) or tbNpc.foundNpcEnemy <= 0 then
                local e = self:IsNpcEnemyAround(simInstance, tbNpc)
                if e and e > 0 then tbNpc.foundNpcEnemy = e end
            end
            if tbNpc.foundNpcEnemy and tbNpc.foundNpcEnemy > 0 and NpcRun and GetNpcPos then
                local _ex, _ey = GetNpcPos(tbNpc.foundNpcEnemy)
                if _ex and _ey then
                    NpcRun(tbNpc.finalIndex, floor(_ex / 32), floor(_ey / 32))
                end
            end
            if self.Update then self:Update(simInstance, tbNpc) end
            if SIMBOT_COMBAT_DEBUG == 1 and Msg2Player and simInstance then
                local pId = simInstance.GetPlayer and simInstance:GetPlayer(nListId)
                if pId and pId > 0 then
                    Msg2Player(format("[SIMBOT_COMBAT_DEBUG] JoinFight bot=%s mode=%s enemy=%s reason=%s",
                        tostring(tbNpc.szName or tbNpc.finalIndex),
                        tostring(tbNpc.mode),
                        tostring(tbNpc.foundNpcEnemy or 0),
                        tostring(reason or "none")))
                end
            end
            return 1
        end
        tbNpc.entitySys:Respawn(simInstance, tbNpc, 3, "JoinFight " .. reason)      
        return 1
    end,

    IsParentFighting = function(self, simInstance, tbNpc)
        local foundParent = simInstance:Get(tbNpc.parentID)
        if foundParent and foundParent.isFighting == 1 then
            return 1
        end
        return 0
    end,

    GetFightingNPCs = function(self, simInstance, tbNpc, myPosX, myPosY)
        local countFighting = 0
        for key, fighter2 in simInstance.fighterList do
            if fighter2.finalIndex and fighter2.isDead == 0 and fighter2.id ~= tbNpc.id and fighter2.nMapId == tbNpc.nMapId and
                (fighter2.isFighting == 0 and IsAttackableCamp(fighter2.camp, tbNpc.camp) == 1) then
                local otherPosX, otherPosY, otherPosW = GetNpcPos(fighter2.finalIndex)
                otherPosX = floor(otherPosX / 32)
                otherPosY = floor(otherPosY / 32)

                local distance = floor(GetDistanceRadius(otherPosX, otherPosY, myPosX, myPosY))
                local checkDistance = tbNpc.RADIUS_FIGHT_NPC or RADIUS_FIGHT_NPC
                if distance < checkDistance then
                    countFighting = countFighting + 1
                    fighter2.fightSys:JoinFight(simInstance, fighter2, "caused by others " ..
                        distance .. " (" .. otherPosX ..
                        " " .. otherPosY .. ") (" .. myPosX .. " " .. myPosY .. ")")
                end
            end
        end
        return countFighting
    end,

    Update = execCastNormalSkill
}

SimFight.KeoXe = {
    LeaveFight = LeaveFight,
    BuffChar = BuffChar,
    execCastOnParent = execCastOnParent,
    execCastOnSelf = execCastOnSelf,
    TriggerFightWithNPC = function(self, simInstance, tbNpc)
        if tbNpc.isPlayerFighting == 0 then
            return 0
        end
        if (self:IsNpcEnemyAround(simInstance, tbNpc) > 0) then
            return self:JoinFight(simInstance, tbNpc, "enemy around")
        end
        return 0
    end,

    IsNpcEnemyAround = function(self, simInstance, tbNpc)
        local allNpcs = {}
        local nCount = 0
        local outdoorOk = tbNpc.worldInfo and tbNpc.worldInfo.allowFighting == 1 and tbNpc.worldInfo.cityPeace ~= 1
        local grind = (tbNpc.mode == "train" or outdoorOk)
        local radius = tbNpc.RADIUS_FIGHT_SCAN or RADIUS_FIGHT_SCAN
        if grind then
            radius = tbNpc.RADIUS_FIGHT_SCAN or 20
        end
        -- Keo xe?
        local pID = simInstance:GetPlayer(tbNpc.id)
        if pID > 0 then
            allNpcs, nCount = CallPlayerFunction(pID, GetAroundNpcList, radius)
            if not allNpcs or not nCount or nCount <= 0 then return 0 end

            local bestMonster = 0
            local bestKind0 = 0
            for i = 1, nCount do
                local idx = allNpcs[i]
                if idx and idx ~= tbNpc.finalIndex then
                    local isSim = GetNpcParam and (GetNpcParam(idx, 4) == 1)
                    if not isSim then
                        local fighter2Kind = GetNpcKind(idx)
                        local fighter2Camp = GetNpcCurCamp(idx)
                        local alive = 1
                        if NPCINFO_GetNpcCurrentLife then
                            local life = NPCINFO_GetNpcCurrentLife(idx)
                            if life ~= nil and life <= 0 then alive = 0 end
                        end
                        if alive == 1 then
                            if grind then
                                -- Prefer real monsters (kind ~= 0)
                                if fighter2Kind ~= nil and fighter2Kind ~= 0 then
                                    if bestMonster == 0 then bestMonster = idx end
                                elseif fighter2Kind == 0 then
                                    -- Only allow kind-0 player/PvP targets through explicit DoSat/hostile-PvP rules
                                    local isHostileKind0 = 0
                                    if tbNpc.isDoSat == 1 or tbNpc.camp == 5 then
                                        isHostileKind0 = 1
                                    elseif tbNpc.camp ~= 0 and IsAttackableCamp and IsAttackableCamp(tbNpc.camp, fighter2Camp) == 1 then
                                        isHostileKind0 = 1
                                    end
                                    if isHostileKind0 == 1 and bestKind0 == 0 then
                                        bestKind0 = idx
                                    end
                                end
                            elseif fighter2Kind == 0 and IsAttackableCamp(tbNpc.camp, fighter2Camp) == 1 then
                                return idx
                            end
                        end
                    end
                end
            end
            if bestMonster > 0 then return bestMonster end
            if bestKind0 > 0 then return bestKind0 end
        end
        return 0
    end,
    CanLeaveFight = function(self, simInstance, tbNpc)
        if tbNpc.isDead == 1 then
            return 0
        end

        -- No attacker around including NPC and Player ? Stop
        if (self:IsNpcEnemyAround(simInstance, tbNpc) == 0 and
                tbNpc.isPlayerEnemyAround == 0) then
            if (tbNpc.leaveFightWhenNoEnemy and tbNpc.leaveFightWhenNoEnemy > 0) then
                local realCanSwitchTick = tbNpc.tick_breath + tbNpc.leaveFightWhenNoEnemy - 1

                if tbNpc.tick_canswitch > realCanSwitchTick then
                    tbNpc.tick_canswitch = realCanSwitchTick
                end
            end

            return 1
        end
        return 0
    end,
    TriggerFightWithPlayer = function(self, simInstance, tbNpc)
        if tbNpc.isPlayerFighting == 0 then
            return 0
        end
        -- FIGHT other player        
        if tbNpc.isPlayerEnemyAround > 0 then
            return self:JoinFight(simInstance, tbNpc, "player around")
        end

        return 0
    end,
    SetFightState = function(self, tbNpc, mode, nX, nY)  
        
        -- Mode = 9 is no longer used
        if mode == 9 then 
            mode = 1            
        end

        --if mode == 9 then
        --    SetNpcAI(tbNpc.finalIndex, mode, 20, -1, -1, -1, -1, -1, 0, nX, nY)            
        --else
            SetNpcAI(tbNpc.finalIndex, mode)
        --end

        if tbNpc.mode == "tieuthiep" then
            if mode == 1 then 
                SetNpcKind(tbNpc.finalIndex, 0)
            else
                if tbNpc.mode == "train" or tbNpc.isAttackable == 1 then
                    SetNpcKind(tbNpc.finalIndex, 0)
                else
                    SetNpcKind(tbNpc.finalIndex, tbNpc.kind or 4)
                end
            end
            return 1
        end

        -- Combat bots stay kind=0 so players can PK them; kind=4 = unattackable NPC mode
        if tbNpc.mode == "train" or tbNpc.tongkim == 1 or tbNpc.isAttackable == 1 then
            SetNpcKind(tbNpc.finalIndex, 0)
        elseif tbNpc.isPlayerFighting == 0 then
            SetNpcKind(tbNpc.finalIndex, 0)
        else
            SetNpcKind(tbNpc.finalIndex, tbNpc.kind or 4)
        end
    end,
    JoinFight = function(self, simInstance, tbNpc, reason)
        local nListId = tbNpc.id
        tbNpc.isFighting = 1
        if SetNpcCombat then SetNpcCombat(tbNpc.finalIndex, 1, tbNpc.skillCastBua and tbNpc.skillCastBua[1] or 0) end 
        tbNpc.tick_canswitch = tbNpc.tick_breath +
            random(tbNpc.TIME_FIGHTING_minTs or TIME_FIGHTING.minTs,
                tbNpc.TIME_FIGHTING_maxTs or TIME_FIGHTING.maxTs) 

        reason = reason or "no reason"

        local playerID = simInstance:GetPlayer(nListId)
        if playerID <= 0 then
            return 0
        end
       
        local currX, currY, currW = GetNpcPos(tbNpc.finalIndex)
        if tbNpc.lastFightPos and (not tbNpc.mode or tbNpc.mode ~= "tieuthiep") then
            if tbNpc.lastFightPos.W == currW then
                if (GetDistanceRadius(tbNpc.lastFightPos.X/32, tbNpc.lastFightPos.Y/32, currX/32, currY/32) < 16) then
                    self:SetFightState(tbNpc, 9, currX, currY)
                    return 1
                end
            end
        end

        tbNpc.entitySys:Respawn(simInstance, tbNpc, 3, "JoinFight " .. reason)     
    
        return 1
    end,

    Update = execCastNormalSkill
} 

-- Helper function to create a movement behavior by name
function SimFightSys(tbNpc)     
    if tbNpc.role == "keoxe" then
        return SimFight.KeoXe
    end
    return SimFight.Citizen
end
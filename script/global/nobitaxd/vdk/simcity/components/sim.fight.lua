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
        if pW and pTileX and pTileY and pW == myW then
            local dist = GetDistanceRadius(myTileX, myTileY, pTileX, pTileY)
            local pNpcIdx = PIdx2NpcIdx and PIdx2NpcIdx(foundPlayerEnemy)
            local curLife = (pNpcIdx and NPCINFO_GetNpcCurrentLife and NPCINFO_GetNpcCurrentLife(pNpcIdx)) or 1000
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
    if not foundNpcEnemy or foundNpcEnemy <= 0 then
        local isNpcAround = (fightSys and fightSys.IsNpcEnemyAround) or (self and self.IsNpcEnemyAround) or (tbNpc.fightSys and tbNpc.fightSys.IsNpcEnemyAround) or (SimFight and SimFight.Citizen and SimFight.Citizen.IsNpcEnemyAround)
        if isNpcAround then
            foundNpcEnemy = isNpcAround(fightSys or self or tbNpc.fightSys or SimFight.Citizen, simInstance, tbNpc)
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
    if SimProgression and SimProgression.CanCastOnHorse then
        canHorse = SimProgression:CanCastOnHorse(skillId)
    end

    if canHorse == 0 then
        -- Skill bo chien: Xuong ngua
        if SetNpcRideHorse and tbNpc.isCurrentlyRiding ~= 0 then
            SetNpcRideHorse(tbNpc.finalIndex, 0)
        end
        tbNpc.isCurrentlyRiding = 0
    else
        -- Skill ky chien: Len ngua
        if SetNpcRideHorse and tbNpc.isCurrentlyRiding ~= 1 then
            SetNpcRideHorse(tbNpc.finalIndex, 1)
        end
        tbNpc.isCurrentlyRiding = 1
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
    if (isAllDead ~= 1 and tbNpc.kind ~= 3 and (tbNpc.kind ~= 4 or tbNpc.isAttackable == 1)) then        
        self:SetFightState(tbNpc, 0)
    else
        tbNpc.entitySys:Respawn(simInstance, tbNpc, isAllDead, reason)
    end
end
 

function execCastNormalSkill(self, simInstance, tbNpc)
    if not tbNpc or not tbNpc.finalIndex or tbNpc.finalIndex <= 0 then return end
    if not tbNpc.faction or not SimCityPhai[tbNpc.faction] then
        return
    end

    if tbNpc.fighting == 0 and tbNpc.isFighting ~= 1 then
        return
    end
    if (tbNpc.tick_canCast and tbNpc.tick_canCast > tbNpc.tick_breath) then
        return
    end

    local skillCount = getn(SimCityPhai[tbNpc.faction].normalCast)
    if skillCount == 0 and not tbNpc.skillCastBua then
        return
    end

    if tbNpc.isPlayerEnemyAround == 0 and (random(1, 1000) > 50) then
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

    local selectedSkill = SimPickSkill(tbNpc)
    if not selectedSkill or not selectedSkill[1] then return end
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
    if SimProgression and SimProgression.GetSkillAttackRadiusTiles then
        maxCastTiles = SimProgression:GetSkillAttackRadiusTiles(skillId)
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

    local isRanged = SimFight:IsRangedFaction(tbNpc.faction, tbNpc.weaponBranch)

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

    -- Cast skill combo
    SimFight:SetCombatState(tbNpc, SIM_COMBAT_STATE.COMBO, "casting combo")
    if SimMovement then SimMovement:SetState(tbNpc, SIM_MOVE_STATE.IDLE, "casting combo stationary") end
    SimApplyHorseCombat(tbNpc, skillId)

    if target.targetType == "player" then
        if BotDoSkill and target.npcIndex and target.npcIndex > 0 then
            local _r = BotDoSkill(tbNpc.finalIndex, skillId, skillLevel, target.npcIndex)
        else
            NpcCastSkill(tbNpc.finalIndex, skillId, skillLevel, target.worldX, target.worldY)
        end
        local cdTicks = (SimGear and SimGear.GetCastCooldownTicks and SimGear:GetCastCooldownTicks(tbNpc)) or (2*18/REFRESH_RATE)
        tbNpc.tick_canCast = tbNpc.tick_breath + cdTicks
        if SimGear and SimGear.ApplyCombatLeech then SimGear:ApplyCombatLeech(tbNpc, target.targetId, "player") end
        if SimProgression and SimProgression.AddExp and tbNpc.mode == "train" then
            SimProgression:AddExp(tbNpc, (tbNpc.level or 1) * 20)
        end
    else
        NpcCastSkill(tbNpc.finalIndex, skillId, skillLevel, target.worldX, target.worldY)
        local cdTicks = (SimGear and SimGear.GetCastCooldownTicks and SimGear:GetCastCooldownTicks(tbNpc)) or (2*18/REFRESH_RATE)
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
        local radius = tbNpc.RADIUS_FIGHT_SCAN or RADIUS_FIGHT_SCAN
        if tbNpc.mode == "train" or (tbNpc.worldInfo and tbNpc.worldInfo.allowFighting == 1 and tbNpc.worldInfo.cityPeace ~= 1) then
            radius = tbNpc.RADIUS_FIGHT_SCAN or 20
        end

        allNpcs, nCount = GetNpcAroundNpcList(tbNpc.finalIndex, radius)
        if not allNpcs or not nCount then return 0 end
        for i = 1, nCount do
            if allNpcs[i] ~= tbNpc.finalIndex then
                local fighter2Kind = GetNpcKind(allNpcs[i])
                local fighter2Camp = GetNpcCurCamp(allNpcs[i])
                if GetNpcParam and GetNpcParam(allNpcs[i], 4) == 1 then
                    -- skip other simbots
                elseif tbNpc.mode == "train" or (tbNpc.worldInfo and tbNpc.worldInfo.allowFighting == 1 and tbNpc.worldInfo.cityPeace ~= 1) then
                    -- Grind maps: any non-simbot NPC/monster
                    if fighter2Kind ~= nil then
                        return allNpcs[i]
                    end
                elseif fighter2Kind == 0 and IsAttackableCamp(tbNpc.camp, fighter2Camp) == 1 then
                    return allNpcs[i]
                end
            end
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


        -- If already having last fight pos, we may simply chance AI to 1
        local currX, currY, currW = GetNpcPos(tbNpc.finalIndex)
        if tbNpc.lastFightPos then
            if tbNpc.lastFightPos.W == currW then
                if (GetDistanceRadius(tbNpc.lastFightPos.X/32, tbNpc.lastFightPos.Y/32, currX/32, currY/32) < 16) then
                    self:SetFightState(tbNpc, 9, currX, currY)
                    return 1
                end
            end
        end
        
        local outdoorOk = tbNpc.worldInfo and tbNpc.worldInfo.allowFighting == 1 and tbNpc.worldInfo.cityPeace ~= 1
        if tbNpc.mode == "train" or outdoorOk then
            self:SetFightState(tbNpc, 9, currX, currY)
            if tbNpc.foundNpcEnemy and tbNpc.foundNpcEnemy > 0 then
                local _ex, _ey = GetNpcPos(tbNpc.foundNpcEnemy)
                if _ex and NpcRun then
                    NpcRun(tbNpc.finalIndex, floor(_ex/32), floor(_ey/32))
                end
            end
            if self.Update then self:Update(simInstance, tbNpc) end
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
        local radius = tbNpc.RADIUS_FIGHT_SCAN or RADIUS_FIGHT_SCAN
        -- Keo xe?
        local pID = simInstance:GetPlayer(tbNpc.id)
        if pID > 0 then
            allNpcs, nCount = CallPlayerFunction(pID, GetAroundNpcList, radius)
        
            for i = 1, nCount do
                if allNpcs[i] ~= tbNpc.finalIndex then
                    local fighter2Kind = GetNpcKind(allNpcs[i])
                    local fighter2Camp = GetNpcCurCamp(allNpcs[i])
                    if fighter2Kind == 0 and ((tbNpc.mode == "train" and GetNpcParam(allNpcs[i], 4) ~= 1) or (IsAttackableCamp(tbNpc.camp, fighter2Camp) == 1)) then  
                        return allNpcs[i]
                    end
                end
            end
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
                SetNpcKind(tbNpc.finalIndex, tbNpc.kind or 4)
            end
            return 1
        end

        if tbNpc.isPlayerFighting == 0 then
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
--========================================================
-- SIMBOT LUYEN CONG PLUGIN & DYNAMIC AOI SYSTEM (PHASE 4)
-- Engine JX1 Linux - Pure ASCII / ANSI Encoding
--========================================================

Include("\\script\\global\\nobitaxd\\vdk\\simcity\\components\\sim.gear.lua")
Include("\\script\\global\\nobitaxd\\vdk\\simcity\\components\\sim.progression.lua")

SimCityLuyenCong = {
    scanInterval = 15, -- Quet nguoi choi moi 15 giay
    hibernateTimeout = 120, -- Tu dong don dep sau 120 giay (2 phut) khong co nguoi
    lastScanTime = 0,
    mapState = {}
}

SimCityLuyenCong.TRAIN_MAPS = {
    [1] = { name = "Ba Lang Huyen (1-20)", mapId = 53, minLv = 1, maxLv = 20, count = 15 },
    [2] = { name = "Phuc Nguu Son (20-40)", mapId = 11, minLv = 20, maxLv = 40, count = 18 },
    [3] = { name = "Kinh Hoang Dong (40-60)", mapId = 17, minLv = 40, maxLv = 60, count = 20 },
    [4] = { name = "Lam Du Quan (60-80)", mapId = 70, minLv = 60, maxLv = 80, count = 20 },
    [5] = { name = "Dao Hoa Dao (80-90)", mapId = 181, minLv = 80, maxLv = 90, count = 22 },
    [6] = { name = "Truong Bach Son Nam (90-120)", mapId = 321, minLv = 90, maxLv = 120, count = 25 },
    [7] = { name = "Mac Bac Thao Nguyen (120-150)", mapId = 325, minLv = 120, maxLv = 150, count = 25 },
    [8] = { name = "Sa Mac Dia Dao (150-180)", mapId = 225, minLv = 150, maxLv = 180, count = 25 },
    [9] = { name = "Vi Son Dao (180-200)", mapId = 340, minLv = 180, maxLv = 200, count = 25 }
}

-- PK / Chat shouts for Do Sat (Camp 5) bots
SimCityLuyenCong.PK_SHOUTS = {
    "Bai train nay la cua bon tao, bien di!",
    "Do sat toan bo! Khong ai duoc tranh bai!",
    "Danh khong lai thi ve thanh duong thuong di!",
    "Ai cho may train o day? Chay mau di!",
    "Biet tay dai gia chua!"
}

function SimCityLuyenCong:init()
    for i = 1, getn(self.TRAIN_MAPS) do
        local m = self.TRAIN_MAPS[i]
        self.mapState[m.mapId] = {
            isSpawned = 0,
            lastPlayerSeen = 0,
            botCount = 0
        }
    end
end

function SimCityLuyenCong:GetPlayerCountInMap(nMapId)
    local nPlayers = 0
    local total = (GetPlayerCount and GetPlayerCount()) or 0
    if total <= 0 then return 0 end

    for i = 1, total do
        local pW, pX, pY = nil, nil, nil
        if CallPlayerFunction then
            pW, pX, pY = CallPlayerFunction(i, GetWorldPos)
        else
            local oldPIdx = PlayerIndex
            PlayerIndex = i
            pW, pX, pY = GetWorldPos()
            PlayerIndex = oldPIdx
        end
        if pW == nMapId then
            nPlayers = nPlayers + 1
        end
    end
    return nPlayers
end

function SimCityLuyenCong:countBotsInMap(mapId)
    local counter = 0
    if SimCitizen and SimCitizen.fighterList then
        for k, v in SimCitizen.fighterList do
            if v.nMapId and v.nMapId == mapId and v.mode == "train" and (v.isDead ~= 1) then
                counter = counter + 1
            end
        end
    end
    return counter
end

function SimCityLuyenCong:countGlobalTrainBots()
    local counter = 0
    if SimCitizen and SimCitizen.fighterList then
        for k, v in SimCitizen.fighterList do
            if v.mode == "train" and (v.isDead ~= 1) then
                counter = counter + 1
            end
        end
    end
    return counter
end

function SimCityLuyenCong:spawnForMap(mapIdx)
    local m = self.TRAIN_MAPS[mapIdx]
    if not m then return end

    local worldInfo = SimCityWorld:Get(m.mapId)
    if not worldInfo then return end

    worldInfo.allowFighting = 1
    worldInfo.showFightingArea = 0

    local maxPerMap = TRAIN_BOT_MAX_PER_MAP or 25
    local globalBudget = TRAIN_BOT_GLOBAL_BUDGET or 200
    local targetCount = m.count or 20
    if targetCount > maxPerMap then targetCount = maxPerMap end

    local curBots = self:countBotsInMap(m.mapId)
    if curBots >= targetCount then
        if not self.mapState[m.mapId] then self.mapState[m.mapId] = {} end
        self.mapState[m.mapId].isSpawned = 1
        self.mapState[m.mapId].botCount = curBots
        self.mapState[m.mapId].lastPlayerSeen = (GetGameTime and GetGameTime()) or 0
        return
    end

    local needed = targetCount - curBots
    local globalActive = self:countGlobalTrainBots()
    if (globalActive + needed) > globalBudget then
        needed = globalBudget - globalActive
    end
    if needed <= 0 then return end

    local spawnedCount = 0

    -- Lay pool NPC phu hop theo cap map
    local cap = 1
    if m.maxLv >= 150 then cap = 4
    elseif m.maxLv >= 90 then cap = 3
    elseif m.maxLv >= 60 then cap = 2
    else cap = 1 end

    local pool = (SimCityNPCInfo and SimCityNPCInfo.getPoolByCap and SimCityNPCInfo:getPoolByCap(cap)) or {}
    if not pool or getn(pool) == 0 then
        pool = { 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110 }
    end

    for i = 1, needed do
        local id = pool[random(1, getn(pool))]
        local lv = random(m.minLv, m.maxLv)

        -- 5-10% ty le bot bat Do Sat (Camp 5)
        local isDoSat = (random(1, 100) <= 8)
        local camp = (isDoSat and 5) or 0

        local tbNpc = {
            nNpcId = id,
            nMapId = m.mapId,
            mode = "train",
            level = lv,
            camp = camp,
            isFighting = 1,
            walkMode = "random",
            walkVar = 5,
            noRevive = 0,
            capHP = cap,
            ngoaitrang = 1,
            CHANCE_ATTACK_PLAYER = (isDoSat and 1) or 0,
            CHANCE_ATTACK_NPC = (isDoSat and 1) or 0,
            CHANCE_JOIN_FIGHT = 1,
            RADIUS_FIGHT_PLAYER = (isDoSat and 20) or 10,
            RADIUS_FIGHT_NPC = (isDoSat and 20) or 10
        }

        local nListId = SimCitizen:New(tbNpc)
        if nListId and nListId > 0 then
            spawnedCount = spawnedCount + 1
            local bot = SimCitizen:Get(nListId)
            if bot and bot.finalIndex and bot.finalIndex > 0 then
                if isDoSat and SimCityLuyenCong.PK_SHOUTS and getn(SimCityLuyenCong.PK_SHOUTS) > 0 then
                    local shout = SimCityLuyenCong.PK_SHOUTS[random(1, getn(SimCityLuyenCong.PK_SHOUTS))]
                    if NpcChat then NpcChat(bot.finalIndex, shout) end
                end
            end
        end
    end

    if not self.mapState[m.mapId] then
        self.mapState[m.mapId] = {}
    end
    self.mapState[m.mapId].isSpawned = 1
    self.mapState[m.mapId].botCount = curBots + spawnedCount
    self.mapState[m.mapId].lastPlayerSeen = (GetGameTime and GetGameTime()) or 0
end

function SimCityLuyenCong:hibernateMap(mapId)
    if SimCitizen and SimCitizen.ClearMap then
        SimCitizen:ClearMap(mapId, "train")
    end
    if self.mapState[mapId] then
        self.mapState[mapId].isSpawned = 0
        self.mapState[mapId].botCount = 0
    end
end

function SimCityLuyenCong:ATick()
    local curTime = (GetGameTime and GetGameTime()) or 0
    local interval = AOI_SCAN_INTERVAL or self.scanInterval or 15
    local timeout = AOI_HIBERNATE_TIMEOUT or self.hibernateTimeout or 120
    if (curTime - self.lastScanTime) < interval then
        return
    end
    self.lastScanTime = curTime

    for i = 1, getn(self.TRAIN_MAPS) do
        local m = self.TRAIN_MAPS[i]
        local mapId = m.mapId
        if not self.mapState[mapId] then
            self.mapState[mapId] = { isSpawned = 0, lastPlayerSeen = 0, botCount = 0 }
        end

        local state = self.mapState[mapId]
        local pCount = self:GetPlayerCountInMap(mapId)

        if pCount > 0 then
            state.lastPlayerSeen = curTime
            self:spawnForMap(i)
        else
            if state.isSpawned == 1 then
                local idleTime = curTime - state.lastPlayerSeen
                if idleTime >= timeout then
                    self:hibernateMap(mapId)
                end
            end
        end
    end
end

function SimCityLuyenCong:mainMenu()
    local text = "<color=yellow>=== HE THONG LUYEN CONG SIMBOT (DYNAMIC AOI) ===<color>\n"
    text = text .. "Trang thai phan bo Simbot luyen cong tu dong theo vi tri nguoi choi:\n"
    local tbSay = { text }

    for i = 1, getn(self.TRAIN_MAPS) do
        local m = self.TRAIN_MAPS[i]
        local state = self.mapState[m.mapId]
        local statusStr = (state and state.isSpawned == 1 and "<color=green>[Dang Hoat Dong - " .. (state.botCount or 0) .. " Bot]<color>") or "<color=gray>[Nghi / Hibernate 0% CPU]<color>"
        tinsert(tbSay, m.name .. " " .. statusStr .. "/#SimCityLuyenCong:spawnForMap(" .. i .. ")")
    end

    tinsert(tbSay, "Kich hoat toan bo cac map luyen cong/#SimCityLuyenCong:spawnAllMaps()")
    tinsert(tbSay, "Thu hoi / Don dep toan bo bot luyen cong/#SimCityLuyenCong:removeAll()")
    tinsert(tbSay, "Ket thuc doi thoai/no")
    CreateTaskSay(tbSay)
end

function SimCityLuyenCong:spawnAllMaps()
    for i = 1, getn(self.TRAIN_MAPS) do
        self:spawnForMap(i)
    end
    Msg2Player("Da kich hoat toan bo cac map luyen cong!")
end

function SimCityLuyenCong:removeAll()
    for i = 1, getn(self.TRAIN_MAPS) do
        self:hibernateMap(self.TRAIN_MAPS[i].mapId)
    end
    Msg2Player("Da thu hoi va don dep toan bo bot luyen cong tren cac ban do!")
end

function no()
end

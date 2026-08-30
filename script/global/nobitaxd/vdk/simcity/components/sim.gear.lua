--========================================================
-- SIMBOT VIRTUAL GEAR & ITEM INSPECTION SYSTEM (PHASE 2)
-- Engine JX1 Linux - Pure ASCII / ANSI Encoding
--========================================================

IncludeLib("NPCINFO")
Include("\\script\\global\\nobitaxd\\vdk\\simcity\\components\\sim.progression.lua")

SimGear = {}

-- Gear names database by tier and category
SimGear.TIER_NAMES = {
    [1] = { -- 1x (1-19)
        weapon = {"Doan Kiem 1x", "Lieu Diep Dao 1x", "Thiet Thuong 1x", "Dong Chuy 1x", "Moc Bong 1x", "Tieu No 1x", "Thiet Quyen 1x"},
        armor = "Bo Y 1x", helm = "Bo Khoi 1x", belt = "Bo Dai 1x", boots = "Bo Ngoa 1x",
        ring = "Dong Gioi Chi 1x", amulet = "Hac Ngoc Boi 1x",
        hpBonus = 50, spdBonus = 5, defBonus = 10
    },
    [2] = { -- 2x (20-29)
        weapon = {"Thanh Dong Kiem 2x", "Bach Luyen Dao 2x", "Huyen Thiet Thuong 2x", "Thiet Chuy 2x", "Truc Bong 2x", "Cung No 2x", "Cuong Thiet Quyen 2x"},
        armor = "Thanh Dong Giap 2x", helm = "Thanh Dong Khoi 2x", belt = "Thanh Dong Dai 2x", boots = "Thanh Dong Ngoa 2x",
        ring = "Bach Ngan Gioi Chi 2x", amulet = "Bach Ngoc Day Chuyen 2x",
        hpBonus = 150, spdBonus = 10, defBonus = 25
    },
    [3] = { -- 3x (30-39)
        weapon = {"Tuyet Anh Kiem 3x", "Tieu Dao Dao 3x", "Pha Quan Thuong 3x", "Loi Than Chuy 3x", "Lang Nha Bong 3x", "Tuyet Menh No 3x", "Ba Vuong Quyen 3x"},
        armor = "Thiet Giap 3x", helm = "Thiet Khoi 3x", belt = "Thiet Dai 3x", boots = "Thiet Ngoa 3x",
        ring = "Hong Ngoc Gioi Chi 3x", amulet = "Tu Tinh Day Chuyen 3x",
        hpBonus = 300, spdBonus = 15, defBonus = 45
    },
    [4] = { -- 4x (40-49)
        weapon = {"Huyen Thiet Trong Kiem 4x", "Yen Nguyet Dao 4x", "Xich Long Thuong 4x", "Cuong Phong Chuy 4x", "Ho Vi Bong 4x", "Than Co No 4x", "Long Trao Quyen 4x"},
        armor = "Khoa Long Giap 4x", helm = "Khoa Long Khoi 4x", belt = "Khoa Long Dai 4x", boots = "Khoa Long Ngoa 4x",
        ring = "Hoang Kim Gioi Chi 4x", amulet = "Phuong Hoang Boi 4x",
        hpBonus = 500, spdBonus = 20, defBonus = 70
    },
    [5] = { -- 5x (50-59)
        weapon = {"Long Tuyen Kiem 5x", "Long Lan Dao 5x", "Bat Xa Mau 5x", "Thien Dinh Chuy 5x", "Da Toa Bong 5x", "Cuu Cung No 5x", "Loi Quang Quyen 5x"},
        armor = "Kim Ti Giap 5x", helm = "Kim Ti Khoi 5x", belt = "Kim Ti Dai 5x", boots = "Kim Ti Ngoa 5x",
        ring = "Lam Bao Thach Gioi Chi 5x", amulet = "Thien Chau Day Chuyen 5x",
        hpBonus = 750, spdBonus = 25, defBonus = 100
    },
    [6] = { -- 6x (60-79)
        weapon = {"Bach Kim Kiem 6x", "Tram Ma Dao 6x", "Hung Loi Thuong 6x", "Tran Thien Chuy 6x", "Hang Ma Bong 6x", "Bat Quai No 6x", "La Han Quyen 6x"},
        armor = "Thien Tam Giap 6x", helm = "Thien Tam Khoi 6x", belt = "Thien Tam Dai 6x", boots = "Thien Tam Ngoa 6x",
        ring = "Luc Bao Thach Gioi Chi 6x", amulet = "Long Van Boi 6x",
        hpBonus = 1100, spdBonus = 30, defBonus = 140
    },
    [7] = { -- 8x (80-89)
        weapon = {"Tu Kim Kiem 8x", "Thanh Long Dao 8x", "Phuong Duc Thuong 8x", "Khai Son Chuy 8x", "Thau Cot Bong 8x", "Am Duong No 8x", "Kim Cang Quyen 8x"},
        armor = "Huyen Vu Giap 8x", helm = "Huyen Vu Khoi 8x", belt = "Huyen Vu Dai 8x", boots = "Huyen Vu Ngoa 8x",
        ring = "Cuu U Gioi Chi 8x", amulet = "Thien Menh Day Chuyen 8x",
        hpBonus = 1600, spdBonus = 35, defBonus = 190
    },
    [8] = { -- 9x (90-99)
        weapon = {"Cap Phong Chan Vo Kiem (HKMP)", "Ma Hoang Kho Lau Dao (HKMP)", "Dich Khai Tuong Tu Kham (HKMP)", "Tu Khong Gioi Dao (HKMP)", "U Lung Kim Cang Y (HKMP)", "Bao Vu Le Hoa No (HKMP)", "Dat Ma Quyen (HKMP)"},
        armor = "U Lung Kim Cang Bao (HKMP)", helm = "Dich Khai Phat Khoi (HKMP)", belt = "Thien Quang Boi Dai (HKMP)", boots = "Kim Phung Ngoa (HKMP)",
        ring = "Ma Dinh Gioi Chi (HKMP)", amulet = "Vo Gian Day Chuyen (HKMP)",
        hpBonus = 2200, spdBonus = 40, defBonus = 250
    },
    [9] = { -- 10x (100-119)
        weapon = {"Vo Danh Kiem (9x VIP)", "Huyet Kiem Dao (9x VIP)", "Long Dam Thuong (9x VIP)", "Pha Thien Chuy (9x VIP)", "Thien Ma Bong (9x VIP)", "Kham Long No (9x VIP)", "Bat Quai Quyen (9x VIP)"},
        armor = "An Bang Bang Tinh Bao", helm = "An Bang Bang Tinh Khoi", belt = "An Bang Bang Tinh Dai", boots = "An Bang Bang Tinh Ngoa",
        ring = "An Bang Ke Huyet Thach Gioi Chi", amulet = "An Bang Dien Hoang Thach Boi",
        hpBonus = 3000, spdBonus = 45, defBonus = 320
    },
    [10] = { -- 12x (120-149)
        weapon = {"Dinh Quoc Nhan Kiem (Set Dinh Quoc)", "Dinh Quoc Cuong Dao (Set Dinh Quoc)", "Dinh Quoc Ba Thuong (Set Dinh Quoc)", "Dinh Quoc Than Chuy (Set Dinh Quoc)", "Dinh Quoc Bong (Set Dinh Quoc)", "Dinh Quoc No (Set Dinh Quoc)", "Dinh Quoc Quyen (Set Dinh Quoc)"},
        armor = "Dinh Quoc Thanh Sa Truong Bao", helm = "Dinh Quoc Long Lan Phat Khoi", belt = "Dinh Quoc Ngan To Dai", boots = "Dinh Quoc Xich Te Ngoa",
        ring = "Nhu Tinh Gioi Chi (VIP)", amulet = "Hiep Cot Day Chuyen (VIP)",
        mantle = "Phi Phong Ngu Phong (Cap 120)",
        hpBonus = 4000, spdBonus = 50, defBonus = 400
    },
    [11] = { -- 15x (150-179)
        weapon = {"Than Binh 150: Cuu Chau Thien Ton Kiem", "Than Binh 150: Ba Dao Diet The", "Than Binh 150: Pha Thien Long Thuong", "Than Binh 150: Bat Bai Than Chuy", "Than Binh 150: Long Co Bong", "Than Binh 150: Than Co Liet No", "Than Binh 150: Kim Cang Bat Hoai Quyen"},
        armor = "Vo Song Chien Giap 150", helm = "Vo Song Chien Khoi 150", belt = "Vo Song Chien Dai 150", boots = "Vo Song Chien Ngoa 150",
        ring = "Chi Ton Nhan Gioi (VIP 150)", amulet = "Chi Ton Ngoc Boi (VIP 150)",
        mantle = "Phi Phong Kinh Thien (Cap 150)",
        hpBonus = 5500, spdBonus = 55, defBonus = 520
    },
    [12] = { -- 18x+ (180-200)
        weapon = {"Tuyet The Than Binh 180: Thien Ha De Nhat Kiem", "Tuyet The Than Binh 180: Cuong Long Diet The Dao", "Tuyet The Than Binh 180: Than Long Ba Thuong", "Tuyet The Than Binh 180: Thien Ton Thien Chuy", "Tuyet The Than Binh 180: Cuu U Ma Bong", "Tuyet The Than Binh 180: Vo Song Than No", "Tuyet The Than Binh 180: Thien Phat Than Chuong"},
        armor = "Chi Ton Than Long Giap 180", helm = "Chi Ton Than Long Khoi 180", belt = "Chi Ton Than Long Dai 180", boots = "Chi Ton Than Long Ngoa 180",
        ring = "Thien Dia Vo Cuc Nhan 180", amulet = "Thien Dia Vo Cuc Ngoc Boi 180",
        mantle = "Phi Phong Vo Song / Vo Dich (Cap 180+)",
        hpBonus = 7500, spdBonus = 60, defBonus = 680
    }
}

function SimGear:GetTierByLevel(level)
    level = level or 1
    if level < 20 then return 1
    elseif level < 30 then return 2
    elseif level < 40 then return 3
    elseif level < 50 then return 4
    elseif level < 60 then return 5
    elseif level < 80 then return 6
    elseif level < 90 then return 7
    elseif level < 100 then return 8
    elseif level < 120 then return 9
    elseif level < 150 then return 10
    elseif level < 180 then return 11
    else return 12 end
end

-- Generate full authentic virtual gear for a bot
function SimGear:GenerateGearForBot(tbNpc)
    if not tbNpc then return end
    local lv = tbNpc.level or 1
    local tier = self:GetTierByLevel(lv)
    local tData = self.TIER_NAMES[tier] or self.TIER_NAMES[1]

    local weaponList = tData.weapon
    local weaponName = weaponList[random(1, getn(weaponList))]

    local horseName = "Khong Co (Di Bo)"
    if lv >= 180 then horseName = "Sieu Quang / Han Huyet Long Cau (Cap 180)"
    elseif lv >= 150 then horseName = "Phien Vu / Xich Long Cau (Cap 150)"
    elseif lv >= 120 then horseName = "Bon Tieu / Phien Vu (Cap 120)"
    elseif lv >= 100 then horseName = "Phi Van / Bon Tieu (Cap 100)"
    elseif lv >= 80 then horseName = "O Van Dap Tuyet / Chieu Da Ngoc Su Tu (Cap 80)"
    elseif lv >= 60 then horseName = "Xich Tho / Dich Lo (Cap 60)"
    elseif lv >= 40 then horseName = "Dai Uyen / Hong Ma / Hoa Luu (Cap 40)"
    elseif lv >= 20 then horseName = "Tuc Suong / Hac Ma / Thanh Ma (Cap 20)"
    end

    tbNpc.virtualGear = {
        tier = tier,
        weapon = weaponName,
        armor = tData.armor,
        helm = tData.helm,
        belt = tData.belt,
        boots = tData.boots,
        ring1 = tData.ring,
        ring2 = tData.ring,
        amulet = tData.amulet,
        horse = horseName,
        mantle = tData.mantle or "Chua Dat Cap (Yeu Cau Cap 120+)",
        hpBonus = tData.hpBonus,
        spdBonus = tData.spdBonus,
        defBonus = tData.defBonus
    }

    return tbNpc.virtualGear
end

-- Calculate final stats with virtual gear applied
function SimGear:ApplyGearStats(tbNpc, nNpcIndex)
    if not tbNpc then return end
    nNpcIndex = nNpcIndex or tbNpc.finalIndex
    if not nNpcIndex or nNpcIndex <= 0 then return end

    if not tbNpc.virtualGear then
        self:GenerateGearForBot(tbNpc)
    end

    local lv = tbNpc.level or 1
    if SimProgression and SimProgression.CalcMaxHP then
        tbNpc.maxHP = SimProgression:CalcMaxHP(lv, tbNpc.faction)
    else
        tbNpc.maxHP = 250 + (lv * 35)
    end

    if SimProgression and SimProgression.CalcAtkSpeed then
        tbNpc.attackSpeed = SimProgression:CalcAtkSpeed(lv)
    else
        tbNpc.attackSpeed = 100
    end

    tbNpc.lastHP = tbNpc.lastHP or tbNpc.maxHP

    if SetNpcLevel then SetNpcLevel(nNpcIndex, lv) end
    if NPCINFO_SetNpcCurrentMaxLife then NPCINFO_SetNpcCurrentMaxLife(nNpcIndex, tbNpc.maxHP) end
    if NPCINFO_SetNpcCurrentLife then NPCINFO_SetNpcCurrentLife(nNpcIndex, tbNpc.lastHP) end
    if SetNpcAtkSpeed then SetNpcAtkSpeed(nNpcIndex, tbNpc.attackSpeed) end
end

-- Format detailed Inspection Dialog for player
function SimGear:GetInspectText(tbNpc)
    if not tbNpc then return "Khong co thong tin nhan vat." end
    if not tbNpc.virtualGear then self:GenerateGearForBot(tbNpc) end

    local g = tbNpc.virtualGear
    local name = tbNpc.szName or "Simbot"
    local fac = tbNpc.faction or "Chua Gia Nhap"
    local lv = tbNpc.level or 1
    local curHp = (tbNpc.finalIndex and NPCINFO_GetNpcCurrentLife and NPCINFO_GetNpcCurrentLife(tbNpc.finalIndex)) or tbNpc.lastHP or tbNpc.maxHP or 1000
    local maxHp = tbNpc.maxHP or 1000
    local spd = tbNpc.attackSpeed or 100

    local text = "<color=yellow>=== THONG TIN TRANG BI NHAN VAT ===<color>\\n"
    text = text .. "<color=cyan>Ten:<color> " .. name .. " | <color=cyan>Mon Phai:<color> " .. fac .. "\\n"
    text = text .. "<color=cyan>Cap Do:<color> " .. lv .. " | <color=cyan>Sinh Luc:<color> " .. curHp .. " / " .. maxHp .. "\\n"
    text = text .. "<color=cyan>Toc Do Xuat Chieu:<color> " .. spd .. " | <color=cyan>Phong Thu Cong Them:<color> +" .. (g.defBonus or 0) .. "\\n"
    text = text .. "-------------------------------------------\\n"
    text = text .. "<color=gold>[Vu Khi]:<color> " .. (g.weapon or "Khong Co") .. "\\n"
    text = text .. "<color=gold>[Y Phuc]:<color> " .. (g.armor or "Khong Co") .. "\\n"
    text = text .. "<color=gold>[Mu/Non]:<color> " .. (g.helm or "Khong Co") .. "\\n"
    text = text .. "<color=gold>[That Lung]:<color> " .. (g.belt or "Khong Co") .. "\\n"
    text = text .. "<color=gold>[Giay]:<color> " .. (g.boots or "Khong Co") .. "\\n"
    text = text .. "<color=gold>[Nhan 1]:<color> " .. (g.ring1 or "Khong Co") .. "\\n"
    text = text .. "<color=gold>[Nhan 2]:<color> " .. (g.ring2 or "Khong Co") .. "\\n"
    text = text .. "<color=gold>[Day Chuyen]:<color> " .. (g.amulet or "Khong Co") .. "\\n"
    text = text .. "<color=gold>[Thu Cuoi]:<color> " .. (g.horse or "Di Bo") .. "\\n"
    text = text .. "<color=gold>[Phi Phong]:<color> " .. (g.mantle or "Chua Co") .. "\\n"
    return text
end


-- Functional Gear Combat Helpers
function SimGear:GetSkillLevelBonus(tbNpc)
    if not tbNpc or not tbNpc.virtualGear then return 0 end
    local tier = tbNpc.virtualGear.tier or 1
    if tier >= 12 then return 10 -- Cap 180 Tuyet The Than Binh (+10 cap skill)
    elseif tier >= 11 then return 6  -- Cap 150 Than Binh (+6 cap skill)
    elseif tier >= 10 then return 4  -- Cap 120 Dinh Quoc (+4 cap skill)
    elseif tier >= 8 then return 3   -- Cap 90 HKMP (+3 cap skill)
    elseif tier >= 6 then return 2   -- Cap 60-80 (+2 cap skill)
    elseif tier >= 4 then return 1   -- Cap 40-50 (+1 cap skill)
    end
    return 0
end

function SimGear:GetCastCooldownTicks(tbNpc)
    local spd = (tbNpc and tbNpc.attackSpeed) or 100
    if spd >= 200 then
        return 1 -- Max toc danh: ra chieu lien tuc moi tick
    elseif spd >= 150 then
        return max(1, floor(1.4 * 18 / REFRESH_RATE))
    else
        return max(1, floor(2.0 * 18 / REFRESH_RATE))
    end
end

-- 10. COMBAT LIFE LEECH (PROBABILISTIC CAST-TRIGGERED LEECH)
-- Note on JX1 Engine Architecture:
-- In JX1 C-Engine, NpcCastSkill and BotDoSkill are asynchronous calls where projectile path,
-- hit registration and damage calculations are resolved asynchronously in core game ticks.
-- Therefore, combat life leech is implemented as probabilistic cast-triggered life leech (70% effective hit rate)
-- gated strictly by active enemy target presence (player or NPC) and tier-based life leech gear stats.
function SimGear:ApplyCombatLeech(tbNpc, targetIdx, targetType)
    if not tbNpc or not tbNpc.finalIndex or tbNpc.finalIndex <= 0 then return end
    if not tbNpc.virtualGear then return end
    local tier = tbNpc.virtualGear.tier or 1
    if tier < 5 then return end -- Chi do cap 5x tro len moi co dong Hut Sinh Luc

    -- Validate target index and target type (must be "player" or "npc")
    if not targetIdx or targetIdx <= 0 then return end
    if targetType ~= "player" and targetType ~= "npc" then return end

    -- Probabilistic hit roll (70% hit rate) per cast cycle
    if random(1, 100) > 70 then return end

    local leechRate = tier * 0.006 -- 3% toi 7.2%
    local curHp = (NPCINFO_GetNpcCurrentLife and NPCINFO_GetNpcCurrentLife(tbNpc.finalIndex)) or tbNpc.lastHP or 0
    local maxHp = tbNpc.maxHP or 2000
    if curHp > 0 and curHp < maxHp then
        local heal = floor(maxHp * leechRate)
        if heal < 10 then heal = 10 end
        local newHp = curHp + heal
        if newHp > maxHp then newHp = maxHp end
        tbNpc.lastHP = newHp
        if NPCINFO_SetNpcCurrentLife then NPCINFO_SetNpcCurrentLife(tbNpc.finalIndex, newHp) end
    end
end

--========================================================
-- SIMBOT PROGRESSION: CORE LEVEL, EXP & PERSISTENCE
-- Engine JX1 Linux - Pure ASCII / ANSI Encoding
--========================================================

SimProgression = {}

-- 1. BANG EXP YEU CAU CHO TUNG CAP DO (1 -> 150)
SimProgression.EXP_TABLE = {
    [1] = 100, [2] = 250, [3] = 450, [4] = 700, [5] = 1050,
    [6] = 1500, [7] = 2100, [8] = 2850, [9] = 3800, [10] = 5000,
    [11] = 6500, [12] = 8300, [13] = 10500, [14] = 13200, [15] = 16500,
    [16] = 20500, [17] = 25300, [18] = 31000, [19] = 37700, [20] = 45500,
    [21] = 54600, [22] = 65200, [23] = 77400, [24] = 91400, [25] = 107400,
    [26] = 125600, [27] = 146200, [28] = 169400, [29] = 195400, [30] = 224400,
    [31] = 257000, [32] = 293400, [33] = 333800, [34] = 378400, [35] = 427400,
    [36] = 481000, [37] = 539600, [38] = 603400, [39] = 672600, [40] = 747600,
    [41] = 828600, [42] = 916000, [43] = 1010000, [44] = 1111000, [45] = 1220000,
    [46] = 1337000, [47] = 1463000, [48] = 1598000, [49] = 1743000, [50] = 1900000,
    [51] = 2070000, [52] = 2253000, [53] = 2450000, [54] = 2662000, [55] = 2890000,
    [56] = 3135000, [57] = 3400000, [58] = 3685000, [59] = 3990000, [60] = 4320000,
    [61] = 4675000, [62] = 5055000, [63] = 5460000, [64] = 5900000, [65] = 6380000,
    [66] = 6900000, [67] = 7460000, [68] = 8060000, [69] = 8710000, [70] = 9420000,
    [71] = 10200000, [72] = 11050000, [73] = 12000000, [74] = 13050000, [75] = 14200000,
    [76] = 15500000, [77] = 16900000, [78] = 18450000, [79] = 20150000, [80] = 22000000,
    [81] = 24100000, [82] = 26400000, [83] = 29000000, [84] = 31900000, [85] = 35200000,
    [86] = 38900000, [87] = 43100000, [88] = 47800000, [89] = 53100000, [90] = 60000000,
    [91] = 68000000, [92] = 77000000, [93] = 87000000, [94] = 98000000, [95] = 110000000,
    [96] = 125000000, [97] = 142000000, [98] = 162000000, [99] = 185000000, [100] = 210000000
}

function SimProgression:GetExpRequired(level)
    level = level or 1
    if self.EXP_TABLE[level] then
        return self.EXP_TABLE[level]
    end
    return floor(210000000 + (level - 100) * 35000000)
end

-- 2. TINH TOAN SINH LUC (MAX HP) CHUAN CLASSIC VLTK1 (LINEAR GROWTH + GEAR)
function SimProgression:CalcBaseHP(level, faction)
    level = level or 1
    -- Linear base: 250 + level * 35 (Level 10: 600, Level 90: 3400, Level 150: 5500, Level 200: 7250)
    local baseHp = 250 + (level * 35)

    -- He so mon phai theo chuan VLTK1
    local mult = 1.0
    if faction == "thienvuong" or faction == "thieulam" then
        mult = 1.30 -- Tanker trau nhat
    elseif faction == "caibang" or faction == "vodang" or faction == "conlon" or faction == "thiennhan" then
        mult = 1.10 -- Dau si / Sat thu can bang
    elseif faction == "ngami" or faction == "thuyyen" then
        mult = 1.05 -- Ho tro / Noi cong
    elseif faction == "duongmon" or faction == "ngudoc" then
        mult = 0.90 -- Sat thu tam xa / Don doc (mau thap hon bu lai dame to)
    end

    return floor(baseHp * mult)
end

function SimProgression:CalcMaxHP(level, faction)
    level = level or 1
    local base = self:CalcBaseHP(level, faction)
    local tier = (SimGear and SimGear.GetTierByLevel and SimGear:GetTierByLevel(level)) or 1
    local gearBonus = 0
    if SimGear and SimGear.TIER_NAMES and SimGear.TIER_NAMES[tier] then
        gearBonus = SimGear.TIER_NAMES[tier].hpBonus or 0
    end
    return base + gearBonus
end

-- 3. TINH TOAN TOC DO XUAT CHIEU / TOC DO DANH (ATTACK SPEED)
function SimProgression:CalcAtkSpeed(level)
    level = level or 1
    local tier = (SimGear and SimGear.GetTierByLevel and SimGear:GetTierByLevel(level)) or 1
    local gearSpd = 0
    if SimGear and SimGear.TIER_NAMES and SimGear.TIER_NAMES[tier] then
        gearSpd = SimGear.TIER_NAMES[tier].spdBonus or 0
    end
    local spd = 100 + gearSpd + floor(level * 0.25)
    if spd > 250 then spd = 250 end
    return spd
end

-- 4. TINH TOAN SAT THUONG VA PHONG THU THEO CAP
function SimProgression:CalcDamageBonus(level, faction)
    level = level or 1
    local baseDmg = level * 10
    if faction == "duongmon" or faction == "ngudoc" or faction == "caibang" then
        baseDmg = floor(baseDmg * 1.25)
    end
    return baseDmg
end

function SimProgression:CalcDefenseBonus(level)
    level = level or 1
    local tier = (SimGear and SimGear.GetTierByLevel and SimGear:GetTierByLevel(level)) or 1
    local def = 20 + (level * 5)
    if SimGear and SimGear.TIER_NAMES and SimGear.TIER_NAMES[tier] then
        def = def + (SimGear.TIER_NAMES[tier].defBonus or 0)
    end
    return def
end

-- 4. BANG KY NANG 10 MON PHAI CHUAN XAC 100% (1 -> 180+)
SimProgression.FACTION_SKILLS = {
    thieulam = {
        taykhong = {
            { reqLv = 150, id = 1055 }, -- Dai Luc Kim Cang Chuong
            { reqLv = 90,  id = 318 },  -- Dat Ma Do Giang
            { reqLv = 60,  id = 272 },  -- Su Tu Hong
            { reqLv = 30,  id = 271 },  -- Long Trao Ho Trao
            { reqLv = 10,  id = 14 },   -- La Han Quyen
            { reqLv = 1,   id = 53 },
        },
        con = {
            { reqLv = 150, id = 1056 }, -- Vi Da Hien Xu
            { reqLv = 90,  id = 319 },  -- Hoanh Tao Thien Quan
            { reqLv = 60,  id = 216 },  -- Kim Cang Phuc Ma
            { reqLv = 30,  id = 19 },   -- Ma Ha Vo Luong
            { reqLv = 10,  id = 3 },    -- Thieu Lam Con Phap
            { reqLv = 1,   id = 53 },
        },
        dao = {
            { reqLv = 150, id = 1057 }, -- Tam Muoi Chan Hoa
            { reqLv = 90,  id = 321 },  -- Vo Tuong Tram
            { reqLv = 60,  id = 10 },   -- Kim Cang Phuc Ma
            { reqLv = 30,  id = 2 },    -- Thieu Lam Dao Phap
            { reqLv = 10,  id = 13 },   -- Hang Long Bat Vu
            { reqLv = 1,   id = 53 },
        }
    },
    thienvuong = {
        thuong = {
            { reqLv = 150, id = 1058 }, -- Hon Nguyen Nhat Khi Thuong
            { reqLv = 90,  id = 323 },  -- Truy Tinh Truc Nguyet
            { reqLv = 60,  id = 324 },  -- Doan Hon Thich
            { reqLv = 30,  id = 31 },   -- Huyet Chien Bat Phuong
            { reqLv = 10,  id = 25 },   -- Thien Vuong Thuong Phap
            { reqLv = 1,   id = 53 },
        },
        dao = {
            { reqLv = 150, id = 1059 }, -- Tram Long Dao Phap
            { reqLv = 90,  id = 322 },  -- Pha Thien Tram
            { reqLv = 60,  id = 32 },   -- Vo Dich Tram
            { reqLv = 30,  id = 31 },   -- Huyet Chien Bat Phuong
            { reqLv = 10,  id = 26 },   -- Thien Vuong Dao Phap
            { reqLv = 1,   id = 53 },
        },
        chuy = {
            { reqLv = 150, id = 1060 }, -- Ba Vuong Chuy
            { reqLv = 90,  id = 325 },  -- Truy Phong Quyet
            { reqLv = 60,  id = 28 },   -- Ba Vuong Thuong Phap
            { reqLv = 30,  id = 31 },   -- Huyet Chien Bat Phuong
            { reqLv = 10,  id = 27 },   -- Thien Vuong Chuy Phap
            { reqLv = 1,   id = 53 },
        }
    },
    duongmon = {
        amkhi = {
            { reqLv = 150, id = 1069 }, -- Bao Vu Tuyet Menh Tieu
            { reqLv = 90,  id = 302 },  -- Bao Vu Le Hoa
            { reqLv = 60,  id = 341 },  -- Tan Hoa Tieu
            { reqLv = 30,  id = 57 },   -- Bang Phach Han Quang
            { reqLv = 10,  id = 47 },   -- Doat Hon Phi Tieu
            { reqLv = 1,   id = 53 },
        },
        phi_dao = {
            { reqLv = 150, id = 1070 }, -- Cuu Cung Tuyet Anh
            { reqLv = 90,  id = 342 },  -- Cuu Cung Phi Tinh
            { reqLv = 60,  id = 54 },   -- Man Thien Hoa Vu
            { reqLv = 30,  id = 50 },   -- Truy Tam Tien
            { reqLv = 10,  id = 43 },   -- Duong Mon Am Khi
            { reqLv = 1,   id = 53 },
        },
        bay = {
            { reqLv = 150, id = 1071 }, -- Loan Hoan Tuyet Sat
            { reqLv = 90,  id = 339 },  -- Nhiep Hon Nguyet Anh
            { reqLv = 60,  id = 351 },  -- Loan Hoan Kich
            { reqLv = 30,  id = 59 },   -- Cuu Cung Dia Sat
            { reqLv = 10,  id = 52 },   -- Doc Thich Cot
            { reqLv = 1,   id = 53 },
        }
    },
    ngudoc = {
        chuong = {
            { reqLv = 150, id = 1066 }, -- Van Co Doc Ton
            { reqLv = 90,  id = 353 },  -- Am Phong Thuc Cot
            { reqLv = 60,  id = 73 },   -- Doc Sa Hu Cot
            { reqLv = 30,  id = 68 },   -- Van Co Kho Lau
            { reqLv = 10,  id = 60 },   -- Ngu Doc Chuong Phap
            { reqLv = 1,   id = 53 },
        },
        dao = {
            { reqLv = 150, id = 1067 }, -- Huyen Am Tuyet Sat
            { reqLv = 90,  id = 355 },  -- Huyen Am Tram
            { reqLv = 60,  id = 74 },   -- Xuyen Tam Doc
            { reqLv = 30,  id = 64 },   -- Bach Doc Xuyen Tam
            { reqLv = 10,  id = 62 },   -- Ngu Doc Dao Phap
            { reqLv = 1,   id = 53 },
        },
        bua = {
            { reqLv = 150, id = 1066 }, -- Van Co Doc Ton
            { reqLv = 90,  id = 390 },  -- Doan Can Hu Cot
            { reqLv = 60,  id = 69 },   -- Vo Hinh Doc
            { reqLv = 30,  id = 66 },   -- On Dich Thuat
            { reqLv = 10,  id = 65 },   -- Huyet Sat Doc
            { reqLv = 1,   id = 53 },
        }
    },
    ngami = {
        kiem = {
            { reqLv = 150, id = 1061 }, -- Cuu Kiem Hop Nhat
            { reqLv = 90,  id = 328 },  -- Tam Nga Te Tuyet
            { reqLv = 60,  id = 88 },   -- Bat Diet Bat Tuyet
            { reqLv = 30,  id = 85 },   -- Nhat Diep Tri Thu
            { reqLv = 10,  id = 77 },   -- Nga Mi Kiem Phap
            { reqLv = 1,   id = 53 },
        },
        chuong = {
            { reqLv = 150, id = 1062 }, -- Bang Vu Lac Cuu Thien
            { reqLv = 90,  id = 380 },  -- Phong Suong Toai Anh
            { reqLv = 60,  id = 91 },   -- Phat Quang Pho Chieu
            { reqLv = 30,  id = 93 },   -- Tu Tuong Pho Do
            { reqLv = 10,  id = 80 },   -- Phieu Tuyet Xuyen Van
            { reqLv = 1,   id = 53 },
        },
        buff = {
            { reqLv = 150, id = 1114 }, -- Phat Quang Tuyet Sat
            { reqLv = 90,  id = 332 },  -- Pho Do Chung Sinh
            { reqLv = 60,  id = 252 },  -- Vo Bien Te Ma
            { reqLv = 30,  id = 89 },   -- Mong Diep
            { reqLv = 10,  id = 79 },   -- Nga Mi Chuong Phap
            { reqLv = 1,   id = 53 },
        }
    },
    thuyyen = {
        dao = {
            { reqLv = 150, id = 1063 }, -- Bang Tam Tuyet Anh
            { reqLv = 90,  id = 336 },  -- Bang Tung Vo Anh
            { reqLv = 60,  id = 105 },  -- Bang Tung Diet Tuyet
            { reqLv = 30,  id = 100 },  -- Bang Han Tieu
            { reqLv = 10,  id = 95 },   -- Thuy Yen Dao Phap
            { reqLv = 1,   id = 53 },
        },
        songdao = {
            { reqLv = 150, id = 1065 }, -- Phong Hoa Tuyet Dai
            { reqLv = 90,  id = 337 },  -- Bang Tam Tien Tu
            { reqLv = 60,  id = 109 },  -- Tuyet Anh
            { reqLv = 30,  id = 102 },  -- Phong Quyen Tan Tuyet
            { reqLv = 10,  id = 97 },   -- Thuy Yen Song Dao
            { reqLv = 1,   id = 53 },
        }
    },
    caibang = {
        chuong = {
            { reqLv = 150, id = 1073 }, -- Khang Long Huu Hoi 150
            { reqLv = 90,  id = 357 },  -- Phi Long Tai Thien
            { reqLv = 60,  id = 120 },  -- Khang Long Huu Hoi
            { reqLv = 30,  id = 119 },  -- Diet Hoa Chuong
            { reqLv = 10,  id = 112 },  -- Kien Long Tai Dien
            { reqLv = 1,   id = 53 },
        },
        bong = {
            { reqLv = 150, id = 1074 }, -- Bong Da Ac Cau 150
            { reqLv = 90,  id = 359 },  -- Thien Ha Vo Cau
            { reqLv = 60,  id = 123 },  -- Bong Da Ac Cau
            { reqLv = 30,  id = 121 },  -- Bong Da Ac Cau 30
            { reqLv = 10,  id = 115 },  -- Cai Bang Bong Phap
            { reqLv = 1,   id = 53 },
        }
    },
    thiennhan = {
        dao = {
            { reqLv = 150, id = 1076 }, -- Van Long Tuyet Sat
            { reqLv = 90,  id = 361 },  -- Van Long Kich
            { reqLv = 60,  id = 563 },  -- Bi Ma Huyet Quang
            { reqLv = 30,  id = 137 },  -- Ao Anh Phi Ho
            { reqLv = 10,  id = 131 },  -- Thien Nhan Dao Phap
            { reqLv = 1,   id = 53 },
        },
        chuong = {
            { reqLv = 150, id = 1075 }, -- Ma Diem Tuyet Sat
            { reqLv = 90,  id = 362 },  -- Thien Ngoai Luu Tinh
            { reqLv = 60,  id = 141 },  -- Liet Hoa Tinh Thien
            { reqLv = 30,  id = 138 },  -- Thoi Son Dien Hai
            { reqLv = 10,  id = 135 },  -- Tan Huyet Chi
            { reqLv = 1,   id = 53 },
        },
        bua = {
            { reqLv = 150, id = 1075 }, -- Ma Diem Tuyet Sat
            { reqLv = 90,  id = 391 },  -- Nhiep Hon Loan Tam
            { reqLv = 60,  id = 139 },  -- Thien Ma Giai The
            { reqLv = 30,  id = 140 },  -- Phi Ho Vo Kich
            { reqLv = 10,  id = 145 },  -- Dao Chi Cuong
            { reqLv = 1,   id = 53 },
        }
    },
    vodang = {
        kiem = {
            { reqLv = 150, id = 1079 }, -- Vo Nga Vo Kiem 150
            { reqLv = 90,  id = 368 },  -- Nhan Kiem Hop Nhat
            { reqLv = 60,  id = 164 },  -- Kiem Phi Kinh Thien
            { reqLv = 30,  id = 158 },  -- That Tinh Quyet
            { reqLv = 10,  id = 151 },  -- Vo Dang Kiem Phap
            { reqLv = 1,   id = 53 },
        },
        chuong = {
            { reqLv = 150, id = 1078 }, -- Thai Cuc Vo Luong
            { reqLv = 90,  id = 365 },  -- Thien Dia Vo Cuc
            { reqLv = 60,  id = 165 },  -- Vo Nga Vo Kiem
            { reqLv = 30,  id = 159 },  -- Bat Quai Du Long
            { reqLv = 10,  id = 153 },  -- No Loi Chi
            { reqLv = 1,   id = 53 },
        }
    },
    conlon = {
        dao = {
            { reqLv = 150, id = 1081 }, -- Ngao Tuyet Tuyet Sat
            { reqLv = 90,  id = 372 },  -- Ngao Tuyet Tieu Phong
            { reqLv = 60,  id = 178 },  -- Nhat Khi Tam Thanh
            { reqLv = 30,  id = 172 },  -- Tan Loi Quyet
            { reqLv = 10,  id = 167 },  -- Con Lon Dao Phap
            { reqLv = 1,   id = 53 },
        },
        kiem = {
            { reqLv = 150, id = 1080 }, -- Cuu Thien Cuong Loi
            { reqLv = 90,  id = 375 },  -- Loi Dong Cuu Thien
            { reqLv = 60,  id = 173 },  -- Ngu Loi Chanh Phap
            { reqLv = 30,  id = 169 },  -- Cuong Phong Bao Vu
            { reqLv = 10,  id = 168 },  -- Con Lon Kiem Phap
            { reqLv = 1,   id = 53 },
        },
        bua = {
            { reqLv = 150, id = 1080 }, -- Cuu Thien Cuong Loi
            { reqLv = 90,  id = 394 },  -- Tuy Tien Tao Cot
            { reqLv = 60,  id = 176 },  -- Thien Thanh Dia Truc
            { reqLv = 30,  id = 171 },  -- Thanh Phong Phu
            { reqLv = 10,  id = 179 },  -- Ho Phong Phap
            { reqLv = 1,   id = 53 },
        }
    }
}

-- 5. BANG TRA CUU KY CHIEN (HORSE SKILLS: HorseLimit >= 1 in skills.txt)
SimProgression.HORSE_SKILLS = {
    [10] = 1, [17] = 1, [30] = 1, [47] = 1, [50] = 1, [54] = 1,
    [85] = 1, [91] = 1, [102] = 1, [128] = 1, [155] = 1, [164] = 1,
    [271] = 1, [283] = 1, [284] = 1, [286] = 1, [288] = 1, [290] = 1,
    [302] = 1, [304] = 1, [321] = 1, [322] = 1, [323] = 1, [325] = 1,
    [342] = 1, [351] = 1, [361] = 1, [362] = 1, [373] = 1, [375] = 1,
    [389] = 1, [429] = 1, [1055] = 1, [1058] = 1, [1059] = 1, [1060] = 1,
    [1069] = 1, [1070] = 1, [1076] = 1, [1109] = 1
}

function SimProgression:CanCastOnHorse(skillId)
    if not skillId or skillId <= 0 then return 0 end
    return self.HORSE_SKILLS[skillId] or 0
end

-- 6. TINH TOAN CAP DO SKILL THEO CAP NHAN VAT
function SimProgression:CalcSkillLevel(level, reqLv)
    level = level or 1
    reqLv = reqLv or 1
    if level < reqLv then return 1 end

    local diff = level - reqLv
    local skLv = 1 + floor(diff / 4)
    if skLv > 20 then skLv = 20 end
    if skLv < 1 then skLv = 1 end
    return skLv
end

-- 7. CAP NHAT SKILL DONG CHO BOT
function SimProgression:UpdateBotSkills(tbNpc)
    if not tbNpc then return end
    local fac = tbNpc.faction or "thieulam"
    local branch = tbNpc.weaponBranch
    local lv = tbNpc.level or 1

    local facTable = self.FACTION_SKILLS[fac]
    if not facTable then
        facTable = self.FACTION_SKILLS["thieulam"]
    end

    if not branch or not facTable[branch] then
        local firstBranch = nil
        for bName, _ in pairs(facTable) do
            firstBranch = bName
            break
        end
        branch = firstBranch or "taykhong"
        tbNpc.weaponBranch = branch
    end

    local skillList = facTable[branch]
    local chosenSkillId = 53
    local chosenReqLv = 1

    for i = 1, getn(skillList) do
        local entry = skillList[i]
        if lv >= entry.reqLv then
            chosenSkillId = entry.id
            chosenReqLv = entry.reqLv
            break
        end
    end

    local skLevel = self:CalcSkillLevel(lv, chosenReqLv)
    tbNpc.skillCastBua = { chosenSkillId, skLevel }
    tbNpc.skillCastBuaNoDebuff = { chosenSkillId, skLevel }
    tbNpc.attackSpeed = self:CalcAtkSpeed(lv)
end

-- 8. CAP NHAT NGOAI TRANG VA THU CUOI THEO CHUAN VLTK1 KINH DIEN
function SimProgression:ApplyGearByLevel(tbNpc, nNpcIndex)
    if not tbNpc or not nNpcIndex or nNpcIndex <= 0 then return end
    local lv = tbNpc.level or 1
    local charType = tbNpc.nSettingsIdx or -1
    if tbNpc.series == 0 then charType = -1 elseif tbNpc.series == 2 then charType = -2 end
    if charType ~= -1 and charType ~= -2 then charType = -1 end
    tbNpc.nSettingsIdx = charType

    local helm = 0
    local armor = 0
    local horse = 0
    local isRide = 0
    local weapon = 0

    if lv < 10 then
        -- Cap 1 - 9: Di bo, ao vai tan thu, tay khong / con go
        helm = 0
        armor = 18
        horse = 0
        isRide = 0
        weapon = 0
    elseif lv < 20 then
        -- Cap 10 - 19: Di bo, Sa Di / Sa Ni phuc, non vai, vk 1x
        helm = 0
        armor = 0
        horse = 0
        isRide = 0
        weapon = 1
    elseif lv < 30 then
        -- Cap 20 - 29: Ngua cap 20 (Tuc Suong / Hac Ma), Do xanh 2x, Non 2x, VK 2x
        helm = 1
        armor = (charType == -2) and 6 or 2
        horse = 9 -- Tuc Suong
        isRide = 1
        weapon = 2
    elseif lv < 40 then
        -- Cap 30 - 39: Ngua cap 20/30 (Hoang Ma / Tuc Suong), Do xanh 3x, Non 3x, VK 3x
        helm = 2
        armor = (charType == -2) and 7 or 8
        horse = 10 -- Hoang Ma
        isRide = 1
        weapon = 5
    elseif lv < 50 then
        -- Cap 40 - 49: Ngua cap 40 (Dai Uyen / Hac Ma), Do xanh 4x, Non 4x, VK 4x
        helm = 6
        armor = (charType == -2) and 8 or 9
        horse = 5 -- Dai Uyen Hac Ma cap 40
        isRide = 1
        weapon = 8
    elseif lv < 60 then
        -- Cap 50 - 59: Ngua cap 40/50 (Hoa Luu / Hong Ma), Do xanh 5x, Non 5x, VK 5x
        helm = 7
        armor = (charType == -2) and 9 or 10
        horse = 8 -- Hong Ma / Hoa Luu cap 40/50
        isRide = 1
        weapon = 11
    elseif lv < 80 then
        -- Cap 60 - 79: Ngua cap 60 (Xich Tho / Dich Lo), Do xanh 6x-7x, Non 6x, VK 6x-7x
        helm = 8
        armor = (charType == -2) and 10 or 11
        horse = 2 -- Xich Tho cap 60
        isRide = 1
        weapon = 14
    elseif lv < 90 then
        -- Cap 80 - 89: Ngua cap 80 (O Van Dap Tuyet / Tuyet Anh), Do xanh 8x, Non 8x, VK 8x phat sang
        helm = 10
        armor = (charType == -2) and 11 or 13
        horse = 7 -- O Van Dap Tuyet cap 80
        isRide = 1
        weapon = 20
    elseif lv < 100 then
        -- Cap 90 - 99: Chieu Da Ngoc Su Tu / O Van, Do xanh 9x / HKMP, Non 9x, VK 9x Hoang Kim
        helm = 11
        armor = (charType == -2) and 14 or 14
        horse = 3 -- Chieu Da Ngoc Su Tu cap 80/90
        isRide = 1
        weapon = 28
    elseif lv < 110 then
        -- Cap 100 - 109: Chieu Da Ngoc Su Tu (hiem hon Phi Van), Do 9x ngon / HKMP
        helm = 11
        armor = (charType == -2) and 14 or 14
        horse = 3 -- Chieu Da Ngoc Su Tu
        isRide = 1
        weapon = 28
    elseif lv < 120 then
        -- Cap 110 - 119: Phi Van / Bon Tieu, HKMP / Hiep Cot - Nhu Tinh
        helm = 11
        armor = (charType == -2) and 14 or 14
        horse = 12 -- Bon Tieu / Phi Van
        isRide = 1
        weapon = 28
    elseif lv < 150 then
        -- Cap 120 - 149: Bon Tieu / Phien Vu, HKMP / Dinh Quoc / An Bang
        helm = 13
        armor = (charType == -2) and 19 or 19
        horse = 12 -- Bon Tieu
        isRide = 1
        weapon = 30
    elseif lv < 180 then
        -- Cap 150 - 179: Phien Vu / Xich Long Cau / Tuyet Dia, Dinh Quoc / An Bang / HKMP cao cap
        helm = 14
        armor = (charType == -2) and 20 or 20
        horse = 13 -- Phien Vu
        isRide = 1
        weapon = 32
    else
        -- Cap 180+: Sieu Quang / Han Huyet Long Cau / Than Thu, An Bang / End-game
        helm = 20
        armor = (charType == -2) and 35 or 41
        horse = 19 -- Sieu Quang
        isRide = 1
        weapon = 32
    end

    if tbNpc.nNewWeaponType and tbNpc.nNewWeaponType > 0 then
        weapon = tbNpc.nNewWeaponType
    end

    tbNpc.nNewHelmType = helm
    tbNpc.nNewArmorType = armor
    tbNpc.nNewHorseType = horse
    tbNpc.nNewWeaponType = weapon

    if ChangeNpcFeature then
        ChangeNpcFeature(nNpcIndex, 0, 0, charType, helm, armor, weapon, horse)
    end
    if SetNpcRideHorse then
        SetNpcRideHorse(nNpcIndex, isRide)
    end
end

-- 9. LOGIC THEM EXP VA THANG CAP
function SimProgression:AddExp(tbNpc, nExp)
    if not tbNpc or not nExp or nExp <= 0 then return end
    tbNpc.level = tbNpc.level or 1
    tbNpc.nExp = (tbNpc.nExp or 0) + nExp

    local leveledUp = 0
    local maxLevel = SIMBOT_MAX_LEVEL or 200
    local reqExp = self:GetExpRequired(tbNpc.level)

    while tbNpc.nExp >= reqExp and tbNpc.level < maxLevel do
        tbNpc.nExp = tbNpc.nExp - reqExp
        tbNpc.level = tbNpc.level + 1
        leveledUp = leveledUp + 1
        reqExp = self:GetExpRequired(tbNpc.level)
    end

    if leveledUp > 0 then
        self:OnLevelUp(tbNpc)
    end
end

-- 10. XU LY SU KIEN THANG CAP
function SimProgression:OnLevelUp(tbNpc)
    if not tbNpc then return end
    local nIdx = tbNpc.finalIndex
    local newLv = tbNpc.level or 1

    if nIdx and nIdx > 0 then
        if SetNpcLevel then
            SetNpcLevel(nIdx, newLv)
        end
        tbNpc.maxHP = self:CalcMaxHP(newLv, tbNpc.faction)
        tbNpc.lastHP = tbNpc.maxHP
        if NPCINFO_SetNpcCurrentMaxLife then NPCINFO_SetNpcCurrentMaxLife(nIdx, tbNpc.maxHP) end
        if NPCINFO_SetNpcCurrentLife then NPCINFO_SetNpcCurrentLife(nIdx, tbNpc.maxHP) end
        self:ApplyGearByLevel(tbNpc, nIdx)
    end

    self:UpdateBotSkills(tbNpc)

    if tbNpc.ownerName and tbNpc.ownerName ~= "" then
        local pIdx = SearchPlayer(tbNpc.ownerName)
        if pIdx and pIdx > 0 then
            local botName = tbNpc.szName or "DocCoCauBai"
            CallPlayerFunction(pIdx, Msg2Player, format("<color=yellow>[Simbot]<color> <color=green>%s<color> da thang len cap <color=red>%d<color>!", botName, newLv))
        end
    end
end


-- 10.5. SANITIZATION & PATH SECURITY
function SimProgression:SanitizeName(szName)
    if not szName or type(szName) ~= "string" or szName == "" then
        return "DocCoCauBai"
    end
    local clean = gsub(szName, "%c", "")
    clean = gsub(clean, "|", "")
    clean = gsub(clean, "/", "")
    clean = gsub(clean, "\\", "")
    clean = gsub(clean, "%.%.", "")
    if clean == "" then
        return "DocCoCauBai"
    end
    return clean
end

-- 10.6. PERSISTENCE: LUU VA DOC ROSTER SIMBOT LUYEN CONG (ATOMIC SAVE)
local function _sim_open(path, mode)
    if openfile then return openfile(path, mode) end
    if io and io.open then return io.open(path, mode) end
    return nil
end
local function _sim_close(f)
    if not f then return end
    if closefile then return closefile(f) end
    if f.close then return f:close() end
end
local function _sim_read(f, mode)
    if not f then return nil end
    if read then return read(f, mode) end
    if f.read then return f:read(mode) end
    return nil
end
local function _sim_write(f, str)
    if not f or not str then return end
    if write then return write(f, str) end
    if f.write then return f:write(str) end
end
-- Helper function for atomic file rename
-- On Linux / POSIX game server (GLIBC), rename(2) is guaranteed atomic and replaces existing destination files
-- on the same filesystem without requiring pre-deletion. renamefile in JX1 C-engine maps directly to this syscall.
local function _sim_rename(oldp, newp)
    if renamefile then
        local r1, r2 = pcall(renamefile, oldp, newp)
        if r1 and (r2 == 1 or r2 == true) then return 1 end
        return 0
    end
    if os and os.rename then
        local ok, err = os.rename(oldp, newp)
        if ok then return 1 end
    end
    return 0
end

function SimProgression:SaveTrainBots(mapId, botList)
    if not mapId or mapId <= 0 then return 0 end
    local szDir = "save/simcity"
    local szPath = format("%s/train_map_%d.dat", szDir, mapId)
    local szTmpPath = format("%s/train_map_%d.dat.tmp", szDir, mapId)

    local f = _sim_open(szTmpPath, "w")
    if not f then return 0 end

    local count = (botList and getn(botList)) or 0
    local curTime = (GetGameTime and GetGameTime()) or 0
    _sim_write(f, format("SIMROSTER_V1|%d|%d|%d\n", mapId, curTime, count))

    if botList then
        for i = 1, count do
            local b = botList[i]
            if b then
                local sName = self:SanitizeName(b.szName or "DocCoCauBai")
                local line = format("%s|%d|%d|%s|%d|%s|%d|%d|%s\n",
                    sName,
                    b.level or 1,
                    b.nExp or 0,
                    b.faction or "thieulam",
                    b.series or 0,
                    b.weaponBranch or "taykhong",
                    b.nNpcId or 100,
                    b.camp or 0,
                    b.personality or "balanced"
                )
                _sim_write(f, line)
            end
        end
    end

    _sim_close(f)
    local renOk = _sim_rename(szTmpPath, szPath)
    if renOk ~= 1 then
        if removefile then pcall(removefile, szTmpPath) end
        if os and os.remove then pcall(os.remove, szTmpPath) end
        return 0
    end
    return 1
end

function SimProgression:LoadTrainBots(mapId)
    if not mapId or mapId <= 0 then return {} end
    local szPath = format("save/simcity/train_map_%d.dat", mapId)
    local f = _sim_open(szPath, "r")
    if not f then return {} end

    local header = _sim_read(f, "*l")
    if not header or not strfind(header, "SIMROSTER_V1") then
        _sim_close(f)
        return {}
    end

    local roster = {}
    local line = _sim_read(f, "*l")
    while line do
        if line ~= "" and strsub(line, 1, 1) ~= "#" then
            line = gsub(line, "%c", "")
            local tokens = split(line, "|")
            if tokens and getn(tokens) >= 7 then
                local botData = {
                    szName = self:SanitizeName(tokens[1]),
                    level = tonumber(tokens[2]) or 1,
                    nExp = tonumber(tokens[3]) or 0,
                    faction = tokens[4] or "thieulam",
                    series = tonumber(tokens[5]) or 0,
                    weaponBranch = tokens[6] or "taykhong",
                    nNpcId = tonumber(tokens[7]) or 100,
                    camp = (tokens[8] and tonumber(tokens[8])) or 0,
                    personality = tokens[9] or "balanced"
                }
                tinsert(roster, botData)
            end
        end
        line = _sim_read(f, "*l")
    end
    _sim_close(f)
    return roster
end

-- 11. PERSISTENCE: LUU VA DOC DAN XE (KEO XE)
function SimProgression:SaveKeoXe(szPlayerName, tbXeList)
    if not szPlayerName or szPlayerName == "" then return 0 end
    local szPath = format("dulieu/simcity/keoxe_%s.txt", szPlayerName)
    local f = openfile(szPath, "w")
    if not f then return 0 end

    write(f, "# SIMCITY KEOXE DATA PERSISTENCE\n")
    write(f, format("# OWNER: %s\n", szPlayerName))
    write(f, "# Index|Name|Level|Exp|Faction|Series|WeaponBranch|WeaponType|Camp|NpcId\n")

    local count = 0
    if tbXeList then
        for i = 1, getn(tbXeList) do
            local x = tbXeList[i]
            if x and x.szName then
                count = count + 1
                local line = format("%d|%s|%d|%d|%s|%d|%s|%d|%d|%d\n",
                    count,
                    x.szName or "DocCoCauBai",
                    x.level or 1,
                    x.nExp or 0,
                    x.faction or "thieulam",
                    x.series or 0,
                    x.weaponBranch or "taykhong",
                    x.nNewWeaponType or 0,
                    x.camp or 1,
                    x.nNpcId or 1908
                )
                write(f, line)
            end
        end
    end

    closefile(f)
    return count
end

function SimProgression:LoadKeoXe(szPlayerName)
    if not szPlayerName or szPlayerName == "" then return {} end
    local szPath = format("dulieu/simcity/keoxe_%s.txt", szPlayerName)
    local f = openfile(szPath, "r")
    if not f then return {} end

    local tbList = {}
    local line = read(f, "*l")
    while line do
        if line ~= "" and strsub(line, 1, 1) ~= "#" then
            local parts = {}
            local s = line
            while 1 do
                local p = strfind(s, "|")
                if p then
                    tinsert(parts, strsub(s, 1, p - 1))
                    s = strsub(s, p + 1)
                else
                    tinsert(parts, s)
                    break
                end
            end

            if getn(parts) >= 10 then
                tinsert(tbList, {
                    szName = parts[2],
                    level = tonumber(parts[3]) or 1,
                    nExp = tonumber(parts[4]) or 0,
                    faction = parts[5],
                    series = tonumber(parts[6]) or 0,
                    weaponBranch = parts[7],
                    nNewWeaponType = tonumber(parts[8]) or 0,
                    camp = tonumber(parts[9]) or 1,
                    nNpcId = tonumber(parts[10]) or 1908,
                    ownerName = szPlayerName
                })
            end
        end
        line = read(f, "*l")
    end

    closefile(f)
    return tbList
end




--========================================================
-- 6. BANG TRA CUU TAM DANH (ATTACK RADIUS IN PIXELS)
-- 32 pixels = 1 tile (o vuong)
--========================================================
SimProgression.SKILL_ATTACK_RADIUS = {
    [1] = 100,
    [2] = 320,
    [10] = 90,
    [11] = 90,
    [13] = 400,
    [14] = 90,
    [15] = 400,
    [16] = 180,
    [17] = 90,
    [18] = 400,
    [19] = 200,
    [20] = 90,
    [29] = 72,
    [30] = 90,
    [31] = 72,
    [32] = 90,
    [34] = 72,
    [35] = 90,
    [37] = 90,
    [38] = 90,
    [40] = 200,
    [41] = 90,
    [45] = 400,
    [46] = 180,
    [47] = 450,
    [49] = 180,
    [50] = 360,
    [52] = 180,
    [53] = 75,
    [54] = 400,
    [56] = 180,
    [58] = 520,
    [59] = 180,
    [63] = 180,
    [64] = 440,
    [65] = 400,
    [67] = 440,
    [68] = 400,
    [69] = 400,
    [70] = 440,
    [71] = 420,
    [72] = 440,
    [73] = 440,
    [74] = 400,
    [80] = 240,
    [82] = 570,
    [83] = 180,
    [84] = 180,
    [85] = 180,
    [86] = 180,
    [88] = 360,
    [89] = 180,
    [90] = 440,
    [91] = 400,
    [92] = 180,
    [93] = 400,
    [94] = 400,
    [99] = 360,
    [101] = 400,
    [102] = 360,
    [105] = 300,
    [106] = 400,
    [107] = 180,
    [108] = 420,
    [110] = 180,
    [111] = 72,
    [113] = 400,
    [117] = 280,
    [118] = 400,
    [119] = 240,
    [120] = 400,
    [121] = 180,
    [122] = 300,
    [123] = 400,
    [125] = 72,
    [126] = 400,
    [128] = 400,
    [129] = 400,
    [135] = 270,
    [136] = 440,
    [137] = 440,
    [138] = 400,
    [139] = 60,
    [140] = 440,
    [141] = 72,
    [142] = 60,
    [143] = 440,
    [145] = 280,
    [146] = 180,
    [147] = 60,
    [148] = 570,
    [153] = 400,
    [155] = 480,
    [158] = 400,
    [159] = 180,
    [162] = 520,
    [164] = 470,
    [165] = 400,
    [169] = 300,
    [171] = 440,
    [172] = 360,
    [173] = 440,
    [174] = 440,
    [175] = 440,
    [176] = 180,
    [177] = 440,
    [178] = 440,
    [179] = 400,
    [181] = 440,
    [182] = 470,
    [183] = 180,
    [185] = 180,
    [186] = 180,
    [187] = 180,
    [188] = 180,
    [189] = 180,
    [190] = 180,
    [191] = 180,
    [192] = 400,
    [193] = 180,
    [194] = 180,
    [195] = 180,
    [196] = 180,
    [197] = 180,
    [198] = 180,
    [199] = 180,
    [200] = 180,
    [201] = 180,
    [202] = 180,
    [203] = 180,
    [204] = 180,
    [205] = 180,
    [206] = 180,
    [207] = 180,
    [208] = 180,
    [209] = 180,
    [210] = 400,
    [211] = 180,
    [212] = 180,
    [213] = 180,
    [214] = 180,
    [216] = 75,
    [217] = 75,
    [218] = 75,
    [219] = 75,
    [220] = 75,
    [221] = 75,
    [222] = 75,
    [223] = 75,
    [224] = 75,
    [225] = 75,
    [226] = 180,
    [227] = 180,
    [228] = 180,
    [229] = 75,
    [230] = 75,
    [231] = 75,
    [232] = 75,
    [233] = 270,
    [234] = 180,
    [235] = 450,
    [236] = 360,
    [237] = 300,
    [238] = 72,
    [239] = 400,
    [240] = 320,
    [241] = 180,
    [242] = 72,
    [243] = 400,
    [244] = 400,
    [245] = 400,
    [246] = 600,
    [247] = 400,
    [248] = 400,
    [249] = 350,
    [250] = 400,
    [251] = 800,
    [255] = 400,
    [266] = 360,
    [267] = 90,
    [268] = 75,
    [271] = 90,
    [272] = 75,
    [276] = 480,
    [278] = 400,
    [280] = 180,
    [281] = 180,
    [282] = 180,
    [283] = 400,
    [284] = 300,
    [285] = 300,
    [286] = 300,
    [287] = 300,
    [288] = 300,
    [289] = 300,
    [290] = 470,
    [292] = 180,
    [301] = 400,
    [302] = 470,
    [303] = 50,
    [305] = 180,
    [306] = 180,
    [307] = 200,
    [308] = 600,
    [309] = 600,
    [310] = 600,
    [311] = 600,
    [312] = 600,
    [313] = 180,
    [314] = 180,
    [315] = 180,
    [316] = 180,
    [317] = 75,
    [318] = 90,
    [319] = 75,
    [320] = 90,
    [321] = 400,
    [322] = 90,
    [323] = 90,
    [324] = 72,
    [325] = 72,
    [326] = 75,
    [327] = 75,
    [328] = 360,
    [329] = 400,
    [331] = 400,
    [332] = 180,
    [333] = 180,
    [334] = 180,
    [335] = 180,
    [336] = 360,
    [337] = 240,
    [338] = 400,
    [339] = 360,
    [340] = 400,
    [341] = 400,
    [342] = 360,
    [343] = 50,
    [345] = 50,
    [347] = 50,
    [349] = 50,
    [351] = 50,
    [353] = 420,
    [354] = 420,
    [355] = 180,
    [356] = 440,
    [357] = 400,
    [358] = 570,
    [359] = 400,
    [361] = 60,
    [362] = 420,
    [363] = 570,
    [364] = 440,
    [365] = 470,
    [366] = 470,
    [367] = 400,
    [368] = 90,
    [369] = 480,
    [370] = 400,
    [371] = 470,
    [372] = 400,
    [373] = 470,
    [374] = 400,
    [375] = 470,
    [376] = 400,
    [377] = 400,
    [378] = 400,
    [379] = 400,
    [380] = 400,
    [381] = 400,
    [382] = 400,
    [383] = 420,
    [384] = 180,
    [385] = 360,
    [386] = 300,
    [387] = 400,
    [388] = 180,
    [389] = 570,
    [390] = 440,
    [391] = 440,
    [392] = 470,
    [393] = 440,
    [394] = 440,
    [395] = 90,
    [396] = 180,
    [397] = 180,
    [398] = 360,
    [399] = 360,
    [400] = 360,
    [404] = 75,
    [405] = 75,
    [406] = 75,
    [407] = 72,
    [408] = 72,
    [409] = 75,
    [414] = 180,
    [415] = 180,
    [416] = 200,
    [417] = 75,
    [418] = 100,
    [419] = 90,
    [420] = 90,
    [421] = 90,
    [422] = 90,
    [423] = 90,
    [424] = 470,
    [425] = 470,
    [426] = 470,
    [427] = 470,
    [428] = 470,
    [429] = 360,
    [430] = 400,
    [431] = 470,
    [432] = 400,
    [433] = 420,
    [434] = 570,
    [435] = 400,
    [436] = 470,
    [437] = 400,
    [438] = 470,
    [439] = 400,
    [445] = 90,
    [446] = 90,
    [447] = 90,
    [448] = 90,
    [449] = 90,
    [450] = 180,
    [451] = 180,
    [460] = 68,
    [461] = 68,
    [491] = 400,
    [492] = 400,
    [505] = 470,
    [506] = 470,
    [507] = 470,
    [508] = 470,
    [510] = 470,
    [534] = 90,
    [535] = 90,
    [536] = 90,
    [537] = 90,
    [538] = 90,
    [539] = 180,
    [540] = 180,
    [554] = 75,
    [555] = 75,
    [556] = 75,
    [557] = 75,
    [558] = 600,
    [559] = 600,
    [560] = 300,
    [561] = 300,
    [562] = 300,
    [563] = 350,
    [564] = 600,
    [565] = 600,
    [566] = 280,
    [567] = 280,
    [568] = 300,
    [569] = 320,
    [570] = 600,
    [571] = 600,
    [572] = 180,
    [573] = 180,
    [574] = 200,
    [575] = 200,
    [576] = 600,
    [577] = 600,
    [578] = 220,
    [579] = 240,
    [580] = 260,
    [581] = 260,
    [582] = 600,
    [583] = 600,
    [587] = 400,
    [591] = 400,
    [592] = 400,
    [593] = 400,
    [595] = 400,
    [600] = 400,
    [601] = 400,
    [602] = 400,
    [604] = 400,
    [607] = 400,
    [608] = 400,
    [609] = 400,
    [610] = 400,
    [611] = 400,
    [612] = 400,
    [613] = 400,
    [614] = 400,
    [615] = 400,
    [616] = 400,
    [617] = 400,
    [618] = 400,
    [619] = 400,
    [621] = 200,
    [624] = 440,
    [625] = 440,
    [626] = 440,
    [627] = 440,
    [628] = 440,
    [656] = 440,
    [657] = 280,
    [658] = 320,
    [659] = 260,
    [660] = 400,
    [663] = 440,
    [664] = 440,
    [665] = 440,
    [666] = 440,
    [667] = 440,
    [668] = 50,
    [669] = 50,
    [671] = 50,
    [672] = 50,
    [675] = 300,
    [676] = 300,
    [677] = 300,
    [678] = 300,
    [679] = 300,
    [680] = 470,
    [681] = 300,
    [682] = 300,
    [683] = 300,
    [684] = 300,
    [685] = 300,
    [686] = 470,
    [687] = 800,
    [688] = 300,
    [689] = 300,
    [690] = 300,
    [691] = 300,
    [692] = 300,
    [693] = 300,
    [694] = 470,
    [695] = 470,
    [696] = 300,
    [697] = 300,
    [698] = 300,
    [699] = 400,
    [700] = 400,
    [701] = 400,
    [702] = 50,
    [706] = 500,
    [712] = 180,
    [718] = 180,
    [720] = 440,
    [723] = 180,
    [736] = 500,
    [737] = 500,
    [752] = 400,
    [753] = 440,
    [754] = 440,
    [755] = 440,
    [756] = 160,
    [760] = 160,
    [763] = 60,
    [840] = 160,
    [874] = 180,
    [875] = 180,
    [876] = 180,
    [877] = 400,
    [930] = 400,
    [931] = 420,
    [932] = 160,
    [933] = 400,
    [934] = 400,
    [935] = 400,
    [936] = 400,
    [937] = 72,
    [938] = 50,
    [939] = 180,
    [940] = 180,
    [941] = 180,
    [942] = 180,
    [943] = 180,
    [944] = 180,
    [945] = 180,
    [946] = 180,
    [947] = 400,
    [948] = 400,
    [949] = 72,
    [950] = 180,
    [951] = 50,
    [964] = 180,
    [965] = 180,
    [966] = 180,
    [967] = 180,
    [968] = 400,
    [969] = 400,
    [970] = 400,
    [971] = 400,
    [972] = 180,
    [973] = 180,
    [974] = 400,
    [975] = 400,
    [979] = 180,
    [980] = 180,
    [983] = 180,
    [984] = 180,
    [985] = 448,
    [986] = 448,
    [1000] = 1000,
    [1001] = 400,
    [1002] = 800,
    [1003] = 400,
    [1004] = 180,
    [1006] = 400,
    [1007] = 400,
    [1009] = 180,
    [1013] = 800,
    [1014] = 800,
    [1015] = 800,
    [1016] = 800,
    [1017] = 1000,
    [1018] = 800,
    [1021] = 800,
    [1022] = 800,
    [1024] = 400,
    [1025] = 420,
    [1026] = 420,
    [1027] = 448,
    [1029] = 400,
    [1030] = 180,
    [1031] = 360,
    [1032] = 480,
    [1033] = 400,
    [1034] = 400,
    [1035] = 400,
    [1036] = 180,
    [1037] = 180,
    [1043] = 180,
    [1044] = 180,
    [1045] = 480,
    [1046] = 480,
    [1047] = 480,
    [1048] = 480,
    [1049] = 480,
    [1050] = 800,
    [1051] = 260,
    [1052] = 470,
    [1053] = 470,
    [1054] = 470,
    [1055] = 200,
    [1056] = 180,
    [1057] = 400,
    [1058] = 280,
    [1059] = 72,
    [1060] = 108,
    [1061] = 360,
    [1062] = 400,
    [1063] = 360,
    [1064] = 400,
    [1065] = 240,
    [1066] = 420,
    [1067] = 420,
    [1068] = 420,
    [1069] = 360,
    [1070] = 470,
    [1071] = 360,
    [1072] = 570,
    [1073] = 400,
    [1074] = 400,
    [1075] = 60,
    [1076] = 570,
    [1077] = 280,
    [1078] = 470,
    [1079] = 470,
    [1080] = 400,
    [1081] = 470,
    [1082] = 180,
    [1083] = 200,
    [1084] = 280,
    [1085] = 400,
    [1086] = 280,
    [1087] = 72,
    [1088] = 108,
    [1089] = 800,
    [1090] = 400,
    [1091] = 800,
    [1092] = 400,
    [1093] = 400,
    [1094] = 420,
    [1095] = 420,
    [1096] = 420,
    [1097] = 400,
    [1098] = 400,
    [1099] = 360,
    [1100] = 360,
    [1101] = 400,
    [1102] = 240,
    [1103] = 280,
    [1104] = 420,
    [1105] = 520,
    [1106] = 400,
    [1107] = 470,
    [1108] = 470,
    [1109] = 470,
    [1110] = 420,
    [1111] = 400,
    [1112] = 180,
    [1113] = 420,
    [1114] = 470,
    [1115] = 400,
    [1122] = 480,
    [1131] = 60,
    [1132] = 400,
    [1133] = 400,
    [1134] = 800,
    [1135] = 400,
    [1136] = 400,
    [1137] = 100,
    [1138] = 100,
    [1139] = 400,
    [1140] = 400,
    [1141] = 400,
    [1142] = 400,
    [1143] = 400,
    [1144] = 360,
    [1145] = 800,
    [1146] = 200,
    [1147] = 180,
    [1148] = 400,
    [1149] = 280,
    [1150] = 72,
    [1151] = 108,
    [1152] = 360,
    [1153] = 400,
    [1154] = 360,
    [1155] = 240,
    [1156] = 420,
    [1157] = 420,
    [1158] = 360,
    [1159] = 470,
    [1160] = 360,
    [1161] = 400,
    [1162] = 400,
    [1163] = 60,
    [1164] = 570,
    [1165] = 470,
    [1166] = 470,
    [1167] = 400,
    [1168] = 470,
    [1169] = 180,
    [1170] = 180,
    [1172] = 800,
    [1173] = 600,
    [1175] = 420,
    [1176] = 420,
    [1177] = 420,
    [1178] = 400,
    [1179] = 400,
    [1180] = 400,
    [1181] = 400,
    [1182] = 400,
    [1183] = 400,
    [1184] = 400,
    [1185] = 400,
    [1186] = 50,
    [1187] = 50,
    [1188] = 50,
    [1189] = 50,
    [1193] = 90,
    [1194] = 440,
    [1195] = 50,
    [1196] = 50,
    [1197] = 50,
    [1198] = 50,
    [1201] = 180,
    [1202] = 800,
    [1203] = 800,
    [1204] = 800,
    [1208] = 180,
    [1209] = 180,
    [1210] = 180,
    [1211] = 180,
    [1486] = 68,
    [1500] = 180,
    [1731] = 180,
}

function SimProgression:GetSkillAttackRadius(skillId)
    if not skillId then return 90 end
    return self.SKILL_ATTACK_RADIUS[skillId] or 90
end

function SimProgression:GetSkillAttackRadiusTiles(skillId)
    local px = self:GetSkillAttackRadius(skillId)
    local tiles = floor(px / 32)
    if tiles < 1 then tiles = 1 end
    return tiles
end

function SimProgression:IsMeleeSkill(skillId)
    local px = self:GetSkillAttackRadius(skillId)
    return px <= 120
end

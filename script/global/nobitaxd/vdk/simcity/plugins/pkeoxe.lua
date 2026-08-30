--========================================================
-- SIMBOT KEO XE: PARTY GRINDING & PERSISTENCE
-- Engine JX1 Linux - Pure ASCII / ANSI Encoding
--========================================================

Include("\\script\\lib\\timerlist.lua")
Include("\\script\\global\\nobitaxd\\vdk\\simcity\\components\\sim.progression.lua")

SimCityKeoXe = {
	ALLXE = {
		{ 1355, 1356, 523,  1358, 513,  1360, 1361, 1362, 511,  1364, },
		{ 566,  739,  567,  568,  741,  1366, 742,  582,  743,  1365, 740, },
		{ 744,  745,  583,  565,  563,  748,  746,  562,  1367, 1368, 747, },
		{ 1194, 1193, 1195, 1196, 1197, 1198, 1199, 1200, 1201, 1202, 1231, },
		{ 1875, 1874, 1873, },
		{ 1466, 1437, 1479, 1438, },
	},
	collections = {},
	collections_knownPoint = {},
	lastExpTick = {}
}

function createTaskSayKeoxe()
	local tbOpt = {}
	local nSettingIdx = 103
	local nActionId = 1
	tinsert(tbOpt, 1, "<dec><link=image[0,14]:#npcspr:?NPCSID="..tostring(nSettingIdx).."?ACTION="..tostring(nActionId)..">Vo Ky:<link> Nhan sinh nhu mong, gap go nhau la duyen phan.");
	return tbOpt
end

function SimCityKeoXe:taoNV(id, camp, mapID, map, nt, theosau, capHP, extraConfig)
	local name = GetName()

	local tbNpc = {
		szName = SimCityNPCInfo:generateName(),
		nNpcId = id,
		nMapId = mapID,
		camp = camp,
		walkMode = "random",
		walkVar = 2,
		noStop = 1,
		leaveFightWhenNoEnemy = 5,
		noRevive = 0,
		CHANCE_ATTACK_PLAYER = 1,
		CHANCE_ATTACK_NPC = 1,
		CHANCE_JOIN_FIGHT = 1,
		RADIUS_FIGHT_PLAYER = 15,
		RADIUS_FIGHT_NPC = 10,
		RADIUS_FIGHT_SCAN = 10,
		kind = 0,
		TIME_FIGHTING_minTs = 1800,
		TIME_FIGHTING_maxTs = 3000,
		TIME_RESTING_minTs = 0,
		TIME_RESTING_maxTs = 1,
		ngoaitrang = nt or 0,
		childrenSetup = theosau or nil,
		childrenCheckDistance = (theosau and 8) or nil,
		playerID = name,
		ownerName = name,
		capHP = capHP,
		level = (extraConfig and extraConfig.level) or 1,
		nExp = (extraConfig and extraConfig.nExp) or 0,
		role = "keoxe",
		mode = "keoxe"
	}
	if extraConfig then
		for k, v in extraConfig do
			tbNpc[k] = v
		end
	end

	local nListId = SimTheoSau:New(tbNpc)

	if not self.collections[name] then
		self.collections[name] = {}
	end

	if nListId > 0 then
		tinsert(self.collections[name], nListId)
	end

	return nListId
end

function SimCityKeoXe:nv_tudo_xe(capHP)
	local forCamp = GetCurCamp()
	local pW, pX, pY = GetWorldPos()
	local pool = SimCityNPCInfo:getPoolByCap(capHP)

	for i = 1, 10 do
		local pid = pool[random(1, getn(pool))]
		while SimCityNPCInfo:notFightingChar(pid) == 1 do
			pid = pool[random(1, getn(pool))]
		end
		self:taoNV(pid, forCamp, pW, {}, 1, {}, capHP, { level = 1, nExp = 0 })
	end
	self:SavePlayerKeoXe(GetName())
end

function SimCityKeoXe:goiAnhHungThiepNgoaiTrang()
	local tbSay = createTaskSayKeoxe()
	tinsert(tbSay, "De tu tinh anh/#SimCityKeoXe:nv_tudo_xe(1)")
	tinsert(tbSay, "Cao thu nhat luu/#SimCityKeoXe:nv_tudo_xe(2)")
	tinsert(tbSay, "Tuyen ranh cao thu/#SimCityKeoXe:nv_tudo_xe(3)")
	tinsert(tbSay, "Vo lam chi ton/#SimCityKeoXe:nv_tudo_xe(4)")
	tinsert(tbSay, "Quay lai./#SimCityKeoXe:mainMenu()")
	tinsert(tbSay, "Ket thuc doi thoai./no")
	CreateTaskSay(tbSay)
	return 1
end

function SimCityKeoXe:goiAnhHungThiep()
	local tbSay = createTaskSayKeoxe()
	tinsert(tbSay, "Mo tat ca/#SimCityKeoXe:taonhanhnhom_confirm(0)")
	for i = 1, getn(self.ALLXE) do
		tinsert(tbSay, format("Mo nhom %d/#SimCityKeoXe:taonhanhnhom_confirm(%d)", i, i))
	end
	tinsert(tbSay, "Quay lai./#SimCityKeoXe:mainMenu()")
	tinsert(tbSay, "Ket thuc doi thoai./no")
	CreateTaskSay(tbSay)
	return 1
end

function SimCityKeoXe:taonhanhnhom_confirm(mode)
	local ALLXE = self.ALLXE
	if (mode == 0) then
		for i = 1, getn(ALLXE) do
			self:tao1xe(ALLXE[i])
		end
	elseif (mode > 0 and mode <= getn(ALLXE)) then
		self:tao1xe(ALLXE[mode])
	end
	self:SavePlayerKeoXe(GetName())
end

function SimCityKeoXe:tao1xe(data)
	local forCamp = GetCurCamp()
	local pW, pX, pY = GetWorldPos()
	for i = 1, getn(data) do
		local pid = data[i]
		self:taoNV(pid, forCamp, pW, {}, 0, {}, 0, { level = 1, nExp = 0 })
	end
end

function SimCityKeoXe:ketgiaoNgauNhien()
	local phai = random(1, 10)
	local ten = SimCityNPCInfo:generateName()
	local gen = random(1, 2)
	if phai == 2 then
		gen = 1
	elseif phai == 7 or phai == 8 then
		gen = 2
	end
	self.randomName = { ten }
	SimCityKeoXe:taoBangHuu(phai, gen, 1)
	return 1
end

function SimCityKeoXe:ketgiaoPhai(phai)
	local tbSay = createTaskSayKeoxe()
	if phai == 0 then
		tinsert(tbSay, "Giang ho lang tu/#SimCityKeoXe:ketgiaoNgauNhien()")
		tinsert(tbSay, "Thien Vuong Bang/#SimCityKeoXe:ketgiaoPhai(1)")
		tinsert(tbSay, "Thieu Lam/#SimCityKeoXe:ketgiaoPhai(2)")
		tinsert(tbSay, "Vo Dang/#SimCityKeoXe:ketgiaoPhai(3)")
		tinsert(tbSay, "Con Lon/#SimCityKeoXe:ketgiaoPhai(4)")
		tinsert(tbSay, "Duong Mon/#SimCityKeoXe:ketgiaoPhai(5)")
		tinsert(tbSay, "Ngu Doc/#SimCityKeoXe:ketgiaoPhai(6)")
		tinsert(tbSay, "Nga Mi/#SimCityKeoXe:ketgiaoPhai(7)")
		tinsert(tbSay, "Thuy Yen/#SimCityKeoXe:ketgiaoPhai(8)")
		tinsert(tbSay, "Cai Bang/#SimCityKeoXe:ketgiaoPhai(9)")
		tinsert(tbSay, "Thien Nhan/#SimCityKeoXe:ketgiaoPhai(10)")
		tinsert(tbSay, "Ket thuc doi thoai./no")
	else
		self.randomName = {}
		for i = 1, 5 do
			self.randomName[i] = SimCityNPCInfo:generateName()
			local gen = random(1, 2)
			if phai == 2 then
				gen = 1
			elseif phai == 7 or phai == 8 then
				gen = 2
			end

			local gioiTinh = (gen == 2) and "Nu" or "Nam"
			local ten = self.randomName[i]
			tinsert(tbSay, format("%s (%s)/#SimCityKeoXe:taoBangHuu(%d, %d, %d)", ten, gioiTinh, phai, gen, i))
		end
		tinsert(tbSay, format("Tim them/#SimCityKeoXe:ketgiaoPhai(%d)", phai))
		tinsert(tbSay, format("Quay lai/#SimCityKeoXe:ketgiaoPhai(%d)", 0))
		tinsert(tbSay, "Ket thuc doi thoai./no")
	end

	CreateTaskSay(tbSay)
	return 1
end

function SimCityKeoXe:taoBangHuu(phai, gen, tenIndex)
	local ten = self.randomName[tenIndex]
	local forCamp = GetCurCamp()
	local pW, pX, pY = GetWorldPos()
	local name = GetName()
	local factionList = {"thienvuong", "thieulam", "vodang", "conlon", "duongmon", "ngudoc", "ngami", "thuyyen", "caibang", "thiennhan"}
	local tenPhai = factionList[phai] or "thienvuong"

	local pool = {}
	if SimCityPhai[tenPhai] then
		pool = getObjectKeys(SimCityPhai[tenPhai].knownIds)
		local id = pool[random(1, getn(pool))]
		local realGen = (gen == 1) and -1 or -2
		local _kxSeries = SimCityPhai[tenPhai].knownIds[id].series
		if _kxSeries == 0 then realGen = -1 elseif _kxSeries == 2 then realGen = -2 end
		if tenPhai == "thienvuong" or tenPhai == "thieulam" then realGen = -1 elseif tenPhai == "ngami" or tenPhai == "thuyyen" then realGen = -2 end

		self:taoNV(id, forCamp, pW, 1, 1, {}, 1, {
			szName = ten,
			nSettingsIdx = realGen,
			series = _kxSeries,
			faction = tenPhai,
			level = 1,
			nExp = 0,
			ownerName = name
		})

		-- Auto save
		self:SavePlayerKeoXe(name)
		Msg2Player(format("<color=green>[Simbot]<color> Ban da ket giao bang huu <color=yellow>%s<color> (Mon phai: %s, Cap 1)!", ten, tenPhai))
	end
end

function SimCityKeoXe:ShowDanXeInfo()
	local name = GetName()
	local tbSay = createTaskSayKeoxe()
	local count = 0

	for key, fighter in SimTheoSau.fighterList do
		if fighter and fighter.playerID == name and fighter.mode == "keoxe" then
			count = count + 1
			local reqExp = (SimProgression and SimProgression.GetExpRequired and SimProgression:GetExpRequired(fighter.level or 1)) or 100
			local line = format("[%d] %s - %s - Cap %d (EXP: %d/%d)", count, fighter.szName or "DocCoCauBai", fighter.faction or "thieulam", fighter.level or 1, fighter.nExp or 0, reqExp)
			tinsert(tbSay, line .. "/no")
		end
	end

	if count == 0 then
		tinsert(tbSay, "Hien tai ban chua co bang huu nao dang di theo./no")
		local savedList = SimProgression:LoadKeoXe(name)
		if savedList and getn(savedList) > 0 then
			tinsert(tbSay, format("Ban dang co %d bang huu da luu trong file./#SimCityKeoXe:TrieuHoiDanXeDaLuu()", getn(savedList)))
		end
	end

	tinsert(tbSay, "Quay lai./#SimCityKeoXe:mainMenu()")
	tinsert(tbSay, "Ket thuc doi thoai./no")
	CreateTaskSay(tbSay)
	return 1
end

function SimCityKeoXe:TrieuHoiDanXeDaLuu()
	local name = GetName()
	local savedList = SimProgression:LoadKeoXe(name)
	if not savedList or getn(savedList) == 0 then
		local tbSay = createTaskSayKeoxe()
		tinsert(tbSay, "Khong tim thay du lieu dan xe da luu cua ban!/#SimCityKeoXe:mainMenu()")
		tinsert(tbSay, "Ket thuc doi thoai./no")
		CreateTaskSay(tbSay)
		return 1
	end

	-- Remove current active xe
	self:RemoveAll()

	local forCamp = GetCurCamp()
	local pW, pX, pY = GetWorldPos()

	for i = 1, getn(savedList) do
		local x = savedList[i]
		self:taoNV(x.nNpcId or 1908, forCamp, pW, 1, 1, {}, 1, {
			szName = x.szName,
			level = x.level or 1,
			nExp = x.nExp or 0,
			faction = x.faction,
			series = x.series,
			weaponBranch = x.weaponBranch,
			nNewWeaponType = x.nNewWeaponType,
			ownerName = name
		})
	end

	Msg2Player(format("<color=green>[Simbot]<color> Da trieu hoi thanh cong %d bang huu tu du lieu da luu!", getn(savedList)))
	return 1
end

function SimCityKeoXe:SavePlayerKeoXe(szPlayerName)
	szPlayerName = szPlayerName or GetName()
	local tbXeList = {}
	for key, fighter in SimTheoSau.fighterList do
		if fighter and fighter.playerID == szPlayerName and fighter.mode == "keoxe" then
			tinsert(tbXeList, {
				szName = fighter.szName or "DocCoCauBai",
				level = fighter.level or 1,
				nExp = fighter.nExp or 0,
				faction = fighter.faction or "thieulam",
				series = fighter.series or 0,
				weaponBranch = fighter.weaponBranch or "taykhong",
				nNewWeaponType = fighter.nNewWeaponType or 0,
				camp = fighter.camp or 1,
				nNpcId = fighter.nNpcId or 1908,
				ownerName = szPlayerName
			})
		end
	end
	if getn(tbXeList) > 0 then
		SimProgression:SaveKeoXe(szPlayerName, tbXeList)
	end
	return getn(tbXeList)
end

function SimCityKeoXe:SaveAndRemoveAll()
	local name = GetName()
	local count = self:SavePlayerKeoXe(name)
	self:RemoveAll()
	Msg2Player(format("<color=yellow>[Simbot]<color> Da luu %d bang huu va cat vao danh sach an toan!", count))
	return 1
end

function SimCityKeoXe:ResetDanXeLevel()
	local name = GetName()
	local count = 0
	for key, fighter in SimTheoSau.fighterList do
		if fighter and fighter.playerID == name and fighter.mode == "keoxe" then
			fighter.level = 1
			fighter.nExp = 0
			if fighter.finalIndex and fighter.finalIndex > 0 then
				if SetNpcLevel then SetNpcLevel(fighter.finalIndex, 1) end
				fighter.maxHP = SimProgression:CalcMaxHP(1, fighter.faction)
				fighter.lastHP = fighter.maxHP
				if NPCINFO_SetNpcCurrentMaxLife then NPCINFO_SetNpcCurrentMaxLife(fighter.finalIndex, fighter.maxHP) end
				if NPCINFO_SetNpcCurrentLife then NPCINFO_SetNpcCurrentLife(fighter.finalIndex, fighter.maxHP) end
				SimProgression:ApplyGearByLevel(fighter, fighter.finalIndex)
			end
			SimProgression:UpdateBotSkills(fighter)
			count = count + 1
		end
	end
	self:SavePlayerKeoXe(name)
	Msg2Player(format("<color=yellow>[Simbot]<color> Da reset cap do %d bang huu ve Cap 1!", count))
	return 1
end

function SimCityKeoXe:RemoveAll()
	local name = GetName()
	if self.collections[name] then
		self.collections[name] = nil
	end
	for key, fighter in SimTheoSau.fighterList do
		if fighter and fighter.playerID == name and fighter.mode == "keoxe" then
			SimTheoSau:Remove(fighter.id)
		end
	end
end

function SimCityKeoXe:ATick()
	for name, children in self.collections do
		local parentID = SearchPlayer(name)

		if parentID > 0 then
			local pW, pX, pY = CallPlayerFunction(parentID, GetWorldPos)
			local newLoc = "" .. pW .. pY .. pX
			if not self.collections_knownPoint[name] or self.collections_knownPoint[name] ~= newLoc then
				self.collections_knownPoint[name] = newLoc
				local size = getn(children)
				local centerCharId = getCenteredCell(createFormation(size))
				local fighter = SimTheoSau:Get(children[centerCharId])
				if fighter and fighter.finalIndex then
					local nX, nY, nMapIndex = GetNpcPos(fighter.finalIndex)
					local newPath = genCoords_squareshape({ nX / 32, nY / 32 }, { pX, pY }, size)
					for i = 1, size do
						local childFighter = SimTheoSau:Get(children[i])
						if childFighter then
							childFighter.parentAppointPos = newPath[i]
						end
					end
				end
			end

			-- Tinh EXP luyen cong cung chu xe khi chien dau
			local gClock = GetCurServerTime and GetCurServerTime() or 0
			if not self.lastExpTick[name] or (gClock - self.lastExpTick[name] >= 2) then
				self.lastExpTick[name] = gClock
				local isFighting = CallPlayerFunction(parentID, GetFightState)
				if isFighting == 1 then
					local size = getn(children)
					for i = 1, size do
						local f = SimTheoSau:Get(children[i])
						if f and f.level then
							local expGain = 50 + floor((f.level or 1) * 15)
							SimProgression:AddExp(f, expGain)
						end
					end
				end
			end
		end
	end
end

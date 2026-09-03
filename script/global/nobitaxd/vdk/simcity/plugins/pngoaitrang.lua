--========================================================
-- SIMBOT NGOAI TRANG: VISUAL & APPEARANCE SYSTEM
-- Engine JX1 Linux - Pure ASCII / ANSI Encoding
--========================================================

IncludeLib("NPCINFO")
IncludeLib("SETTING")
Include("\\script\\global\\nobitaxd\\vdk\\simcity\\components\\sim.progression.lua")

SimCityNgoaiTrang = {
	ALLTRANGBI_DATA = {
		non = {},
		ao = {},
		ngua = {},
		vukhi = {},
	},

	HELM_WL = { 0, 1, 2, 6, 7, 8, 10, 11, 13, 14, 20 },
	ARMOR_WL_NAM = { 0, 2, 8, 9, 10, 11, 13, 14, 18, 19, 20, 35, 41 },
	ARMOR_WL_NU = { 0, 6, 7, 8, 9, 10, 11, 14, 18, 19, 20, 35 },
	WEAPON_WL = { 0, 1, 2, 5, 8, 11, 14, 20, 28, 30, 32 },
	HORSE_WL = { 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 19, 24 },
}

function SimCityNgoaiTrang:init()
	self.used = {}
end

function SimCityNgoaiTrang:pickHelm()
	return self.HELM_WL[random(1, getn(self.HELM_WL))]
end

function SimCityNgoaiTrang:pickWeapon()
	return self.WEAPON_WL[random(1, getn(self.WEAPON_WL))]
end

function SimCityNgoaiTrang:pickArmor(charType, faction)
	if faction == "caibang" then local _f = {17,38}; return _f[random(1, 2)] end
	if faction == "vodang" or faction == "conlon" then local _f = {5,26}; return _f[random(1, 2)] end
	local _wl = (charType == -2) and self.ARMOR_WL_NU or self.ARMOR_WL_NAM
	return _wl[random(1, getn(_wl))]
end

function SimCityNgoaiTrang:makeup(config, nNpcIndex)
	if config and SimProgression and SimProgression.ApplyGearByLevel then
		config.level = config.level or 1
		return SimProgression:ApplyGearByLevel(config, nNpcIndex)
	end
	if config.series == 0 then config.nSettingsIdx = -1 elseif config.series == 2 then config.nSettingsIdx = -2 end
	config.nSettingsIdx = config.nSettingsIdx or random(-2, -1)
	config.nNewHelmType = config.nNewHelmType or self:pickHelm()
	config.nNewArmorType = config.nNewArmorType or self:pickArmor(config.nSettingsIdx, config.faction)
	config.nNewWeaponType = config.nNewWeaponType or self:pickWeapon()
	config.nNewHorseType = config.nNewHorseType or self.HORSE_WL[random(1, getn(self.HORSE_WL))]

	ChangeNpcFeature(nNpcIndex, 0, 0, config.nSettingsIdx, config.nNewHelmType, config.nNewArmorType,
		config.nNewWeaponType,
		config.nNewHorseType)

	if SetNpcRideHorse then SetNpcRideHorse(nNpcIndex, 1) end
end

function SimCityNgoaiTrang:doRandom(charType)
	local result = {
		nSettingsIdx = charType or random(-2, -1),
		nNewHelmType = self:pickHelm(),
		nNewArmorType = self:pickArmor(charType),
		nNewWeaponType = self:pickWeapon(),
		nNewHorseType = self.HORSE_WL[random(1, getn(self.HORSE_WL))]
	}
	return result
end

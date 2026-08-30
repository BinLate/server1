Include("\\script\\global\\nobitaxd\\vdk\\simcity\\head.lua")
Include("\\script\\global\\nobitaxd\\vdk\\simcity\\components\\sim.gear.lua")

function main(nNpcIndex)
	nNpcIndex = nNpcIndex or LastNpcIndex or 0
	if not nNpcIndex or nNpcIndex <= 0 then return end
	local nListId = GetNpcParam(nNpcIndex, PARAM_LIST_ID)
	local nType = GetNpcParam(nNpcIndex, PARAM_TYPE)
	local tbNpc = nil
	if nType == 1 and SimCitizen and SimCitizen.fighterList then
		tbNpc = SimCitizen.fighterList[nListId]
	elseif nType == 2 and SimTheoSau and SimTheoSau.fighterList then
		tbNpc = SimTheoSau.fighterList[nListId]
	end

	if not tbNpc then
		Say("Ta la nhan si giang ho hanh tau bon phuong.", 0)
		return
	end

	local text = (SimGear and SimGear.GetInspectText and SimGear:GetInspectText(tbNpc)) or "Nhan si giang ho"
	Say(text, 2, "Dong y/no", "Ket thuc doi thoai/no")
end

function no()
end

function OnDeath(nNpcIndex, attackerIndex)
	local nListId = GetNpcParam(nNpcIndex, PARAM_LIST_ID)
	local nType = GetNpcParam(nNpcIndex, PARAM_TYPE)
	if nType == 1 then
		SimCitizen:OnDeath(nListId, nNpcIndex, attackerIndex)	
	elseif nType == 2 then
		SimTheoSau:OnDeath(nListId, nNpcIndex, attackerIndex)	
	end
end

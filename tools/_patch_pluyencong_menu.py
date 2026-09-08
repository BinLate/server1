# -*- coding: utf-8 -*-
"""Patch pluyencong.lua: bracket menu + Vietnamese TCVN3 (same as pthanhthi)."""
from pathlib import Path
import re

ROOT = Path(r"C:\Users\Bin.Late\Documents\aGame\Vo Lam Sim - Vo Khanh\server1")
SRC = ROOT / "script/global/nobitaxd/vdk/simcity/plugins/pluyencong.lua"
REF = ROOT / "script/global/nobitaxd/vdk/simcity/plugins/pthanhthi.lua"

# yohanes/vncharsets TVCN3_1 — byte = 128 + index
TVCN3_1 = (
    "                                        "
    "\u0103\u00e2\u00ea\u00f4\u01a1\u01b0\u0111      \u00e0\u1ea3\u00e3"
    "\u00e1\u1ea1 \u1eb1\u1eb3\u1eb5\u1eaf       \u1eb7\u1ea7\u1ea9"
    "\u1eab\u1ea5\u1ead\u00e8 \u1ebb\u1ebd\u00e9\u1eb9\u1ec1\u1ec3\u1ec5"
    "\u1ebf\u1ec7\u00ec\u1ec9   \u0129\u00ed\u1ecb\u00f2 \u1ecf\u00f5"
    "\u00f3\u1ecd\u1ed3\u1ed5\u1ed7\u1ed1\u1ed9\u1edd\u1edf\u1ee1\u1edb"
    "\u1ee3\u00f9 \u1ee7\u0169\u00fa\u1ee5\u1eeb\u1eed\u1eef\u1ee9\u1ef1"
    "\u1ef3\u1ef7\u1ef9\u00fd\u1ef5 "
)
assert len(TVCN3_1) == 128
UNI_TO_BYTE = {ch: 128 + i for i, ch in enumerate(TVCN3_1) if ch != " "}


def t(s: str) -> str:
    """Unicode -> TCVN3 bytes as latin1 str (for embedding in latin1 lua text)."""
    out = bytearray()
    for ch in s:
        if ord(ch) < 128:
            out.append(ord(ch))
        elif ch in UNI_TO_BYTE:
            out.append(UNI_TO_BYTE[ch])
        else:
            low = ch.lower()
            if low in UNI_TO_BYTE:
                out.append(UNI_TO_BYTE[low])
            else:
                raise KeyError(f"unmapped {ch!r} U+{ord(ch):04X} in {s!r}")
    return out.decode("latin1")


def main():
    raw = SRC.read_bytes()
    assert b"\r\n" in raw
    # verify ref encoding
    assert b"\xae\xb8nh" in REF.read_bytes()

    text = raw.decode("latin1")

    maps = [
        ("Giang Tan Thon (1-9)", 20, 1, 9, 8),  # ASCII ok for names without rare tones first
        ("Vinh Lac Tran (1-9)", 99, 1, 9, 8),
        ("Chu Tien Tran (1-9)", 100, 1, 9, 8),
        ("Dao Huong Thon (1-9)", 101, 1, 9, 8),
        ("Long Mon Tran (1-9)", 121, 1, 9, 8),
        ("Thach Co Tran (1-9)", 153, 1, 9, 8),
        ("Long Tuyen Thon (1-9)", 174, 1, 9, 8),
        ("Phuong Tuong (10-19)", 1, 10, 19, 8),
        ("Bien Kinh (10-19)", 37, 10, 19, 10),
        ("Lam An (10-19)", 176, 10, 19, 10),
        ("Tuong Duong (10-19)", 78, 10, 19, 8),
        ("Duong Chau (10-19)", 80, 10, 19, 8),
        ("Dai Ly (10-19)", 162, 10, 19, 8),
        ("Ba Lang Huyen (10-19)", 53, 10, 19, 8),
        ("Hem Moc Nhan (10-19)", 111, 10, 19, 10),
        ("Nhan Dang Son (10-19)", 195, 10, 19, 10),
        ("Kim Quang Dong (10-19)", 4, 10, 19, 12),
        ("Kiem Cac Tay Bac (20-29)", 3, 20, 29, 12),
        ("Kiem Cac Tay Nam (20-29)", 19, 20, 29, 12),
        ("Kiem Cac Trung Nguyen (20-29)", 43, 20, 29, 12),
        ("Tan Lang (20-29)", 7, 20, 29, 12),
        ("Vu Lang Son (20-29)", 70, 20, 29, 12),
        ("La Tieu Son (20-29)", 179, 20, 29, 12),
        ("Bach Thuy Dong (20-29)", 71, 20, 29, 10),
        ("Phuc Luu Dong (20-29)", 73, 20, 29, 10),
        ("Yen Tu Dong (30-39)", 77, 30, 39, 14),
        ("Thuc Cuong Son (30-39)", 92, 30, 39, 14),
        ("Kinh Hoang Dong (40-49)", 5, 40, 49, 14),
        ("Phuc Nguu Son Tay (40-49)", 41, 40, 49, 14),
        ("Mat That Thieu Lam (40-49)", 113, 40, 49, 12),
        ("Diem Thuong Dong tang 3 (40-49)", 173, 40, 49, 12),
        ("Vu Lang Dong (50-59)", 199, 50, 59, 16),
        ("Lam Du Quan (60-79)", 319, 60, 79, 18),
        ("Dao Hoa Nguyen (80-89)", 55, 80, 89, 16),
        ("Truong Bach Son Nam (90-120)", 321, 90, 120, 22),
        ("Mac Bac Thao Nguyen (120-150)", 341, 120, 150, 20),
        ("Sa Mac tang 1 (150-180)", 225, 150, 180, 20),
        ("Vi Son Dao (180-200)", 342, 180, 200, 20),
    ]
    # Proper Vietnamese names (lowercase tones; ASCII capitals OK)
    maps_vn = [
        "Giang Tân Thôn (1-9)",
        "Vĩnh Lạc Trấn (1-9)",
        "Chu Tiên Trấn (1-9)",
        "Đào Hương Thôn (1-9)",
        "Long Môn Trấn (1-9)",
        "Thạch Cổ Trấn (1-9)",
        "Long Tuyền Thôn (1-9)",
        "Phượng Tường (10-19)",
        "Biện Kinh (10-19)",
        "Lâm An (10-19)",
        "Tương Dương (10-19)",
        "Dương Châu (10-19)",
        "Đại Lý (10-19)",
        "Ba Lăng Huyện (10-19)",
        "Hẻm Mộc Nhân (10-19)",
        "Nhạn Đăng Sơn (10-19)",
        "Kim Quang Động (10-19)",
        "Kiếm Các Tây Bắc (20-29)",
        "Kiếm Các Tây Nam (20-29)",
        "Kiếm Các Trung Nguyên (20-29)",
        "Tần Lăng (20-29)",
        "Vũ Lăng Sơn (20-29)",
        "La Tiêu Sơn (20-29)",
        "Bạch Thủy Động (20-29)",
        "Phục Lưu Động (20-29)",
        "Yến Tử Động (30-39)",
        "Thục Cương Sơn (30-39)",
        "Kinh Hoàng Động (40-49)",
        "Phục Ngưu Sơn Tây (40-49)",
        "Mật Thất Thiếu Lâm (40-49)",
        "Điểm Thương Động tầng 3 (40-49)",
        "Vũ Lăng Động (50-59)",
        "Lâm Du Quan (60-79)",
        "Đào Hoa Nguyên (80-89)",
        "Trường Bạch Sơn Nam (90-120)",
        "Mạc Bắc Thảo Nguyên (120-150)",
        "Sa Mạc tầng 1 (150-180)",
        "Vi Sơn Đảo (180-200)",
    ]
    assert len(maps) == len(maps_vn)

    brackets = [
        ("0x", "0x - Thôn trấn tân thủ (1-9)", 1, 9),
        ("1x", "1x - Thành thị và luyện công (10-19)", 10, 19),
        ("2x", "2x - Map luyện công (20-29)", 20, 29),
        ("3x", "3x - Map luyện công (30-39)", 30, 39),
        ("4x", "4x - Map luyện công (40-49)", 40, 49),
        ("5x", "5x - Map luyện công (50-59)", 50, 59),
        ("6x", "6x-7x - Map luyện công (60-79)", 60, 79),
        ("8x", "8x - Map luyện công (80-89)", 80, 89),
        ("9x", "9x - Map luyện công (90-120)", 90, 120),
        ("120", "120-150 - Map cao cấp", 120, 150),
        ("150", "150-180 - Map cao cấp", 150, 180),
        ("180", "180-200 - Map cao cấp", 180, 200),
    ]

    map_block = ["SimCityLuyenCong.TRAIN_MAPS = {"]
    map_block.append("    -- mapId MUST exist in thanhthi.txt. Do NOT invent Map IDs.")
    map_block.append("    -- Menu groups by TRAIN_BRACKETS; spawnForBracket = ALL maps in band.")
    for i, ((_, mid, a, b, cnt), name) in enumerate(zip(maps, maps_vn), 1):
        idx = f"[{i}] " if i < 10 else f"[{i}]"
        map_block.append(
            f'    {idx} = {{ name = "{t(name)}", mapId = {mid}, minLv = {a}, maxLv = {b}, count = {cnt} }},'
        )
    map_block[-1] = map_block[-1].rstrip(",")
    map_block.append("}")

    br_block = ["SimCityLuyenCong.TRAIN_BRACKETS = {"]
    br_block.append("    -- Chon 1 hang = goi bot tren TAT CA map thuoc dang cap do")
    for i, (key, label, a, b) in enumerate(brackets, 1):
        br_block.append(
            f'    [{i}] = {{ key = "{key}", label = "{t(label)}", minLv = {a}, maxLv = {b} }},'
        )
    br_block[-1] = br_block[-1].rstrip(",")
    br_block.append("}")

    m = re.search(r"SimCityLuyenCong\.TRAIN_MAPS = \{.*?\n\}", text, re.S)
    if not m:
        raise SystemExit("TRAIN_MAPS not found")
    text = text[: m.start()] + "\n".join(map_block) + text[m.end() :]

    m2 = re.search(r"SimCityLuyenCong\.TRAIN_BRACKETS = \{.*?\n\}", text, re.S)
    if m2:
        text = text[: m2.start()] + "\n".join(br_block) + text[m2.end() :]
    else:
        m_maps = re.search(r"SimCityLuyenCong\.TRAIN_MAPS = \{.*?\n\}", text, re.S)
        text = text[: m_maps.end()] + "\n\n" + "\n".join(br_block) + text[m_maps.end() :]

    # Build menu functions (no '/' inside labels!)
    def L(s):
        return t(s)

    menu = f'''function SimCityLuyenCong:bracketStatus(minLv, maxLv)
    local activeMaps = 0
    local bots = 0
    local totalMaps = 0
    for i = 1, getn(self.TRAIN_MAPS) do
        local m = self.TRAIN_MAPS[i]
        if m.minLv == minLv and m.maxLv == maxLv then
            totalMaps = totalMaps + 1
            local state = self.mapState[m.mapId]
            if state and state.isSpawned == 1 then
                activeMaps = activeMaps + 1
                bots = bots + (state.botCount or 0)
            end
        end
    end
    return activeMaps, bots, totalMaps
end

function SimCityLuyenCong:spawnForBracket(bracketIdx)
    local br = self.TRAIN_BRACKETS[bracketIdx]
    if not br then return end
    local n = 0
    for i = 1, getn(self.TRAIN_MAPS) do
        local m = self.TRAIN_MAPS[i]
        if m.minLv == br.minLv and m.maxLv == br.maxLv then
            self:spawnForMap(i)
            n = n + 1
        end
    end
    Msg2Player(br.label .. " - {L("da goi SimBot tren ")}" .. n .. " map.")
end

function SimCityLuyenCong:hibernateBracket(bracketIdx)
    local br = self.TRAIN_BRACKETS[bracketIdx]
    if not br then return end
    local n = 0
    for i = 1, getn(self.TRAIN_MAPS) do
        local m = self.TRAIN_MAPS[i]
        if m.minLv == br.minLv and m.maxLv == br.maxLv then
            self:hibernateMap(m.mapId)
            n = n + 1
        end
    end
    Msg2Player(br.label .. " - {L("da thu hoi ")}" .. n .. " map.")
end

function SimCityLuyenCong:mainMenu()
    -- CreateTaskSay gioi han so dong: liet ke dang cap 0x..9x, khong liet ke tung map.
    -- Khong dung dau '/' trong nhan. Khong dung <color=...> tren option.
    local text = "{L("=== HE THONG LUYEN CONG SIMBOT (DYNAMIC AOI) ===")}"
    text = text .. "<enter>{L("Chon dang cap map de goi SimBot tren TAT CA map thuoc nhom do:")}"
    local tbSay = {{ text }}

    for i = 1, getn(self.TRAIN_BRACKETS) do
        local br = self.TRAIN_BRACKETS[i]
        local activeMaps, bots, totalMaps = self:bracketStatus(br.minLv, br.maxLv)
        local statusStr
        if activeMaps > 0 then
            statusStr = "[Train " .. activeMaps .. "/" .. totalMaps .. " map - " .. bots .. " bot]"
        else
            statusStr = "[Nghi " .. totalMaps .. " map]"
        end
        tinsert(tbSay, br.label .. " " .. statusStr .. "/#SimCityLuyenCong:bracketMenu(" .. i .. ")")
    end

    tinsert(tbSay, "{L("Kich hoat toan bo map luyen cong")}/#SimCityLuyenCong:spawnAllMaps()")
    tinsert(tbSay, "{L("Moi SimBot gan vao PT cua toi")}/#SimCityLuyenCong:inviteBotToMyParty()")
    tinsert(tbSay, "{L("Thu hoi - Don sach toan bo bot luyen cong")}/#SimCityLuyenCong:removeAll()")
    tinsert(tbSay, "{L("Ket thuc doi thoai")}/no")
    CreateTaskSay(tbSay)
end

function SimCityLuyenCong:bracketMenu(bracketIdx)
    local br = self.TRAIN_BRACKETS[bracketIdx]
    if not br then
        self:mainMenu()
        return
    end
    local text = br.label
    text = text .. "<enter>{L("Goi hoac thu hoi ca nhom, hoac chon tung map:")}"
    local tbSay = {{ text }}
    tinsert(tbSay, "{L(">> Goi SimBot TAT CA map nhom nay")}/#SimCityLuyenCong:spawnForBracket(" .. bracketIdx .. ")")
    tinsert(tbSay, "{L(">> Thu hoi TAT CA map nhom nay")}/#SimCityLuyenCong:hibernateBracket(" .. bracketIdx .. ")")

    for i = 1, getn(self.TRAIN_MAPS) do
        local m = self.TRAIN_MAPS[i]
        if m.minLv == br.minLv and m.maxLv == br.maxLv then
            local state = self.mapState[m.mapId]
            local statusStr
            if state and state.isSpawned == 1 then
                statusStr = "[Train - " .. (state.botCount or 0) .. " bot]"
            else
                statusStr = "[Nghi]"
            end
            tinsert(tbSay, m.name .. " " .. statusStr .. "/#SimCityLuyenCong:spawnForMap(" .. i .. ")")
        end
    end

    tinsert(tbSay, "{L("Quay lai")}/#SimCityLuyenCong:mainMenu()")
    tinsert(tbSay, "{L("Ket thuc doi thoai")}/no")
    CreateTaskSay(tbSay)
end

function SimCityLuyenCong:inviteBotToMyParty()
    local ok = 0
    if SimParty and SimParty.InviteNearestBotToPlayer and PlayerIndex then
        ok = SimParty:InviteNearestBotToPlayer(PlayerIndex, nil, 30)
    end
    if ok == 1 then
        Msg2Player("{L("Da moi SimBot gan nhat vao PT (follow).")}")
    else
        Msg2Player("{L("Khong tim thay SimBot train gan (trong 30 o).")}")
    end
end

function SimCityLuyenCong:spawnAllMaps()
    for i = 1, getn(self.TRAIN_MAPS) do
        self:spawnForMap(i)
    end
    Msg2Player("{L("Da kich hoat toan bo cac map luyen cong!")}")
end

function SimCityLuyenCong:removeAll()
    for i = 1, getn(self.TRAIN_MAPS) do
        self:hibernateMap(self.TRAIN_MAPS[i].mapId)
    end
    Msg2Player("{L("Da thu hoi va don sach toan bo bot luyen cong tren cac ban do!")}")
end
'''

    # Use Vietnamese WITH diacritics for menu strings (re-do L calls above that were ASCII)
    # Replace the ASCII stubs with proper VN by rebuilding menu cleanly:
    menu = (
        "function SimCityLuyenCong:bracketStatus(minLv, maxLv)\n"
        "    local activeMaps = 0\n"
        "    local bots = 0\n"
        "    local totalMaps = 0\n"
        "    for i = 1, getn(self.TRAIN_MAPS) do\n"
        "        local m = self.TRAIN_MAPS[i]\n"
        "        if m.minLv == minLv and m.maxLv == maxLv then\n"
        "            totalMaps = totalMaps + 1\n"
        "            local state = self.mapState[m.mapId]\n"
        "            if state and state.isSpawned == 1 then\n"
        "                activeMaps = activeMaps + 1\n"
        "                bots = bots + (state.botCount or 0)\n"
        "            end\n"
        "        end\n"
        "    end\n"
        "    return activeMaps, bots, totalMaps\n"
        "end\n"
        "\n"
        "function SimCityLuyenCong:spawnForBracket(bracketIdx)\n"
        "    local br = self.TRAIN_BRACKETS[bracketIdx]\n"
        "    if not br then return end\n"
        "    local n = 0\n"
        "    for i = 1, getn(self.TRAIN_MAPS) do\n"
        "        local m = self.TRAIN_MAPS[i]\n"
        "        if m.minLv == br.minLv and m.maxLv == br.maxLv then\n"
        "            self:spawnForMap(i)\n"
        "            n = n + 1\n"
        "        end\n"
        "    end\n"
        f'    Msg2Player(br.label .. " - {t("đã gọi SimBot trên ")}" .. n .. " map.")\n'
        "end\n"
        "\n"
        "function SimCityLuyenCong:hibernateBracket(bracketIdx)\n"
        "    local br = self.TRAIN_BRACKETS[bracketIdx]\n"
        "    if not br then return end\n"
        "    local n = 0\n"
        "    for i = 1, getn(self.TRAIN_MAPS) do\n"
        "        local m = self.TRAIN_MAPS[i]\n"
        "        if m.minLv == br.minLv and m.maxLv == br.maxLv then\n"
        "            self:hibernateMap(m.mapId)\n"
        "            n = n + 1\n"
        "        end\n"
        "    end\n"
        f'    Msg2Player(br.label .. " - {t("đã thu hồi ")}" .. n .. " map.")\n'
        "end\n"
        "\n"
        "function SimCityLuyenCong:mainMenu()\n"
        "    -- CreateTaskSay limit: list brackets, not every map row.\n"
        "    -- Never put '/' in label. No <color=...> on option rows.\n"
        f'    local text = "{t("=== Hệ thống luyện công SimBot (Dynamic AOI) ===")}"\n'
        f'    text = text .. "<enter>{t("Chọn đẳng cấp map để gọi SimBot trên tất cả map thuộc nhóm đó:")}"\n'
        "    local tbSay = { text }\n"
        "\n"
        "    for i = 1, getn(self.TRAIN_BRACKETS) do\n"
        "        local br = self.TRAIN_BRACKETS[i]\n"
        "        local activeMaps, bots, totalMaps = self:bracketStatus(br.minLv, br.maxLv)\n"
        "        local statusStr\n"
        "        if activeMaps > 0 then\n"
        '            statusStr = "[Train " .. activeMaps .. "-" .. totalMaps .. " map - " .. bots .. " bot]"\n'
        "        else\n"
        f'            statusStr = "[{t("Nghỉ")} " .. totalMaps .. " map]"\n'
        "        end\n"
        '        tinsert(tbSay, br.label .. " " .. statusStr .. "/#SimCityLuyenCong:bracketMenu(" .. i .. ")")\n'
        "    end\n"
        "\n"
        f'    tinsert(tbSay, "{t("Kích hoạt toàn bộ map luyện công")}/#SimCityLuyenCong:spawnAllMaps()")\n'
        f'    tinsert(tbSay, "{t("Mời SimBot gần vào PT của tôi")}/#SimCityLuyenCong:inviteBotToMyParty()")\n'
        f'    tinsert(tbSay, "{t("Thu hồi - Dọn sạch toàn bộ bot luyện công")}/#SimCityLuyenCong:removeAll()")\n'
        f'    tinsert(tbSay, "{t("Kết thúc đối thoại")}/no")\n'
        "    CreateTaskSay(tbSay)\n"
        "end\n"
        "\n"
        "function SimCityLuyenCong:bracketMenu(bracketIdx)\n"
        "    local br = self.TRAIN_BRACKETS[bracketIdx]\n"
        "    if not br then\n"
        "        self:mainMenu()\n"
        "        return\n"
        "    end\n"
        "    local text = br.label\n"
        f'    text = text .. "<enter>{t("Gọi hoặc thu hồi cả nhóm, hoặc chọn từng map:")}"\n'
        "    local tbSay = { text }\n"
        f'    tinsert(tbSay, "{t(">> Gọi SimBot tất cả map nhóm này")}/#SimCityLuyenCong:spawnForBracket(" .. bracketIdx .. ")")\n'
        f'    tinsert(tbSay, "{t(">> Thu hồi tất cả map nhóm này")}/#SimCityLuyenCong:hibernateBracket(" .. bracketIdx .. ")")\n'
        "\n"
        "    for i = 1, getn(self.TRAIN_MAPS) do\n"
        "        local m = self.TRAIN_MAPS[i]\n"
        "        if m.minLv == br.minLv and m.maxLv == br.maxLv then\n"
        "            local state = self.mapState[m.mapId]\n"
        "            local statusStr\n"
        "            if state and state.isSpawned == 1 then\n"
        '                statusStr = "[Train - " .. (state.botCount or 0) .. " bot]"\n'
        "            else\n"
        f'                statusStr = "[{t("Nghỉ")}]"\n'
        "            end\n"
        '            tinsert(tbSay, m.name .. " " .. statusStr .. "/#SimCityLuyenCong:spawnForMap(" .. i .. ")")\n'
        "        end\n"
        "    end\n"
        "\n"
        f'    tinsert(tbSay, "{t("Quay lại")}/#SimCityLuyenCong:mainMenu()")\n'
        f'    tinsert(tbSay, "{t("Kết thúc đối thoại")}/no")\n'
        "    CreateTaskSay(tbSay)\n"
        "end\n"
        "\n"
        "function SimCityLuyenCong:inviteBotToMyParty()\n"
        "    local ok = 0\n"
        "    if SimParty and SimParty.InviteNearestBotToPlayer and PlayerIndex then\n"
        "        ok = SimParty:InviteNearestBotToPlayer(PlayerIndex, nil, 30)\n"
        "    end\n"
        "    if ok == 1 then\n"
        f'        Msg2Player("{t("Đã mời SimBot gần nhất vào PT (follow).")}")\n'
        "    else\n"
        f'        Msg2Player("{t("Không tìm thấy SimBot train gần (trong 30 ô).")}")\n'
        "    end\n"
        "end\n"
        "\n"
        "function SimCityLuyenCong:spawnAllMaps()\n"
        "    for i = 1, getn(self.TRAIN_MAPS) do\n"
        "        self:spawnForMap(i)\n"
        "    end\n"
        f'    Msg2Player("{t("Đã kích hoạt toàn bộ các map luyện công!")}")\n'
        "end\n"
        "\n"
        "function SimCityLuyenCong:removeAll()\n"
        "    for i = 1, getn(self.TRAIN_MAPS) do\n"
        "        self:hibernateMap(self.TRAIN_MAPS[i].mapId)\n"
        "    end\n"
        f'    Msg2Player("{t("Đã thu hồi và dọn sạch toàn bộ bot luyện công trên các bản đồ!")}")\n'
        "end\n"
    )

    # Remove old mainMenu..removeAll (and any previously inserted bracket helpers before mainMenu)
    # Cut from first of bracketStatus|mainMenu to just before function no()
    m3 = re.search(
        r"(?:function SimCityLuyenCong:bracketStatus\(|function SimCityLuyenCong:mainMenu\().*?(?=\nfunction no\(\))",
        text,
        re.S,
    )
    if not m3:
        raise SystemExit("menu block not found")
    text = text[: m3.start()] + menu + text[m3.end() :]

    text = text.replace(
        "-- Engine JX1 Linux - Pure ASCII / ANSI Encoding",
        "-- Engine JX1 Linux - Vietnamese menu in TCVN3 (ABC), same as pthanhthi.lua",
    )
    # also replace if already patched differently
    text = text.replace(
        "-- Engine JX1 Linux - Vietnamese menu text in TCVN3 (ABC), same as pthanhthi.lua",
        "-- Engine JX1 Linux - Vietnamese menu in TCVN3 (ABC), same as pthanhthi.lua",
    )

    out = text.encode("latin1").replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    SRC.write_bytes(out)

    # Sanity
    assert b"TRAIN_BRACKETS" in out
    assert b"spawnForBracket" in out
    assert b"bracketMenu" in out
    assert b"\xae" in out  # đ
    # no slash inside new title (CreateTaskSay)
    # 1x maps alone can exceed limit - 1x has 10 maps + 4 actions = 14 OK
    print("OK", SRC, "bytes", len(out))


if __name__ == "__main__":
    main()

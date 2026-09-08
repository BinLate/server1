"""Tests for train map brackets + GetFactionCamp name colors."""
import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
SIM = os.path.join(ROOT, "script", "global", "nobitaxd", "vdk", "simcity")
THANK = os.path.join(ROOT, "settings", "global", "vdk", "simcity", "maps", "thanhthi.txt")


class TestFactionCampColors(unittest.TestCase):
    def test_get_faction_camp_mapping(self):
        src = open(os.path.join(SIM, "libs", "common.lua"), encoding="utf-8", errors="replace").read()
        self.assertIn("function GetFactionCamp(faction)", src)
        self.assertIn("function ApplySimBotFactionCamp(config)", src)
        # Chinh = 1, Trung = 3, Ta = 2 (npcthunghiem.lua)
        self.assertRegex(src, r'thieulam".*return 1|faction == "thieulam".*\n.*return 1')
        expect = {
            "thieulam": 1, "ngami": 1, "caibang": 1, "vodang": 1,
            "thienvuong": 3, "duongmon": 3, "thuyyen": 3, "conlon": 3,
            "ngudoc": 2, "thiennhan": 2,
        }
        # Execute via simple parse of if branches
        for fac, camp in expect.items():
            self.assertIn(f'faction == "{fac}"', src)
        self.assertIn("return 1", src)
        self.assertIn("return 3", src)
        self.assertIn("return 2", src)

    def test_core_applies_faction_camp(self):
        core = open(os.path.join(SIM, "components", "sim.core.lua"), encoding="utf-8", errors="replace").read()
        self.assertIn("ApplySimBotFactionCamp(config)", core)
        self.assertNotIn("config.camp = config.camp or random(1, 3)", core)


class TestTrainMapBrackets(unittest.TestCase):
    def test_train_maps_cover_brackets_and_real_ids(self):
        src = open(os.path.join(SIM, "plugins", "pluyencong.lua"), encoding="utf-8", errors="replace").read()
        thank = open(THANK, encoding="latin1", errors="replace").read()
        have = set()
        for line in thank.splitlines()[1:]:
            parts = line.split("\t")
            if parts and parts[0].isdigit():
                have.add(int(parts[0]))

        entries = re.findall(
            r"mapId\s*=\s*(\d+)\s*,\s*minLv\s*=\s*(\d+)\s*,\s*maxLv\s*=\s*(\d+)",
            src,
        )
        self.assertGreaterEqual(len(entries), 30)
        map_ids = []
        brackets = set()
        for mid, a, b in entries:
            mid, a, b = int(mid), int(a), int(b)
            self.assertIn(mid, have, f"mapId {mid} missing thanhthi nodes")
            self.assertLessEqual(a, b)
            map_ids.append(mid)
            if a == 1 and b == 9:
                brackets.add("0x")
            elif a == 10 and b == 19:
                brackets.add("1x")
            elif a == 20 and b == 29:
                brackets.add("2x")
            elif a == 30 and b == 39:
                brackets.add("3x")
            elif a == 40 and b == 49:
                brackets.add("4x")
            elif a == 50 and b == 59:
                brackets.add("5x")
            elif a <= 60 and b >= 79:
                brackets.add("6x7x")
            elif a == 80 and b == 89:
                brackets.add("8x")
            elif a == 90 and b >= 99:
                brackets.add("9x")
            elif a == 120:
                brackets.add("120")
            elif a == 150:
                brackets.add("150")
            elif a == 180:
                brackets.add("180")
        for need in ("0x", "1x", "2x", "3x", "4x", "5x", "8x", "9x", "120", "150", "180"):
            self.assertIn(need, brackets, f"missing bracket {need}")
        # no duplicate mapId entries (one roster per map)
        self.assertEqual(len(map_ids), len(set(map_ids)), f"duplicate mapIds: {map_ids}")

    def test_spawn_random_level_in_bracket(self):
        src = open(os.path.join(SIM, "plugins", "pluyencong.lua"), encoding="utf-8", errors="replace").read()
        self.assertIn("lv = random(m.minLv, m.maxLv)", src)
        self.assertIn("isDoSat", src)
        self.assertNotIn("local camp = (isDoSat == 1 and 5) or 0", src)

    def test_menu_uses_brackets_not_flat_map_list(self):
        raw = open(os.path.join(SIM, "plugins", "pluyencong.lua"), "rb").read()
        src = raw.decode("latin-1")
        self.assertIn("TRAIN_BRACKETS", src)
        self.assertIn("spawnForBracket", src)
        self.assertIn("bracketMenu", src)
        self.assertIn("hibernateBracket", src)
        # CreateTaskSay splits on '/': status must not use slash between counts
        self.assertNotIn('activeMaps .. "/" .. totalMaps', src)
        self.assertIn('activeMaps .. "-" .. totalMaps', src)
        # Main menu must iterate brackets, not dump every TRAIN_MAPS row
        self.assertIn("getn(self.TRAIN_BRACKETS)", src)
        self.assertIn("SimCityLuyenCong:bracketMenu", src)
        # TCVN3 đ (0xAE) present in Vietnamese labels
        self.assertIn(b"\xae", raw)

    def test_skill_level_gate(self):
        prog = open(os.path.join(SIM, "components", "sim.progression.lua"), encoding="utf-8", errors="replace").read()
        self.assertIn("if lv >= 10 then", prog)
        self.assertIn("chosenSkillId = 53", prog)
        self.assertIn("tbNpc.skill351 = 351", prog)
        self.assertIn("lv >= 90 then tinsert(debuffs, 390)", prog)


if __name__ == "__main__":
    unittest.main()

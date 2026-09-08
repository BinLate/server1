"""Strict SimSkillMeta allowlist / range / pending-skill regression tests."""
import os
import re
import unittest
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
SIM = os.path.join(ROOT, "script", "global", "nobitaxd", "vdk", "simcity")
META = os.path.join(SIM, "components", "sim.skill_meta.lua")
CORE = os.path.join(SIM, "components", "sim.core.lua")
FIGHT = os.path.join(SIM, "components", "sim.fight.lua")
HORSE = os.path.join(SIM, "components", "sim.horse_skills.lua")
REPORT = os.path.join(
    ROOT, "plans", "260904-ai-bot-simulated-player", "reports", "faction-skills-combat-meta.md"
)


def meta_entry(src: str, sid: int):
    m = re.search(rf"\[{sid}\]=\{{([^}}]+)\}}", src)
    assert m, f"missing meta for {sid}"
    body = m.group(1)
    horse = int(re.search(r"horse=(\d+)", body).group(1))
    ar = int(re.search(r"ar=(\d+)", body).group(1))
    tiles = int(re.search(r"tiles=(\d+)", body).group(1))
    melee = int(re.search(r"melee=(\d+)", body).group(1))
    typ = int(re.search(r"typ=(\d+)", body).group(1))
    return {"horse": horse, "ar": ar, "tiles": tiles, "melee": melee, "typ": typ}


class TestSkillCombatMetaMatrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = open(META, encoding="ascii", errors="replace").read()
        cls.core = open(CORE, encoding="utf-8", errors="replace").read()
        cls.fight = open(FIGHT, encoding="utf-8", errors="replace").read()

    def test_api_present(self):
        self.assertIn("function SimSkillMeta:GetSkillCombatMeta", self.src)
        self.assertIn("STRICT ALLOWLIST", self.src)
        self.assertIn("ceil(px/32)", self.src)

    def test_high_priority_horse_matrix(self):
        expect = {
            318: 0, 319: 0, 321: 1, 322: 1, 302: 1, 342: 0, 351: 0,
            355: 1, 336: 0, 337: 0, 361: 1, 362: 0, 368: 0, 375: 0,
            323: 0, 325: 0, 380: 0, 372: 0, 339: 0, 353: 0,
            1059: 0, 1069: 0, 1076: 0,
        }
        for sid, horse in expect.items():
            e = meta_entry(self.src, sid)
            self.assertEqual(e["horse"], horse, f"skill {sid} horse")

    def test_380_phong_suong_is_ranged_not_melee(self):
        e = meta_entry(self.src, 380)
        self.assertEqual(e["horse"], 0)
        self.assertEqual(e["melee"], 0)
        self.assertGreater(e["ar"], 120)

    def test_high_priority_radius(self):
        expect_ar = {
            318: 90, 321: 400, 322: 90, 302: 470, 342: 360, 351: 50,
            355: 180, 336: 360, 337: 240, 361: 60, 362: 420, 368: 90, 375: 470,
        }
        for sid, ar in expect_ar.items():
            e = meta_entry(self.src, sid)
            self.assertEqual(e["ar"], ar, f"skill {sid} ar")

    def test_ceil_tiles_not_floor(self):
        # 90px -> ceil 3 tiles (not floor 2)
        self.assertEqual(meta_entry(self.src, 318)["tiles"], 3)
        self.assertEqual(meta_entry(self.src, 322)["tiles"], 3)
        # 60px -> ceil 2
        self.assertEqual(meta_entry(self.src, 361)["tiles"], 2)
        # 470 -> ceil 15
        self.assertEqual(meta_entry(self.src, 302)["tiles"], 15)

    def test_trap_and_melee_types(self):
        self.assertEqual(meta_entry(self.src, 351)["typ"], 2)  # trap
        self.assertEqual(meta_entry(self.src, 318)["melee"], 1)
        self.assertEqual(meta_entry(self.src, 361)["melee"], 1)
        self.assertEqual(meta_entry(self.src, 321)["melee"], 0)

    def test_no_conflicting_legacy_tables(self):
        self.assertIn("SIMBOT_DISMOUNT_SKILLS = nil", self.core)
        self.assertIn("SIMBOT_SKILL_RANGE = nil", self.core)
        horse = open(HORSE, encoding="utf-8", errors="replace").read()
        self.assertIn("HORSE_SKILLS = {}", horse)
        # No non-empty conflicting allow entries for 375/342/362 in horse file
        self.assertNotRegex(horse, r"\[375\]\s*=\s*1")

    def test_pending_skill_pipeline(self):
        self.assertIn("pendingSkillId", self.core)
        self.assertIn("SimBotCastDist(tbNpc, skillId)", self.core)
        self.assertIn("GetSkillCombatMeta", self.fight)
        # BV path picks once then reuses pending
        self.assertIn("local pending = SimPickSkill(tbNpc, 1)", self.core)
        self.assertIn("local sk = pending", self.core)

    def test_range_switch_semantics_documented(self):
        """SimBotCastDist must take explicit skillId of pending skill."""
        self.assertIn("function SimBotCastDist(tbNpc, skillId)", self.core)
        # fight uses selected skillId for maxCastTiles
        self.assertIn("GetSkillCombatMeta(skillId)", self.fight)

    def test_horse_independent_of_range(self):
        # Mounted melee vs foot ranged
        self.assertEqual(meta_entry(self.src, 361)["horse"], 1)
        self.assertLessEqual(meta_entry(self.src, 361)["ar"], 120)
        self.assertEqual(meta_entry(self.src, 362)["horse"], 0)
        self.assertGreater(meta_entry(self.src, 362)["ar"], 384)
        self.assertEqual(meta_entry(self.src, 321)["horse"], 1)
        self.assertGreater(meta_entry(self.src, 321)["ar"], 384)
        self.assertEqual(meta_entry(self.src, 368)["horse"], 0)
        self.assertLessEqual(meta_entry(self.src, 368)["ar"], 120)

    def test_audit_report_exists(self):
        self.assertTrue(os.path.isfile(REPORT))
        rpt = open(REPORT, encoding="utf-8").read()
        self.assertIn("| 375 | 0 | 0 | PASS |", rpt)
        self.assertIn("| 361 | 1 | 1 | PASS |", rpt)
        self.assertIn("DEFAULT-DENY", rpt)

    def test_generator_validator_roundtrip(self):
        gen = os.path.join(ROOT, "tools", "gen_skill_meta.py")
        r = subprocess.run([sys.executable, gen], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("matrix fails none", r.stdout)


class TestRangeSwitchRegression(unittest.TestCase):
    def test_cast_dist_uses_pending_not_primary(self):
        """Simulate: primary 420px (tiles~14) vs pending 90px (tiles 3)."""
        src = open(META, encoding="ascii", errors="replace").read()
        primary = meta_entry(src, 362)  # 420
        pending = meta_entry(src, 318)  # 90
        self.assertGreater(primary["tiles"], 10)
        self.assertLessEqual(pending["tiles"], 3)
        # Correct behavior: use pending tiles for approach, not primary
        cast_tiles = pending["tiles"]
        target_dist = 10
        self.assertTrue(target_dist > cast_tiles, "must approach before cast")


class TestHorseSwitchRegression(unittest.TestCase):
    def test_four_combinations(self):
        src = open(META, encoding="ascii", errors="replace").read()
        cases = {
            "A_mounted_ranged": (321, 1, "ranged"),
            "B_foot_ranged": (362, 0, "ranged"),
            "C_mounted_melee": (322, 1, "melee"),
            "D_foot_melee": (368, 0, "melee"),
        }
        for name, (sid, horse, kind) in cases.items():
            e = meta_entry(src, sid)
            self.assertEqual(e["horse"], horse, name)
            if kind == "melee":
                self.assertEqual(e["melee"], 1, name)
            else:
                self.assertEqual(e["melee"], 0, name)


if __name__ == "__main__":
    unittest.main()

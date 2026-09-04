"""Update legacy skill-meta tests for ALLOWLIST / DEFAULT-DENY semantics."""
import os
import re
import unittest
import csv

ROOT = os.path.join(os.path.dirname(__file__), "..")
SIM = os.path.join(ROOT, "script", "global", "nobitaxd", "vdk", "simcity")
META = os.path.join(SIM, "components", "sim.skill_meta.lua")


class TestSimSkillMeta(unittest.TestCase):
    def test_meta_matches_skills_txt_radius(self):
        by_txt = {}
        with open(os.path.join(ROOT, "settings", "skills.txt"), encoding="latin1") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                try:
                    sid = int(row["SkillId"])
                    hl = int(row.get("HorseLimit") or 0)
                    ar = int(row.get("AttackRadius") or 0)
                except ValueError:
                    continue
                by_txt[sid] = (hl, ar)
        src = open(META, encoding="ascii", errors="replace").read()
        self.assertIn("function SimSkillMeta:CanCastOnHorse", src)
        self.assertIn("STRICT ALLOWLIST", src)
        self.assertIn("function SimSkillMeta:GetSkillCombatMeta", src)
        # Radius from skills.txt
        for sid in (318, 321, 302, 375, 361):
            m = re.search(rf"\[{sid}\]=\{{([^}}]+)\}}", src)
            self.assertIsNotNone(m)
            ar = int(re.search(r"ar=(\d+)", m.group(1)).group(1))
            raw = by_txt[sid][1]
            self.assertEqual(ar, raw if raw > 0 else 64)
        # Allowlist horse (not raw HL alone)
        self.assertRegex(src, r"\[321\]=\{horse=1,")
        self.assertRegex(src, r"\[318\]=\{horse=0,")
        self.assertRegex(src, r"\[375\]=\{horse=0,")
        self.assertRegex(src, r"\[302\]=\{horse=1,")
        self.assertEqual(by_txt[318][0], 1)
        self.assertEqual(by_txt[321][0], 0)
        self.assertEqual(by_txt[375][0], 1)

    def test_core_pending_skill_api(self):
        core = open(os.path.join(SIM, "components", "sim.core.lua"), encoding="utf-8", errors="replace").read()
        self.assertIn("function SimBotCastDist(tbNpc, skillId)", core)
        self.assertIn("pendingSkillId", core)
        self.assertIn("SimCommitSkillToggle", core)
        self.assertIn("SimEnsureCombatAttackable", core)
        self.assertIn("sim.skill_meta.lua", core)
        self.assertIn("SIMBOT_DISMOUNT_SKILLS = nil", core)
        self.assertIn("SIMBOT_SKILL_RANGE = nil", core)

    def test_train_dosat_pct_restored(self):
        cfg = open(os.path.join(SIM, "config.lua"), encoding="utf-8", errors="replace").read()
        self.assertIn("TRAIN_DOSAT_PCT = 8", cfg)

    def test_fight_uses_same_skill_for_range_and_cast(self):
        fight = open(os.path.join(SIM, "components", "sim.fight.lua"), encoding="utf-8", errors="replace").read()
        self.assertIn("GetSkillCombatMeta(skillId)", fight)
        self.assertIn("SimApplyHorseCombat(tbNpc, skillId)", fight)
        self.assertIn("SimCommitSkillToggle", fight)


if __name__ == "__main__":
    unittest.main()

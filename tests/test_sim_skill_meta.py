"""SimSkillMeta + pendingSkill architecture checks."""
import os
import re
import unittest
import csv

ROOT = os.path.join(os.path.dirname(__file__), "..")
SIM = os.path.join(ROOT, "script", "global", "nobitaxd", "vdk", "simcity")
META = os.path.join(SIM, "components", "sim.skill_meta.lua")


class TestSimSkillMeta(unittest.TestCase):
    def test_meta_matches_skills_txt(self):
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
        # sample horse allowlist
        self.assertIn("function SimSkillMeta:CanCastOnHorse", src)
        self.assertIn("HorseLimit: 1 = can cast on horse", src)
        # 318 is HL=1 melee
        self.assertIn("[318]={horse=1", src)
        # 302 is HL=0 -> horse=0
        self.assertIn("[302]={horse=0", src)
        self.assertEqual(by_txt[318][0], 1)
        self.assertEqual(by_txt[302][0], 0)

    def test_core_pending_skill_api(self):
        core = open(os.path.join(SIM, "components", "sim.core.lua"), encoding="utf-8", errors="replace").read()
        self.assertIn("function SimBotCastDist(tbNpc, skillId)", core)
        self.assertIn("pendingSkillId", core)
        self.assertIn("SimCommitSkillToggle", core)
        self.assertIn("SimEnsureCombatAttackable", core)
        self.assertIn("sim.skill_meta.lua", core)

    def test_train_dosat_pct_restored(self):
        cfg = open(os.path.join(SIM, "config.lua"), encoding="utf-8", errors="replace").read()
        self.assertIn("TRAIN_DOSAT_PCT = 8", cfg)

    def test_fight_uses_same_skill_for_range_and_cast(self):
        fight = open(os.path.join(SIM, "components", "sim.fight.lua"), encoding="utf-8", errors="replace").read()
        self.assertIn("SimSkillMeta:GetAttackRadiusTiles(skillId)", fight)
        self.assertIn("SimApplyHorseCombat(tbNpc, skillId)", fight)
        self.assertIn("SimCommitSkillToggle", fight)


if __name__ == "__main__":
    unittest.main()

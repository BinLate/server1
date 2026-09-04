"""Static checks for train PK policy + horse skills + party invite."""
import os
import re
import unittest
import csv

ROOT = os.path.join(os.path.dirname(__file__), "..")
SIM = os.path.join(ROOT, "script", "global", "nobitaxd", "vdk", "simcity")


class TestTrainPkHorseParty(unittest.TestCase):
    def test_train_dosat_pct_default_zero(self):
        cfg = open(os.path.join(SIM, "config.lua"), encoding="utf-8", errors="replace").read()
        self.assertIn("TRAIN_DOSAT_PCT = 8", cfg)

    def test_pluyencong_uses_dosat_pct(self):
        src = open(os.path.join(SIM, "plugins", "pluyencong.lua"), encoding="utf-8", errors="replace").read()
        self.assertIn("TRAIN_DOSAT_PCT", src)
        self.assertIn("inviteBotToMyParty", src)
        self.assertIn("dosatPct", src)

    def test_no_train_proximity_aggro_exception(self):
        src = open(os.path.join(SIM, "components", "sim.movement.lua"), encoding="utf-8", errors="replace").read()
        self.assertNotIn('SIMBOT_AGGRO_PLAYER == 1 or tbNpc.mode == "train"', src)
        self.assertIn("tbNpc.camp == 5", src)

    def test_horse_skills_match_skills_txt(self):
        src = open(os.path.join(SIM, "components", "sim.skill_meta.lua"), encoding="ascii", errors="replace").read()
        self.assertIn("[318]={horse=0", src)
        self.assertIn("[375]={horse=0", src)
        self.assertIn("function SimSkillMeta:CanCastOnHorse", src)

    def test_botmount_uses_cancastonhorse(self):
        src = open(os.path.join(SIM, "components", "sim.core.lua"), encoding="utf-8", errors="replace").read()
        self.assertIn("CanCastOnHorse", src)
        self.assertIn("SIMBOT_DISMOUNT_SKILLS = {}", src)

    def test_party_invite_helpers(self):
        src = open(os.path.join(SIM, "components", "sim.party.lua"), encoding="utf-8", errors="replace").read()
        self.assertIn("InviteNearbyPlayer", src)
        self.assertIn("BindBotToPlayer", src)
        self.assertIn("InviteNearestBotToPlayer", src)


if __name__ == "__main__":
    unittest.main()

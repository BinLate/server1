"""Static checks: train combat engage/leave matches goc restore plan."""
import os
import unittest

ROOT = os.path.join(
    os.path.dirname(__file__),
    "..",
    "script",
    "global",
    "nobitaxd",
    "vdk",
    "simcity",
    "components",
)


class TestTrainCombatEngage(unittest.TestCase):
    def _read(self, name):
        path = os.path.join(ROOT, name)
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def test_movement_case3_join_fight_fallback(self):
        src = self._read("sim.movement.lua")
        self.assertIn('JoinFight(simInstance, tbNpc, "I start a fight")', src)
        # train/outdoor must still fall through to JoinFight when CHANCE_ATTACK_NPC > 1
        self.assertIn('tbNpc.mode == "train" or outdoorOk', src)
        self.assertIn("CHANCE_ATTACK_NPC > 1", src)

    def test_movement_case2_train_no_early_leave(self):
        src = self._read("sim.movement.lua")
        self.assertIn("train/outdoor keep AI fight", src)
        idx = src.find("train/outdoor keep AI fight")
        self.assertGreater(idx, 0)
        chunk = src[idx : idx + 600]
        self.assertIn('tbNpc.mode == "train" or outdoorOk', chunk)
        self.assertIn("goc: return without LeaveFight", chunk)

    def test_fight_prefers_monster_kind(self):
        src = self._read("sim.fight.lua")
        self.assertIn("bestMonster", src)
        self.assertIn("Prefer real monsters", src)
        self.assertIn("IsNpcEnemyAround(simInstance, tbNpc)", src)

    def test_train_joinfight_uses_engine_ai_not_mode0(self):
        """Regression: AI mode 0 left bots idle next to monsters (2026-09-04)."""
        src = self._read("sim.fight.lua")
        idx = src.find('JoinFight = function(self, simInstance, tbNpc, reason)')
        self.assertGreater(idx, 0)
        # Citizen JoinFight body until next top-level method
        chunk = src[idx : idx + 3500]
        self.assertIn('tbNpc.mode == "train" or outdoorOk', chunk)
        self.assertIn("SetFightState(tbNpc, 9", chunk)
        # Must not force idle AI for train engage
        self.assertNotIn(
            "AI mode 0: Lua owns cast",
            chunk,
            "train JoinFight must not use AI mode 0 commentary/path",
        )
        # Ensure the train/outdoor branch still ends with SetFightState 9
        train_branch = chunk.find('if tbNpc.mode == "train" or outdoorOk then')
        self.assertGreater(train_branch, 0)
        after = chunk[train_branch : train_branch + 900]
        self.assertIn("SetFightState(tbNpc, 9", after)
        self.assertNotIn("SetFightState(tbNpc, 0", after)


if __name__ == "__main__":
    unittest.main()

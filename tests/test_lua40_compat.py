# -*- coding: utf-8 -*-
"""Guard tests: the live JX1 game server embeds a Kingsoft Lua 4.0 fork whose
parser is NOT equivalent to the Lua 5.x runtime used by the lupa-based tests.

Constructs that are valid Lua 5.x but fatal on the live engine:
  * ``local function``  -> "<name> expected; last token read: `function'"
  * C-style /* */ comments -> whole file fails to load
  * ``goto``            -> not a keyword construct in the 4.0 fork

These checks are regex/byte based because no Lua 5.x parser can reject them.
"""
import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIMBOT_ROOT = os.path.join(REPO, 'script', 'global', 'nobitaxd')

RE_C_COMMENT = re.compile(rb'/\*')
RE_LOCAL_FUNCTION = re.compile(rb'\blocal\s+function\b')
RE_GOTO = re.compile(rb'\bgoto\b')
RE_INCLUDE = re.compile(rb'Include\("([^"]+)"\)')
# Nested pcall(function() ... end) cannot close over outer locals on the
# Kingsoft Lua 4.0 fork ("cannot access a variable in outer scope").
RE_PCALL_CLOSURE = re.compile(rb'pcall\s*\(\s*function\s*\(')

# group_fighter timer callbacks use the Kingsoft %-pack syntax which is valid
# only on the engine; excluded from the portable Lua 5.1 parse check.
LUAPACK_SYNTAX = re.compile(rb'%[A-Za-z_][A-Za-z0-9_]*')
PARSE_EXEMPT = ('group_fighter.timer.lua', 'group_fighter.timer.child.lua')


def iter_lua_files(root):
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if name.lower().endswith('.lua'):
                yield os.path.join(dirpath, name)


def resolve_include(repo, inc):
    path = inc.replace(b'\\\\', b'\\').strip(b'\\')
    rel = path.replace(b'\\', b'/').decode('ascii', 'ignore')
    return os.path.normpath(os.path.join(repo, rel))


class TestKingsoftLua40Compat(unittest.TestCase):
    """No construct that the Kingsoft Lua 4.0 parser rejects may come back."""

    def test_no_c_style_comments(self):
        bad = []
        for path in iter_lua_files(SIMBOT_ROOT):
            with open(path, 'rb') as fh:
                data = fh.read()
            for m in RE_C_COMMENT.finditer(data):
                line = data[:m.start()].count(b'\n') + 1
                bad.append('%s:%d' % (os.path.relpath(path, SIMBOT_ROOT), line))
        self.assertEqual(bad, [], 'C-style /* */ comments break the whole file '
                                  'on the Kingsoft Lua 4.0 parser: %s' % bad)

    def test_no_local_function(self):
        bad = []
        for path in iter_lua_files(SIMBOT_ROOT):
            with open(path, 'rb') as fh:
                data = fh.read()
            for m in RE_LOCAL_FUNCTION.finditer(data):
                line = data[:m.start()].count(b'\n') + 1
                bad.append('%s:%d' % (os.path.relpath(path, SIMBOT_ROOT), line))
        self.assertEqual(bad, [], '`local function` is invalid in the Kingsoft '
                                 'Lua 4.0 fork; use a plain global function: %s' % bad)

    def test_no_goto_statement(self):
        bad = []
        for path in iter_lua_files(SIMBOT_ROOT):
            with open(path, 'rb') as fh:
                data = fh.read()
            for m in RE_GOTO.finditer(data):
                line = data[:m.start()].count(b'\n') + 1
                bad.append('%s:%d' % (os.path.relpath(path, SIMBOT_ROOT), line))
        self.assertEqual(bad, [], '`goto` does not exist in the Kingsoft Lua '
                                  '4.0 fork: %s' % bad)

    def test_no_pcall_nested_closures(self):
        """pcall(function() ... end) that closes over outer locals fails with
        'cannot access a variable in outer scope' on Kingsoft Lua 4.0 and
        aborts the whole Include (live luaerror_2026_09_04.txt)."""
        bad = []
        for path in iter_lua_files(SIMBOT_ROOT):
            with open(path, 'rb') as fh:
                data = fh.read()
            for m in RE_PCALL_CLOSURE.finditer(data):
                line = data[:m.start()].count(b'\n') + 1
                bad.append('%s:%d' % (os.path.relpath(path, SIMBOT_ROOT), line))
        self.assertEqual(bad, [], 'pcall(function()...) closures break load on '
                                  'Kingsoft Lua 4.0: %s' % bad)


class TestIncludeTargetsExist(unittest.TestCase):
    """Every Include() inside the simbot tree must resolve to a real file.

    Catches corrupted paths (e.g. single-backslash strings whose escapes
    silently mangle \\n, \\t, \\v, \\f into control characters).
    """

    def test_all_includes_resolve(self):
        missing = []
        for path in iter_lua_files(SIMBOT_ROOT):
            with open(path, 'rb') as fh:
                data = fh.read()
            for m in RE_INCLUDE.finditer(data):
                line_start = data.rfind(b'\n', 0, m.start()) + 1
                if b'--' in data[line_start:m.start()]:
                    continue  # commented-out include
                target = resolve_include(REPO, m.group(1))
                if not os.path.isfile(target):
                    missing.append('%s -> %s' % (
                        os.path.relpath(path, SIMBOT_ROOT),
                        target))
        self.assertEqual(missing, [], 'broken Include() targets: %s' % missing)


class TestSpawnPathContract(unittest.TestCase):
    """SimCore:initCharConfig builds every bot through the four Sim*Sys
    constructors; each must exist in its component file or bot creation dies
    with 'attempt to call a nil value' and no simbot ever spawns."""

    CONTRACT = {
        os.path.join('components', 'sim.movement.lua'): b'function SimMovementSys(',
        os.path.join('components', 'sim.fun.lua'): b'function SimFunSys(',
        os.path.join('components', 'sim.entity.lua'): b'function SimEntitySys(',
        os.path.join('components', 'sim.fight.lua'): b'function SimFightSys(',
    }

    def test_all_sys_constructors_defined(self):
        missing = []
        for rel, needle in self.CONTRACT.items():
            path = os.path.join(SIMBOT_ROOT, 'vdk', 'simcity', rel)
            with open(path, 'rb') as fh:
                if needle not in fh.read():
                    missing.append(rel)
        self.assertEqual(missing, [], 'missing Sim*Sys constructors: %s' % missing)


class TestPortableSyntaxParse(unittest.TestCase):
    """Parse every simbot file with Lua 5.1 (skipped when lupa lacks it).

    Lua 5.1 accepts the 4.0-era dialect (getn, for-var assignment, unknown
    string escapes) while still catching real syntax errors such as typos or
    unbalanced blocks. Files using the Kingsoft %-pack syntax are exempt.
    """

    def test_lua51_parse(self):
        try:
            from lupa import lua51
        except ImportError:
            self.skipTest('lupa.lua51 not available')
        lua = lua51.LuaRuntime(unpack_returned_tuples=True)
        bad = []
        for path in iter_lua_files(SIMBOT_ROOT):
            if os.path.basename(path) in PARSE_EXEMPT:
                continue
            with open(path, 'rb') as fh:
                src = fh.read().decode('latin-1')
            if LUAPACK_SYNTAX.search(src.encode('latin-1')):
                continue
            ok, err = lua.execute('''
                local src, name = ...
                local chunk, e = loadstring(src, name)
                if chunk then return true, nil end
                return false, e
            ''', src, '@' + path.replace('\\', '/'))
            if not ok:
                bad.append('%s: %s' % (os.path.relpath(path, SIMBOT_ROOT), err))
        self.assertEqual(bad, [], 'Lua syntax errors: %s' % bad)


if __name__ == '__main__':
    unittest.main()

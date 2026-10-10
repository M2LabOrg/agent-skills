"""Tests for the skill-authoring scripts: the scaffolder and the validator.

    python3 -m unittest discover tests
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "skill-authoring" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_skill as v  # noqa: E402

GOOD_DESCRIPTION = ("Formats SQL to the team style guide with uppercase keywords and one clause per line. "
                    "Use when the user asks to format or tidy SQL. Do not use for query optimization.")


def write_skill(root, name="sql-style", description=GOOD_DESCRIPTION, body="# SQL Style\n", evals=True, extra=""):
    d = Path(root) / name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {description}\n{extra}---\n\n{body}")
    if evals:
        (d / "evals").mkdir()
        (d / "evals" / "trigger-queries.json").write_text(json.dumps(
            [{"query": "tidy this query", "should_trigger": True},
             {"query": "why is this query slow", "should_trigger": False}]))
    return d


class Validator(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_clean_skill(self):
        errors, warnings, fm = v.check(write_skill(self.tmp.name))
        self.assertEqual((errors, warnings), ([], []))
        self.assertEqual(fm["name"], "sql-style")

    def test_name_must_match_folder_and_format(self):
        d = write_skill(self.tmp.name, name="sql-style")
        (d / "SKILL.md").write_text((d / "SKILL.md").read_text().replace("name: sql-style", "name: SQL_Style"))
        errors, _, _ = v.check(d)
        self.assertTrue(any("lowercase" in e for e in errors))
        self.assertTrue(any("match the folder" in e for e in errors))

    def test_description_limits_and_shape(self):
        errors, warnings, _ = v.check(write_skill(self.tmp.name, description="I do SQL."))
        self.assertEqual(errors, [])
        joined = " ".join(warnings)
        for expected in ("when to use", "near-miss", "third person", "very short"):
            self.assertIn(expected, joined)
        errors, _, _ = v.check(write_skill(self.tmp.name, name="long-one", description="x" * 1025))
        self.assertTrue(any("1025 characters" in e for e in errors))

    def test_links(self):
        d = write_skill(self.tmp.name, body="See [guide](references/guide.md) and [out](../outside.md).\n")
        (Path(self.tmp.name) / "outside.md").write_text("x")
        errors, warnings, _ = v.check(d)
        self.assertTrue(any("broken link 'references/guide.md'" in e for e in errors))
        self.assertTrue(any("leaves the skill folder" in w for w in warnings))

    def test_portability_and_unknown_keys(self):
        d = write_skill(self.tmp.name, body="Run ${CLAUDE_PLUGIN_ROOT}/x.sh\n", extra="author: me\n")
        _, warnings, _ = v.check(d)
        self.assertTrue(any("tool-specific" in w for w in warnings))
        self.assertTrue(any("unknown frontmatter keys ['author']" in w for w in warnings))

    def test_missing_evals_is_a_warning(self):
        errors, warnings, _ = v.check(write_skill(self.tmp.name, evals=False))
        self.assertEqual(errors, [])
        self.assertTrue(any("trigger-queries" in w for w in warnings))

    def test_folded_and_quoted_frontmatter(self):
        fm, _ = v.parse_frontmatter('---\nname: "x-y"\ndescription: >\n  one\n  two\nmetadata:\n  k: "v"\n---\n')
        self.assertEqual(fm, {"name": "x-y", "description": "one two", "metadata": {"k": "v"}})


class Scaffolder(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / "new_skill.py"), *args],
                              capture_output=True, text=True)

    def test_scaffold_then_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = self.run_script("my-skill", "--dir", tmp, "--assets")
            self.assertEqual(r.returncode, 0, r.stderr)
            d = Path(tmp) / "my-skill"
            self.assertTrue((d / "SKILL.md").is_file())
            self.assertTrue((d / "assets").is_dir())
            self.assertFalse((d / "scripts").exists())
            errors, warnings, fm = v.check(d)
            self.assertEqual(fm["name"], "my-skill")
            self.assertEqual(errors, [])  # placeholder links are not reported as broken
            self.assertTrue(any("placeholders" in w for w in warnings))
            self.assertTrue(any("template queries" in w for w in warnings))

    def test_refuses_existing_and_bad_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.run_script("ok-name", "--dir", tmp).returncode, 0)
            self.assertNotEqual(self.run_script("ok-name", "--dir", tmp).returncode, 0)
            self.assertNotEqual(self.run_script("Bad_Name", "--dir", tmp).returncode, 0)
            self.assertEqual(sorted(os.listdir(tmp)), ["ok-name"])


if __name__ == "__main__":
    unittest.main()

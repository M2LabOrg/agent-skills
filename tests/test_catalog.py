"""Checks the skill validator's leak guard and frontmatter parser.

    python3 -m unittest discover tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import catalog  # noqa: E402


def leaks(text):
    return sorted({why for pattern, why in catalog.FORBIDDEN if pattern.search(text)})


class LeakGuard(unittest.TestCase):
    def test_account_id_at_end_of_sentence(self):
        self.assertEqual(leaks("Expect account 123456789012."), ["12-digit account id"])

    def test_account_id_in_json(self):
        self.assertEqual(leaks('{"account":"123456789012"}'), ["12-digit account id"])

    def test_numbers_that_are_not_ids(self):
        self.assertEqual(leaks("p = 0.123456789012 and 1234567890123 and v1.123456789012"), [])

    def test_other_patterns(self):
        self.assertEqual(leaks("See PBI #42 on branch mdsm/fix (retrieved memory abc)"),
                         ["personal branch prefix", "private memory reference", "work-item id"])

    def test_repository_is_clean(self):
        for skill in catalog.skills():
            errors, _ = catalog.validate(skill)
            self.assertEqual(errors, [], skill.name)


class Frontmatter(unittest.TestCase):
    def test_nested_metadata(self):
        fm = catalog.parse_frontmatter("---\nname: x\ndescription: Does y.\nmetadata:\n  category: git\n---\n# X\n")
        self.assertEqual(fm, {"name": "x", "description": "Does y.", "metadata": {"category": "git"}})

    def test_missing_frontmatter(self):
        with self.assertRaises(ValueError):
            catalog.parse_frontmatter("# No frontmatter\n")


if __name__ == "__main__":
    unittest.main()

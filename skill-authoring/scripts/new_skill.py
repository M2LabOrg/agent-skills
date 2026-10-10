#!/usr/bin/env python3
"""Scaffold a new agent skill folder from the templates in ../assets/.

    python3 new_skill.py my-skill --dir .claude/skills
    python3 new_skill.py my-skill --dir skills --scripts --references --assets

Creates <dir>/<name>/SKILL.md and evals/trigger-queries.json, plus only the optional
folders you ask for. Refuses to overwrite an existing skill. Standard library only.
"""

import argparse
import re
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

FOLDER_NOTES = {
    "scripts": "# scripts/\n\nDeterministic helpers the agent runs. Delete this file once a script exists.\n",
    "references": "# references/\n\nDetail the agent reads only when SKILL.md points to it. Delete this file once a reference exists.\n",
    "assets": "# assets/\n\nTemplates and files the agent copies into the user's project. Delete this file once an asset exists.\n",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help="lowercase kebab-case, max 64 characters; becomes the folder name")
    ap.add_argument("--dir", default=".", help="parent folder for the skill (default: current directory)")
    for folder in FOLDER_NOTES:
        ap.add_argument(f"--{folder}", action="store_true", help=f"create {folder}/")
    a = ap.parse_args()

    if not NAME_RE.match(a.name) or len(a.name) > 64:
        sys.exit(f"error: '{a.name}' must be lowercase letters, digits and single hyphens (max 64)")
    root = Path(a.dir) / a.name
    if root.exists():
        sys.exit(f"error: {root} already exists")

    title = a.name.replace("-", " ").title()
    skill_md = (ASSETS / "SKILL.template.md").read_text(encoding="utf-8")
    skill_md = skill_md.replace("skill-name", a.name).replace("Skill Title", title)
    root.mkdir(parents=True)
    (root / "SKILL.md").write_text(skill_md, encoding="utf-8")
    (root / "evals").mkdir()
    (root / "evals" / "trigger-queries.json").write_text(
        (ASSETS / "trigger-queries.template.json").read_text(encoding="utf-8"), encoding="utf-8")
    created = ["SKILL.md", "evals/trigger-queries.json"]
    for folder, note in FOLDER_NOTES.items():
        if getattr(a, folder):
            (root / folder).mkdir()
            (root / folder / "PLACEHOLDER.md").write_text(note, encoding="utf-8")
            created.append(f"{folder}/")

    print(f"Created {root}/: " + ", ".join(created))
    print("Next: write the description and steps in SKILL.md, replace the eval queries, then run:")
    print(f"  python3 {Path(__file__).with_name('validate_skill.py')} {root}")


if __name__ == "__main__":
    main()

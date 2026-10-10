#!/usr/bin/env python3
"""Validate every skill and regenerate the catalog in README.md and docs/index.html.

    python3 scripts/catalog.py           # validate, then rewrite generated sections
    python3 scripts/catalog.py --check   # validate, and fail if generated sections are stale (CI)

A skill is any top-level folder containing SKILL.md. SKILL.md frontmatter is the
single source of truth for the catalog.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
DOCS = ROOT / "docs" / "index.html"
MIN_EVAL_QUERIES = 8

# The format and best-practice checks live in the skill-authoring skill, so the repository
# and anyone using that skill enforce the same rules.
sys.path.insert(0, str(ROOT / "skill-authoring" / "scripts"))
from validate_skill import check, parse_frontmatter as _parse  # noqa: E402

# Generic leak guards: personal branch prefixes, work-item ids, 12-digit cloud account ids,
# references to private assistant memory. Employer names are deliberately not listed here.
FORBIDDEN = [
    (re.compile(r"\bmdsm/"), "personal branch prefix"),
    (re.compile(r"\bPBI #\d"), "work-item id"),
    (re.compile(r"(?<![\d.])\d{12}(?!\.?\d)"), "12-digit account id"),
    (re.compile(r"retrieved memory", re.I), "private memory reference"),
    (re.compile(r"Michel's", re.I), "personal attribution inside a skill"),
]


def parse_frontmatter(text):
    return _parse(text)[0]


def skills():
    return sorted(p.parent for p in ROOT.glob("*/SKILL.md"))


def validate(skill_dir):
    """Shared checks in strict mode (warnings are errors here), plus repository rules:
    a catalog category, enough trigger evals, and the leak guard."""
    rel = skill_dir.name
    errors, warnings, fm = check(skill_dir)
    errors = [f"{rel}: {m}" for m in errors + warnings]
    if not fm:
        return errors, None

    metadata = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
    if not metadata.get("category"):
        errors.append(f"{rel}: metadata.category is required (used by the catalog)")

    evals = skill_dir / "evals" / "trigger-queries.json"
    if evals.exists():
        try:
            if len(json.loads(evals.read_text())) < MIN_EVAL_QUERIES:
                errors.append(f"{rel}: evals need at least {MIN_EVAL_QUERIES} queries")
        except ValueError:
            pass  # reported by check()

    for f in skill_dir.rglob("*"):
        if f.is_file() and f.suffix in {".md", ".py", ".sh", ".json", ".yml", ".html"}:
            content = f.read_text(errors="ignore")
            for pattern, why in FORBIDDEN:
                if pattern.search(content):
                    errors.append(f"{f.relative_to(ROOT)}: contains {why}")

    entry = {
        "name": fm.get("name", rel),
        "category": metadata.get("category", ""),
        "description": fm.get("description", ""),
        "folders": [d for d in ("scripts", "references", "assets", "evals") if (skill_dir / d).is_dir()],
    }
    return errors, entry


def short(desc):
    """First sentence of the description, for the README table and docs cards."""
    return re.split(r"(?<=\.)\s", desc, maxsplit=1)[0].rstrip(".")


def readme_table(entries):
    rows = ["| Skill | Category | What it does | Bundled |", "|---|---|---|---|"]
    for e in entries:
        bundled = ", ".join(f"`{d}/`" for d in e["folders"] if d != "evals") or "—"
        rows.append(f"| [`{e['name']}`]({e['name']}/SKILL.md) | {e['category']} | {short(e['description'])}. | {bundled} |")
    return "\n".join(rows)


def docs_json(entries):
    return json.dumps(
        [{"name": e["name"], "category": e["category"], "description": short(e["description"]) + ".",
          "folders": e["folders"]} for e in entries],
        indent=2, ensure_ascii=False)


def replace_between(text, start, end, body, sep="\n"):
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pattern.search(text):
        raise SystemExit(f"markers {start} ... {end} not found")
    return pattern.sub(lambda _: f"{start}{sep}{body}{sep}{end}", text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail if generated sections are out of date")
    a = ap.parse_args()

    all_errors, entries = [], []
    for d in skills():
        errs, entry = validate(d)
        all_errors += errs
        if entry:
            entries.append(entry)
    if all_errors:
        print("\n".join(all_errors), file=sys.stderr)
        sys.exit(1)

    badge = (f"[![Skills: {len(entries)}](https://img.shields.io/badge/skills-{len(entries)}-blue.svg)]"
             "(#skills)")
    readme = replace_between(README.read_text(), "<!-- catalog:start -->", "<!-- catalog:end -->",
                             readme_table(entries))
    readme = replace_between(readme, "<!-- skill-count:start -->", "<!-- skill-count:end -->", badge, sep="")
    targets = {
        README: readme,
        DOCS: replace_between(DOCS.read_text(), "<!-- catalog:start -->", "<!-- catalog:end -->",
                              f'<script id="skills-data" type="application/json">\n{docs_json(entries)}\n</script>'),
    }
    stale = [p for p, new in targets.items() if p.read_text() != new]
    if a.check:
        if stale:
            print("Out of date: " + ", ".join(str(p.relative_to(ROOT)) for p in stale)
                  + ". Run: python3 scripts/catalog.py", file=sys.stderr)
            sys.exit(1)
        print(f"{len(entries)} skills valid; catalog up to date")
        return
    for p in stale:
        p.write_text(targets[p])
    print(f"{len(entries)} skills valid; updated {len(stale)} file(s)")


if __name__ == "__main__":
    main()

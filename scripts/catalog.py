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

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
MAX_LINES = 500
MAX_DESCRIPTION = 1024

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
    """Minimal parser for the frontmatter this repo uses: scalar keys and one level of nesting."""
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with '---' frontmatter")
    end = text.index("\n---", 4)
    data, parent = {}, None
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        if line.startswith("  ") and parent:
            k, _, v = line.strip().partition(":")
            data[parent][k.strip()] = v.strip()
        else:
            k, _, v = line.partition(":")
            k, v = k.strip(), v.strip()
            if v:
                data[k], parent = v, None
            else:
                data[k], parent = {}, k
    return data


def skills():
    return sorted(p.parent for p in ROOT.glob("*/SKILL.md"))


def validate(skill_dir):
    errors = []
    rel = skill_dir.name
    text = (skill_dir / "SKILL.md").read_text()
    try:
        fm = parse_frontmatter(text)
    except ValueError as e:
        return [f"{rel}: {e}"], None

    name, desc = fm.get("name", ""), fm.get("description", "")
    if name != rel:
        errors.append(f"{rel}: name '{name}' must match the folder name")
    if not NAME_RE.match(name) or len(name) > 64:
        errors.append(f"{rel}: name must be lowercase letters, digits and single hyphens, max 64 chars")
    if not desc:
        errors.append(f"{rel}: description is required")
    if len(desc) > MAX_DESCRIPTION:
        errors.append(f"{rel}: description is {len(desc)} chars (max {MAX_DESCRIPTION})")
    if "Use when" not in desc:
        errors.append(f"{rel}: description should say when to use the skill ('Use when ...')")
    if "Do not use" not in desc:
        errors.append(f"{rel}: description should say when not to use the skill ('Do not use ...')")
    if not isinstance(fm.get("metadata"), dict) or not fm["metadata"].get("category"):
        errors.append(f"{rel}: metadata.category is required (used by the catalog)")

    n_lines = text.count("\n") + 1
    if n_lines > MAX_LINES:
        errors.append(f"{rel}: SKILL.md has {n_lines} lines (max {MAX_LINES}); move detail to references/")
    if (skill_dir / "README.md").exists():
        errors.append(f"{rel}: put documentation in SKILL.md or references/, not a README.md inside the skill")

    for md in [skill_dir / "SKILL.md", *skill_dir.glob("references/*.md")]:
        body = md.read_text()
        for target in LINK_RE.findall(body):
            if "://" in target or target.startswith("mailto:"):
                continue
            if not (md.parent / target).resolve().exists():
                errors.append(f"{md.relative_to(ROOT)}: broken link '{target}'")
    for f in skill_dir.rglob("*"):
        if f.is_file() and f.suffix in {".md", ".py", ".sh", ".json", ".yml", ".html", ".jsonl"}:
            content = f.read_text(errors="ignore")
            for pattern, why in FORBIDDEN:
                if f.suffix != ".jsonl" and pattern.search(content):
                    errors.append(f"{f.relative_to(ROOT)}: contains {why}")

    evals = skill_dir / "evals" / "trigger-queries.json"
    if not evals.exists():
        errors.append(f"{rel}: missing evals/trigger-queries.json")
    else:
        try:
            qs = json.loads(evals.read_text())
            labels = {q["should_trigger"] for q in qs if isinstance(q.get("query"), str) and q["query"]}
            if len(qs) < 8 or labels != {True, False}:
                errors.append(f"{rel}: evals need at least 8 queries with both should_trigger values")
        except (ValueError, KeyError, TypeError) as e:
            errors.append(f"{rel}: invalid evals/trigger-queries.json ({e})")

    entry = {
        "name": name,
        "category": fm.get("metadata", {}).get("category", "") if isinstance(fm.get("metadata"), dict) else "",
        "description": desc,
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


def replace_between(text, start, end, body):
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pattern.search(text):
        raise SystemExit(f"markers {start} ... {end} not found")
    return pattern.sub(lambda _: f"{start}\n{body}\n{end}", text)


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

    targets = {
        README: replace_between(README.read_text(), "<!-- catalog:start -->", "<!-- catalog:end -->",
                                readme_table(entries)),
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

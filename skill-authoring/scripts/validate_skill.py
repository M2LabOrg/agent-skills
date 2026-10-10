#!/usr/bin/env python3
"""Validate agent skills against the Agent Skills format and authoring best practices.

    python3 validate_skill.py path/to/skill [path/to/other-skill ...]
    python3 validate_skill.py --strict path/to/skill   # treat warnings as errors

Exit code 0 when every skill passes, 1 otherwise. Standard library only (Python 3.8+).

Errors break the format (agents may refuse or mis-load the skill).
Warnings break best practice (the skill loads, but triggers or reads worse).
"""

import argparse
import json
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
KNOWN_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
MAX_NAME, MAX_DESCRIPTION, MAX_COMPATIBILITY, MAX_LINES = 64, 1024, 500, 500
TOOL_SPECIFIC = re.compile(r"\$\{CLAUDE_[A-Z_]+\}|\$CLAUDE_[A-Z_]+")
PLACEHOLDER = re.compile(r"<(What|One|First|Next|If|Imperative|Input|A tempting|category|the situations|near-miss)[^>]*>|\bREPLACE\b")


def _unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        return v[1:-1]
    return v


def parse_frontmatter(text):
    """Parse the YAML subset skills use: scalars (plain, quoted, or folded > / literal |)
    and one level of nested mappings. Returns (data, body_start_line)."""
    if not text.startswith("---"):
        raise ValueError("SKILL.md must start with '---' YAML frontmatter")
    lines = text.splitlines()
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise ValueError("frontmatter is not closed with '---'") from None
    data, i = {}, 1
    while i < end:
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line[0] in " \t":
            raise ValueError(f"unexpected indentation on frontmatter line {i + 1}")
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"frontmatter line {i + 1} is not 'key: value'")
        key, value = key.strip(), value.strip()
        i += 1
        block = []
        while i < end and (not lines[i].strip() or lines[i][0] in " \t"):
            block.append(lines[i])
            i += 1
        if value in (">", ">-", "|", "|-"):
            parts = [b.strip() for b in block]
            data[key] = (" " if value.startswith(">") else "\n").join(p for p in parts if p)
        elif value:
            data[key] = _unquote(value)
        else:
            nested = {}
            for b in block:
                if b.strip():
                    k, _, v = b.strip().partition(":")
                    nested[k.strip()] = _unquote(v)
            data[key] = nested
    return data, end + 1


def check(skill_dir):
    """Return (errors, warnings, frontmatter) for one skill folder."""
    skill_dir = Path(skill_dir)
    errors, warnings = [], []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"{skill_dir}: no SKILL.md"], [], {}
    text = skill_md.read_text(encoding="utf-8")
    try:
        fm, _ = parse_frontmatter(text)
    except ValueError as e:
        return [f"{skill_md}: {e}"], [], {}

    name = fm.get("name", "")
    desc = fm.get("description", "")
    if not name:
        errors.append("name is required")
    else:
        if len(name) > MAX_NAME or not NAME_RE.match(name):
            errors.append(f"name '{name}' must be 1-{MAX_NAME} lowercase letters, digits and single hyphens")
        if name != skill_dir.resolve().name:
            errors.append(f"name '{name}' must match the folder name '{skill_dir.resolve().name}'")
        if re.search(r"\b(claude|anthropic)\b", name):
            warnings.append("names containing 'claude' or 'anthropic' may be rejected or read as official")
    if not desc:
        errors.append("description is required")
    else:
        if len(desc) > MAX_DESCRIPTION:
            errors.append(f"description is {len(desc)} characters (max {MAX_DESCRIPTION})")
        if not re.search(r"\b(Use|Apply) (when|whenever|for)\b", desc):
            warnings.append("description should say when to use the skill (e.g. 'Use when ...')")
        if not re.search(r"\bDo not use\b|\bDon't use\b|\bNot for\b", desc):
            warnings.append("description should name near-miss cases it is not for ('Do not use ...')")
        if re.match(r"(I|We|You)\b", desc):
            warnings.append("write the description in the third person ('Creates ...', not 'I create ...')")
        if len(desc) < 80:
            warnings.append("description is very short; agents may not know when to load it")
    if len(fm.get("compatibility", "")) > MAX_COMPATIBILITY:
        errors.append(f"compatibility is over {MAX_COMPATIBILITY} characters")
    if "metadata" in fm and not isinstance(fm["metadata"], dict):
        errors.append("metadata must be a mapping of string keys to string values")
    unknown = sorted(set(fm) - KNOWN_KEYS)
    if unknown:
        warnings.append(f"unknown frontmatter keys {unknown}; put custom fields under metadata")

    if PLACEHOLDER.search(text):
        warnings.append("SKILL.md still contains template placeholders like '<...>' or 'REPLACE'")

    n_lines = len(text.splitlines())
    if n_lines > MAX_LINES:
        warnings.append(f"SKILL.md has {n_lines} lines; keep it under {MAX_LINES} and move detail to references/")
    if (skill_dir / "README.md").exists():
        warnings.append("README.md inside a skill is not read by agents; use SKILL.md or references/")
    if TOOL_SPECIFIC.search(text):
        warnings.append("tool-specific variables (e.g. ${CLAUDE_...}) make the skill non-portable; use relative paths")

    for md in [skill_md, *sorted(skill_dir.glob("references/*.md"))]:
        for target in LINK_RE.findall(md.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("mailto:") or "<" in target:
                continue  # external, or a template placeholder (reported separately)
            resolved = (md.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"{md.relative_to(skill_dir)}: broken link '{target}'")
            elif skill_dir.resolve() not in resolved.parents and resolved != skill_dir.resolve():
                warnings.append(f"{md.relative_to(skill_dir)}: link '{target}' leaves the skill folder; "
                                "the skill will break when installed on its own")
    for ref in sorted(skill_dir.glob("references/*.md")):
        body = ref.read_text(encoding="utf-8")
        if len(body.splitlines()) > 100 and not re.search(r"^#+\s*(contents|table of contents)", body, re.I | re.M):
            warnings.append(f"{ref.relative_to(skill_dir)}: long reference without a 'Contents' section")

    evals = skill_dir / "evals" / "trigger-queries.json"
    if evals.exists():
        try:
            qs = json.loads(evals.read_text(encoding="utf-8"))
            labels = {q["should_trigger"] for q in qs}
            if labels != {True, False}:
                warnings.append("evals/trigger-queries.json should include both should_trigger true and false")
            if any(PLACEHOLDER.search(q["query"]) for q in qs):
                warnings.append("evals/trigger-queries.json still contains template queries (REPLACE ...)")
        except (ValueError, KeyError, TypeError) as e:
            errors.append(f"evals/trigger-queries.json is invalid ({e})")
    else:
        warnings.append("no evals/trigger-queries.json; add should- and should-not-trigger queries")

    return errors, warnings, fm


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("skills", nargs="+", help="skill folders (each containing SKILL.md)")
    ap.add_argument("--strict", action="store_true", help="fail on warnings too")
    a = ap.parse_args()

    failed = False
    for path in a.skills:
        errors, warnings, _ = check(path)
        status = "FAIL" if errors or (a.strict and warnings) else "ok"
        failed |= status == "FAIL"
        print(f"{status:4}  {path}")
        for e in errors:
            print(f"      error: {e}")
        for w in warnings:
            print(f"      warning: {w}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

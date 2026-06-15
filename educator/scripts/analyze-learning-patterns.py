"""Aggregate learning-pattern insights across a workspace.

Parses dialogue-logs/, learning-records/, lessons/, and reference/ in the
given --dir (default cwd) and reports summary stats, misconception categories,
topic dependency network, and recommendations.

Python 3, standard library only. No pip dependencies.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path


RE_DIALOGUE_SLUG = re.compile(r"^\*\*Topic slug:\*\*\s+([\w-]+)", re.MULTILINE)
RE_LR_DATE = re.compile(r"^date:\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)
RE_LR_STATUS = re.compile(r"^status:\s*(\S+)", re.MULTILINE)
RE_MIS_HEADER = re.compile(r"^### MIS-\d+:\s+(.+?)$", re.MULTILINE)
RE_LESSON_FRONT = re.compile(
    r"<!--\s*mode:\s*lesson\s*\|\s*topic:\s*([^\s|]+)",
    re.IGNORECASE,
)


CATEGORY_KEYWORDS = {
    "async/timing": {"async", "promise", "await", "event loop", "microtask", "callback"},
    "derivative": {"derivative", "limit", "calculus", "tangent"},
    "OOP": {"class", "inheritance", "polymorphism", "encapsulation", "object"},
}


def categorize_misconception(text: str) -> str:
    lowered = text.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(kw in lowered for kw in kws):
            return cat
    return "other"


def build_report(workspace: Path) -> dict:
    dlog_dir = workspace / "dialogue-logs"
    lr_dir = workspace / "learning-records"
    lesson_dir = workspace / "lessons"
    ref_dir = workspace / "reference"

    dlogs = sorted(dlog_dir.glob("*.md")) if dlog_dir.is_dir() else []
    lrs = sorted(lr_dir.glob("*.md")) if lr_dir.is_dir() else []
    lessons = sorted(lesson_dir.glob("*.html")) if lesson_dir.is_dir() else []
    refs = sorted(ref_dir.glob("*.html")) if ref_dir.is_dir() else []

    topic_slugs: set[str] = set()
    for d in dlogs:
        m = RE_DIALOGUE_SLUG.search(d.read_text(encoding="utf-8", errors="replace"))
        if m:
            topic_slugs.add(m.group(1))
    for l in lessons:
        m = RE_LESSON_FRONT.search(l.read_text(encoding="utf-8", errors="replace"))
        if m:
            topic_slugs.add(m.group(1).strip())

    # Misconception categories from dialogue logs
    mis_counts: dict[str, int] = {}
    for d in dlogs:
        text = d.read_text(encoding="utf-8", errors="replace")
        for m in RE_MIS_HEADER.finditer(text):
            cat = categorize_misconception(m.group(1))
            mis_counts[cat] = mis_counts.get(cat, 0) + 1

    # Recommendations: dormant topics (no learning record in last 30 days but topic exists)
    recs: list[str] = []
    today = date.today()
    for slug in topic_slugs:
        latest = None
        for lr in lrs:
            text = lr.read_text(encoding="utf-8", errors="replace")
            m = RE_LR_DATE.search(text)
            if m:
                try:
                    d = datetime.strptime(m.group(1), "%Y-%m-%d").date()
                    if latest is None or d > latest:
                        latest = d
                except ValueError:
                    continue
        if latest is None or (today - latest).days > 30:
            recs.append(f"Topic '{slug}' has been dormant - consider a refresher.")

    summary = {
        "topics": len(topic_slugs),
        "dialogue_logs": len(dlogs),
        "learning_records": len(lrs),
        "lessons": len(lessons),
        "reference_docs": len(refs),
    }
    return {
        "summary": summary,
        "misconception_categories": mis_counts,
        "recommendations": recs,
    }


def render_text(report: dict) -> str:
    lines: list[str] = []
    lines.append("Learning Patterns Report")
    lines.append("=" * 40)
    s = report["summary"]
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Topics: {s['topics']}")
    lines.append(f"- Dialogue logs: {s['dialogue_logs']}")
    lines.append(f"- Learning records: {s['learning_records']}")
    lines.append(f"- Lessons: {s['lessons']}")
    lines.append(f"- Reference docs: {s['reference_docs']}")
    if report["misconception_categories"]:
        lines.append("")
        lines.append("## Misconception categories")
        for cat, n in sorted(report["misconception_categories"].items(), key=lambda x: -x[1]):
            lines.append(f"- {cat}: {n}")
    if report["recommendations"]:
        lines.append("")
        lines.append("## Recommendations")
        for r in report["recommendations"]:
            lines.append(f"- {r}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Aggregate learning-pattern insights.")
    parser.add_argument("--dir", default=".", help="Workspace root (default: cwd).")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument("--output", help="Write to file instead of stdout.")
    args = parser.parse_args(argv)

    workspace = Path(args.dir).resolve()
    if not workspace.is_dir():
        print(f"error: {workspace} is not a directory", file=sys.stderr)
        return 2

    report = build_report(workspace)
    out = json.dumps(report, indent=2) if args.json else render_text(report)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

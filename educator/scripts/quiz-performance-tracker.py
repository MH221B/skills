"""Quiz performance analytics across a workspace.

Parses the unified quiz log format from dialogue-logs/ and lessons/ (see
DIALOGUE-LOG-FORMAT.md and the SKILL.md Quiz Formats section) and reports
per-topic and overall accuracy, trend, and readiness.

Python 3, standard library only. No pip dependencies.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


RE_QUIZ_HEADER = re.compile(r"^##+ Quiz:\s+(\d{4}-\d{2}-\d{2})\s+([\w-]+)", re.MULTILINE)
RE_QUIZ_MODE = re.compile(r"^- mode:\s*(\S+)\s*$", re.MULTILINE)
RE_QUIZ_DIFF = re.compile(r"^- difficulty:\s*(\S+)\s*$", re.MULTILINE)
RE_QUIZ_QUESTION = re.compile(r"^- question:\s*(.+?)\s*$", re.MULTILINE)
RE_QUIZ_CORRECT = re.compile(r"^- correct:\s*(yes|no|partial)\s*$", re.MULTILINE)
RE_QUIZ_NOTES = re.compile(r"^- notes:\s*(.*?)\s*$", re.MULTILINE)


def parse_quizzes(text: str) -> list[dict]:
    """Extract quiz entries from a markdown or HTML document."""
    quizzes: list[dict] = []
    for m in RE_QUIZ_HEADER.finditer(text):
        date_str, topic = m.group(1), m.group(2)
        # Inspect the ~500 chars after the header for the bullet fields
        after = text[m.end():m.end() + 500]
        mode_m = RE_QUIZ_MODE.search(after)
        diff_m = RE_QUIZ_DIFF.search(after)
        q_m = RE_QUIZ_QUESTION.search(after)
        c_m = RE_QUIZ_CORRECT.search(after)
        n_m = RE_QUIZ_NOTES.search(after)
        quizzes.append({
            "date": date_str,
            "topic": topic,
            "mode": mode_m.group(1) if mode_m else "unknown",
            "difficulty": diff_m.group(1) if diff_m else "unknown",
            "question": q_m.group(1) if q_m else "",
            "correct": c_m.group(1) if c_m else "no",
            "notes": n_m.group(1) if n_m else "",
        })
    return quizzes


def discover_quizzes(workspace: Path) -> list[dict]:
    quizzes: list[dict] = []
    dlogs = workspace / "dialogue-logs"
    if dlogs.is_dir():
        for dlog in sorted(dlogs.glob("*.md")):
            quizzes.extend(parse_quizzes(dlog.read_text(encoding="utf-8", errors="replace")))
    lessons = workspace / "lessons"
    if lessons.is_dir():
        for lesson in sorted(lessons.glob("*.html")):
            quizzes.extend(parse_quizzes(lesson.read_text(encoding="utf-8", errors="replace")))
    return quizzes


def accuracy(quizzes: list[dict]) -> float:
    if not quizzes:
        return 0.0
    score = sum({"yes": 1.0, "partial": 0.5, "no": 0.0}[q["correct"]] for q in quizzes)
    return round(score / len(quizzes), 3)


def trend(quizzes: list[dict]) -> str:
    if len(quizzes) < 4:
        return "insufficient-data"
    half = len(quizzes) // 2
    first = accuracy(quizzes[:half])
    second = accuracy(quizzes[half:])
    if second - first >= 0.1:
        return "improving"
    if first - second >= 0.1:
        return "declining"
    return "stable"


def readiness(avg: float) -> str:
    if avg >= 0.90:
        return "advanced"
    if avg >= 0.75:
        return "move-forward"
    if avg >= 0.60:
        return "more-practice"
    return "re-learning"


def build_report(quizzes: list[dict], topic_filter: str | None) -> dict:
    if topic_filter:
        quizzes = [q for q in quizzes if q["topic"] == topic_filter]

    per_topic: dict[str, dict] = {}
    for q in quizzes:
        t = per_topic.setdefault(q["topic"], {
            "total": 0, "yes": 0, "no": 0, "partial": 0, "results": []
        })
        t["total"] += 1
        t[q["correct"]] = t.get(q["correct"], 0) + 1
        t["results"].append(q)

    for slug, t in per_topic.items():
        t["average_accuracy"] = accuracy(t["results"])
        t["trend"] = trend(t["results"])
        t["readiness"] = readiness(t["average_accuracy"])

    overall = {
        "total_quizzes": len(quizzes),
        "average_accuracy": accuracy(quizzes),
        "trend": trend(quizzes),
        "readiness": readiness(accuracy(quizzes)),
    }
    return {"overall": overall, "per_topic": per_topic}


def render_text(report: dict) -> str:
    lines: list[str] = []
    o = report["overall"]
    lines.append("Quiz Performance Report")
    lines.append("=" * 40)
    lines.append("")
    lines.append("## Overall")
    lines.append(f"- Total quizzes: {o['total_quizzes']}")
    lines.append(f"- Average accuracy: {o['average_accuracy']:.2f}")
    lines.append(f"- Trend: {o['trend']}")
    lines.append(f"- Readiness: {o['readiness']}")
    lines.append("")
    if report["per_topic"]:
        lines.append("## Per topic")
        for slug, t in sorted(report["per_topic"].items()):
            lines.append(f"- {slug}")
            lines.append(f"    Total: {t['total']}, Avg: {t['average_accuracy']:.2f}, "
                         f"Trend: {t['trend']}, Readiness: {t['readiness']}")
        weak = [s for s, t in report["per_topic"].items() if t["average_accuracy"] < 0.85]
        if weak:
            lines.append("")
            lines.append("## Weak topics (<0.85)")
            for s in weak:
                lines.append(f"- {s} ({report['per_topic'][s]['average_accuracy']:.2f})")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Quiz performance analytics.")
    parser.add_argument("--dir", default=".", help="Workspace root (default: cwd).")
    parser.add_argument("--topic", help="Filter to a single topic slug.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument("--output", help="Write to file instead of stdout.")
    args = parser.parse_args(argv)

    workspace = Path(args.dir).resolve()
    if not workspace.is_dir():
        print(f"error: {workspace} is not a directory", file=sys.stderr)
        return 2

    quizzes = discover_quizzes(workspace)
    report = build_report(quizzes, args.topic)

    if args.json:
        out = json.dumps(report, indent=2)
    else:
        out = render_text(report)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

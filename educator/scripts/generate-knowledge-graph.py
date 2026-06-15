"""Generate tutoring-state/knowledge-graph.md from a workspace.

Parses MISSION.md, RESOURCES.md, GLOSSARY.md, dialogue-logs/, learning-records/,
lessons/, and reference/ in the given --dir (default cwd) and writes a
tutoring-state/knowledge-graph.md with Topic Index, Dependency Map, and
Mastery Gaps sections.

Python 3, standard library only. No pip dependencies.
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from datetime import date, datetime
from pathlib import Path


# --- Parsing helpers ---------------------------------------------------------

RE_LESSON_FRONT = re.compile(
    r"<!--\s*mode:\s*lesson\s*\|\s*topic:\s*([^\s|]+)",
    re.IGNORECASE,
)
RE_QUIZ_HEADER = re.compile(r"^##+ Quiz:\s+(\d{4}-\d{2}-\d{2})\s+([\w-]+)", re.MULTILINE)
RE_QUIZ_CORRECT = re.compile(r"^- correct:\s*(yes|no|partial)\s*$", re.MULTILINE)
RE_DIALOGUE_TOPIC = re.compile(r"^# Dialogue Log:\s+(.+?)$", re.MULTILINE)
RE_DIALOGUE_SLUG = re.compile(r"^\*\*Topic slug:\*\*\s+([\w-]+)\s*$", re.MULTILINE)
RE_DIALOGUE_LAST_UPDATED = re.compile(r"^\*\*Last updated:\*\*\s+(\d{4}-\d{2}-\d{2})", re.MULTILINE)
RE_DIALOGUE_SESSIONS = re.compile(r"^\*\*Sessions:\*\*\s+(\d+)", re.MULTILINE)
RE_RELATED_PREREQ = re.compile(r"Prerequisite for:.*?\[([^\]]*)\]")
RE_RELATED_DEPENDS = re.compile(r"Depends on:.*?\[([^\]]*)\]")


# --- Data types --------------------------------------------------------------

class Topic:
    def __init__(self, slug: str, title: str = ""):
        self.slug = slug
        self.title = title or slug
        self.modes: set[str] = set()
        self.sessions: int = 0
        self.last_session: str | None = None
        # quiz_results holds True for 'yes', False for 'no', None for 'partial'.
        self.quiz_results: list[bool | None] = []
        self.depends_on: set[str] = set()
        self.prerequisite_for: set[str] = set()


# --- Quiz recording ----------------------------------------------------------

def _record_quizzes_in_text(topic: Topic, text: str) -> None:
    """Scan `text` for quiz headers and append results to topic.quiz_results."""
    for qm in RE_QUIZ_HEADER.finditer(text):
        # Look at the next ~500 chars for the `correct:` line belonging to this quiz.
        window = text[qm.end():qm.end() + 500]
        cm = RE_QUIZ_CORRECT.search(window)
        if not cm:
            continue
        val = cm.group(1)
        if val == "yes":
            topic.quiz_results.append(True)
        elif val == "no":
            topic.quiz_results.append(False)
        else:
            topic.quiz_results.append(None)


# --- Discovery ---------------------------------------------------------------

def discover_topics(workspace: Path) -> dict[str, Topic]:
    topics: dict[str, Topic] = {}

    # Lessons: HTML with <!-- mode: lesson | topic: <slug> --> frontmatter.
    lessons_dir = workspace / "lessons"
    if lessons_dir.is_dir():
        for lesson in sorted(lessons_dir.glob("*.html")):
            text = lesson.read_text(encoding="utf-8", errors="replace")
            m = RE_LESSON_FRONT.search(text)
            if not m:
                continue
            slug = m.group(1).strip()
            topic = topics.setdefault(slug, Topic(slug))
            topic.modes.add("lesson")
            _record_quizzes_in_text(topic, text)

    # Dialogue logs: markdown with **Topic slug:** and quiz history.
    dlogs_dir = workspace / "dialogue-logs"
    if dlogs_dir.is_dir():
        for dlog in sorted(dlogs_dir.glob("*.md")):
            text = dlog.read_text(encoding="utf-8", errors="replace")
            slug_m = RE_DIALOGUE_SLUG.search(text)
            if not slug_m:
                continue
            slug = slug_m.group(1).strip()
            title_m = RE_DIALOGUE_TOPIC.search(text)
            topic = topics.setdefault(slug, Topic(slug, title_m.group(1).strip() if title_m else slug))
            topic.modes.add("dialogue")

            last_m = RE_DIALOGUE_LAST_UPDATED.search(text)
            if last_m:
                topic.last_session = last_m.group(1)
            sess_m = RE_DIALOGUE_SESSIONS.search(text)
            if sess_m:
                topic.sessions = int(sess_m.group(1))

            _record_quizzes_in_text(topic, text)

            for m in RE_RELATED_DEPENDS.finditer(text):
                for dep in re.findall(r"[\w-]+", m.group(1)):
                    topic.depends_on.add(dep)
                    topics.setdefault(dep, Topic(dep)).prerequisite_for.add(slug)
            for m in RE_RELATED_PREREQ.finditer(text):
                for pre in re.findall(r"[\w-]+", m.group(1)):
                    topic.prerequisite_for.add(pre)
                    topics.setdefault(pre, Topic(pre)).depends_on.add(slug)

    return topics


# --- Mastery formula ---------------------------------------------------------

def mastery_score(topic: Topic, today: date) -> float:
    if not topic.quiz_results:
        return 0.0
    correct = sum(1 for r in topic.quiz_results if r is True)
    partial = sum(1 for r in topic.quiz_results if r is None)
    accuracy = (correct + 0.5 * partial) / len(topic.quiz_results)

    sessions = max(topic.sessions, 1)
    session_stability = min(1.0, 0.6 + 0.1 * min(sessions, 4))
    decay_rate = max(0.3, 1 - 0.015 / math.log(sessions + 2))

    days_since = 0
    if topic.last_session:
        try:
            last_d = datetime.strptime(topic.last_session, "%Y-%m-%d").date()
            days_since = max(0, (today - last_d).days)
        except ValueError:
            days_since = 0
    time_decay = max(0.5, 1 - decay_rate * days_since / 30)

    return round(accuracy * time_decay * session_stability, 3)


def dominant_mode(topic: Topic) -> str:
    has_d = "dialogue" in topic.modes
    has_l = "lesson" in topic.modes
    if has_d and has_l:
        return "mixed"
    if has_d:
        return "dialogue"
    if has_l:
        return "lesson"
    return "unknown"


# --- Rendering ---------------------------------------------------------------

def render_graph(workspace: Path, topics: dict[str, Topic], today: date) -> str:
    lines: list[str] = []
    lines.append("# Knowledge Graph")
    lines.append("")
    lines.append(f"**Generated:** {today.isoformat()}")
    lines.append(f"**Workspace:** {workspace}")
    lines.append("")
    lines.append("## Topic Index")
    lines.append("")
    lines.append("| Topic | Mode | Sessions | Mastery | Last session |")
    lines.append("|---|---|---|---|---|")
    for slug in sorted(topics):
        t = topics[slug]
        lines.append(
            f"| {t.title} | {dominant_mode(t)} | {t.sessions} | "
            f"{mastery_score(t, today):.3f} | {t.last_session or '-'} |"
        )
    lines.append("")

    lines.append("## Dependency Map")
    lines.append("")
    if any(topics[s].depends_on or topics[s].prerequisite_for for s in topics):
        for slug in sorted(topics):
            t = topics[slug]
            if t.depends_on:
                lines.append(f"- **{t.title}** depends on: {', '.join(sorted(t.depends_on))}")
            if t.prerequisite_for:
                lines.append(
                    f"- **{t.title}** is prerequisite for: "
                    f"{', '.join(sorted(t.prerequisite_for))}"
                )
    else:
        lines.append("_No dependencies recorded._")
    lines.append("")

    lines.append("## Mastery Gaps")
    lines.append("")
    gaps = [
        (slug, mastery_score(t, today))
        for slug, t in topics.items()
        if mastery_score(t, today) < 0.8
    ]
    if gaps:
        for slug, score in sorted(gaps, key=lambda x: x[1]):
            lines.append(f"- {topics[slug].title} - mastery {score:.3f}")
    else:
        lines.append("_No mastery gaps below 0.800._")
    lines.append("")
    return "\n".join(lines)


# --- Main --------------------------------------------------------------------

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Generate tutoring-state/knowledge-graph.md from a workspace."
    )
    parser.add_argument("--dir", default=".", help="Workspace root (default: cwd).")
    args = parser.parse_args(argv)

    workspace = Path(args.dir).resolve()
    if not workspace.is_dir():
        print(f"error: {workspace} is not a directory", file=sys.stderr)
        return 2

    topics = discover_topics(workspace)
    out_dir = workspace / "tutoring-state"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "knowledge-graph.md"
    out_path.write_text(render_graph(workspace, topics, date.today()), encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""
Generate the knowledge graph index from all topic state files.

Parses tutoring-state/*.md files and writes tutoring-state/knowledge-graph.md
with mastery scores (quiz accuracy × time decay × session stability), dependency
maps, and mastery gaps.

Mastery formula:
  mastery = quiz_accuracy × time_decay × session_stability_factor

  session_stability_factor:
    min(1.0, 0.6 + 0.1 × min(sessions, 4))
    → 1 session=0.7, 2=0.8, 3=0.9, 4+=1.0

  time_decay:
    decay_rate = max(0.3, 1 - (0.015 / log(sessions + 2)))
    time_decay  = max(0.5, 1 - (decay_rate × days_since / 30))
    → more sessions = slower decay, floor at 0.5

Usage:
  python generate-knowledge-graph.py
  python generate-knowledge-graph.py --dir ./tutoring-state
  python generate-knowledge-graph.py --dir ./tutoring-state --output ./tutoring-state/knowledge-graph.md
"""

import os
import re
import sys
import math
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _extract_field(content: str, field_name: str) -> Optional[str]:
    pattern = rf"\*\*{re.escape(field_name)}:\*\*\s+(.+?)(?:\n|$)"
    match = re.search(pattern, content)
    return match.group(1).strip() if match else None


def _extract_section(content: str, section_name: str) -> Optional[str]:
    pattern = rf"## {re.escape(section_name)}(.+?)(?=\n##|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1) if match else None


def _parse_date(date_str: str) -> Optional[datetime]:
    """Try common date formats found in state files."""
    for fmt in ("%Y-%m-%d %H:%M UTC", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _days_since(dt: datetime) -> float:
    now = datetime.now(timezone.utc)
    return max(0.0, (now - dt).total_seconds() / 86400)


# ---------------------------------------------------------------------------
# Per-file extraction
# ---------------------------------------------------------------------------

def extract_mode(content: str) -> str:
    mode = _extract_field(content, "Mode")
    return mode if mode in ("Coding", "General") else "Unknown"


def extract_last_session_date(content: str) -> Optional[datetime]:
    """
    Pull the most recent session date from the Progress Over Time section.
    Falls back to Last Updated header field.
    """
    section = _extract_section(content, "Progress Over Time")
    if section:
        dates = re.findall(r"\*\*Session \d+\s*\((\d{4}-\d{2}-\d{2})\)\*\*", section)
        if dates:
            parsed = [_parse_date(d) for d in dates]
            parsed = [d for d in parsed if d]
            if parsed:
                return max(parsed)

    # Fallback: Last Updated header
    last_updated = _extract_field(content, "Last Updated")
    if last_updated:
        return _parse_date(last_updated)

    return None


def extract_session_count(content: str) -> int:
    """Count session entries in Progress Over Time section."""
    section = _extract_section(content, "Progress Over Time")
    if not section:
        return 0
    return len(re.findall(r"\*\*Session \d+", section))


def extract_latest_quiz_accuracy(content: str) -> Optional[float]:
    """Return accuracy % of the most recent quiz entry."""
    section = _extract_section(content, "Quiz Performance Tracking")
    if not section:
        return None

    # Match entries like: **Quiz N (YYYY-MM-DD):** ... Accuracy: X% ...
    entries = re.findall(
        r"\*\*Quiz \d+\s*\((.+?)\):\*\*(.+?)(?=\n-\s+\*\*Quiz|\Z)",
        section,
        re.DOTALL,
    )
    if not entries:
        return None

    # Parse dates to find the most recent
    dated: List[Tuple[datetime, float]] = []
    for date_str, details in entries:
        dt = _parse_date(date_str)
        acc_match = re.search(r"Accuracy:\s*(\d+)%", details)
        if dt and acc_match:
            dated.append((dt, float(acc_match.group(1))))

    if not dated:
        return None

    dated.sort(key=lambda x: x[0])
    return dated[-1][1]


def extract_related_topics(content: str) -> Dict[str, List[str]]:
    section = _extract_section(content, "Related Topics & Cross-Links")
    result = {"depends_on": [], "prerequisite_for": [], "reinforced_by": []}
    if not section:
        return result

    def _parse_list(label: str) -> List[str]:
        m = re.search(rf"\*\*{re.escape(label)}:\*\*\s*(.+?)(?:\n|$)", section)
        if not m:
            return []
        raw = m.group(1).strip()
        if not raw or raw.startswith("["):
            return []
        return [t.strip() for t in raw.split(",") if t.strip()]

    result["depends_on"] = _parse_list("Depends On")
    result["prerequisite_for"] = _parse_list("Prerequisite For")
    result["reinforced_by"] = _parse_list("Reinforced By")
    return result


# ---------------------------------------------------------------------------
# Mastery calculation
# ---------------------------------------------------------------------------

def compute_mastery(
    quiz_accuracy: Optional[float],
    session_count: int,
    last_session: Optional[datetime],
) -> Optional[float]:
    """
    Returns mastery as a percentage (0–100), or None if no quiz data.

    mastery = quiz_accuracy × time_decay × session_stability_factor
    """
    if quiz_accuracy is None:
        return None

    sessions = max(1, session_count)

    # Session stability: more sessions → higher confidence in the score
    stability = min(1.0, 0.6 + 0.1 * min(sessions, 4))

    # Time decay: more sessions → slower decay
    if last_session is not None:
        days = _days_since(last_session)
        # decay_rate: high when few sessions, approaches 0.3 asymptotically
        decay_rate = max(0.3, 1.0 - (0.015 / math.log(sessions + 2)))
        time_decay = max(0.5, 1.0 - (decay_rate * days / 30))
    else:
        time_decay = 0.7  # conservative default when date unknown

    mastery = quiz_accuracy * time_decay * stability
    return round(min(100.0, mastery), 1)


# ---------------------------------------------------------------------------
# State file parsing (top-level)
# ---------------------------------------------------------------------------

def parse_state_file(filepath: Path) -> Dict:
    content = filepath.read_text(encoding="utf-8")
    topic = filepath.stem

    last_session = extract_last_session_date(content)
    session_count = extract_session_count(content)
    quiz_accuracy = extract_latest_quiz_accuracy(content)
    mastery = compute_mastery(quiz_accuracy, session_count, last_session)

    return {
        "topic": topic,
        "mode": extract_mode(content),
        "session_count": session_count,
        "last_session": last_session,
        "quiz_accuracy": quiz_accuracy,
        "mastery": mastery,
        "related": extract_related_topics(content),
    }


# ---------------------------------------------------------------------------
# Graph generation
# ---------------------------------------------------------------------------

def build_dependency_lines(topics: Dict[str, Dict]) -> List[str]:
    """
    Produce deduplicated dependency lines for the Dependency Map section.
    Sources: depends_on + prerequisite_for cross-links.
    """
    lines = []
    seen = set()

    for topic, data in sorted(topics.items()):
        related = data["related"]

        deps = related["depends_on"]
        if deps:
            key = (topic, "depends_on", tuple(sorted(deps)))
            if key not in seen:
                seen.add(key)
                lines.append(
                    f"- {topic} → depends on: {', '.join(deps)}"
                )

        unlocks = related["prerequisite_for"]
        if unlocks:
            key = (topic, "unlocks", tuple(sorted(unlocks)))
            if key not in seen:
                seen.add(key)
                lines.append(
                    f"- {topic} → unlocks: {', '.join(unlocks)}"
                )

        reinforced = related["reinforced_by"]
        if reinforced:
            key = (topic, "reinforced_by", tuple(sorted(reinforced)))
            if key not in seen:
                seen.add(key)
                lines.append(
                    f"- {topic} → reinforced by: {', '.join(reinforced)}"
                )

    return lines


def format_last_session(dt: Optional[datetime]) -> str:
    if dt is None:
        return "unknown"
    return dt.strftime("%Y-%m-%d")


def mastery_label(mastery: Optional[float]) -> str:
    if mastery is None:
        return "no quiz data"
    return f"{mastery}%"


def generate_graph_markdown(topics: Dict[str, Dict]) -> str:
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Knowledge Graph",
        f"_Last updated: {now_str}_",
        "",
        "<!-- Auto-generated by scripts/generate-knowledge-graph.py — do not edit manually -->",
        "",
    ]

    # --- Topic Index ---
    lines += [
        "## Topic Index",
        "",
        "| Topic | Mode | Mastery | Sessions | Last Session |",
        "|---|---|---|---|---|",
    ]

    for topic, data in sorted(topics.items()):
        lines.append(
            f"| {topic} | {data['mode']} | {mastery_label(data['mastery'])} "
            f"| {data['session_count']} | {format_last_session(data['last_session'])} |"
        )

    lines.append("")

    # --- Dependency Map ---
    dep_lines = build_dependency_lines(topics)
    lines.append("## Dependency Map")
    lines.append("")
    if dep_lines:
        lines += dep_lines
    else:
        lines.append("_No cross-links recorded yet._")
    lines.append("")

    # --- Mastery Gaps ---
    lines.append("## Mastery Gaps (< 80%)")
    lines.append("")

    gaps = [
        (topic, data)
        for topic, data in sorted(topics.items())
        if data["mastery"] is not None and data["mastery"] < 80.0
    ]

    if gaps:
        for topic, data in gaps:
            mastery = data["mastery"]
            sessions = data["session_count"]
            last = format_last_session(data["last_session"])

            # Build a human-readable reason
            reasons = []
            if data["quiz_accuracy"] is not None and data["quiz_accuracy"] < 80:
                reasons.append(f"quiz accuracy {data['quiz_accuracy']}%")
            if data["last_session"] is not None:
                days = _days_since(data["last_session"])
                if days > 14:
                    reasons.append(f"last session {int(days)} days ago")
            if sessions < 3:
                reasons.append(f"only {sessions} session(s)")

            reason_str = " — " + ", ".join(reasons) if reasons else ""
            lines.append(f"- {topic}: {mastery}%{reason_str}")
    else:
        lines.append("_No mastery gaps detected._")

    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(state_dir: str, output_path: Optional[str] = None):
    state_path = Path(state_dir)

    if not state_path.exists():
        print(f"[ERROR] State directory not found: {state_path}")
        sys.exit(1)

    # Collect all state files, excluding the graph itself
    state_files = [
        f for f in state_path.glob("*.md")
        if f.name != "knowledge-graph.md"
    ]

    if not state_files:
        print(f"[WARNING] No state files found in {state_path}")
        sys.exit(0)

    # Parse each file
    topics = {}
    for filepath in state_files:
        try:
            topics[filepath.stem] = parse_state_file(filepath)
        except Exception as e:
            print(f"[WARNING] Could not parse {filepath.name}: {e}")

    if not topics:
        print("[ERROR] No topics could be parsed.")
        sys.exit(1)

    # Generate markdown
    graph_md = generate_graph_markdown(topics)

    # Write output
    out_path = Path(output_path) if output_path else state_path / "knowledge-graph.md"
    out_path.write_text(graph_md, encoding="utf-8")

    print(f"[OK] Knowledge graph written to {out_path}")
    print(f"     Topics: {len(topics)} | Gaps: {sum(1 for d in topics.values() if d['mastery'] is not None and d['mastery'] < 80)}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate knowledge-graph.md from tutoring state files"
    )
    parser.add_argument(
        "--dir",
        default="tutoring-state",
        help="Directory containing state files (default: tutoring-state)",
    )
    parser.add_argument(
        "--output",
        help="Output path for knowledge-graph.md (default: <dir>/knowledge-graph.md)",
    )
    args = parser.parse_args()
    run(args.dir, args.output)


if __name__ == "__main__":
    main()

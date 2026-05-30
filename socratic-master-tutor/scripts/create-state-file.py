#!/usr/bin/env python3
"""
Create a new learning state file with proper schema.

Usage:
  python create-state-file.py --topic "async-javascript" --mode "Coding"
  python create-state-file.py --topic "calculus" --mode "General"

This initializes a new topic state file in tutoring-state/ with all required sections.
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path


def create_state_file(topic_name: str, mode: str, output_dir: str = "tutoring-state"):
    """
    Create a new state file with the proper schema.
    
    Args:
        topic_name: Topic name in kebab-case (e.g., "async-javascript")
        mode: "Coding" or "General"
        output_dir: Directory to save state files (default: tutoring-state/)
    """
    
    # Validate inputs
    if not topic_name:
        print("[ERROR] Topic name is required")
        sys.exit(1)
    
    if mode not in ("Coding", "General"):
        print("[ERROR] Mode must be 'Coding' or 'General'")
        sys.exit(1)
    
    # Create directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Filename
    filename = f"{topic_name}.md"
    filepath = Path(output_dir) / filename
    
    if filepath.exists():
        print(f"[WARNING] File already exists: {filepath}")
        response = input("Overwrite? (y/n): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    # Get full topic title from user
    full_title = input(f"Full topic title (e.g., 'Asynchronous JavaScript'): ").strip()
    if not full_title:
        full_title = topic_name.replace('-', ' ').title()
    
    # Create timestamp
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    
    # Build content
    content = f"""# {topic_name}: {full_title}

**Mode:** {mode}
**Session Initiated:** {now}
**Last Updated:** {now}

## Baseline Assessment

- **Conceptual Understanding:** [Level: Beginner/Intermediate/Advanced + brief descriptor]
- **Problem-Solving Ability:** [Approach to tackling new problems; any patterns noticed]
- **Tool Fluency (if coding):** [Familiarity with relevant languages, frameworks, debugging tools]
- **Confidence Level:** [Self-reported; 1-10 scale]
- **Learning Context:** [Why learning this; real project, coursework, curiosity, etc.]

## Learning Goals

- Goal 1: [specific, measurable outcome]
- Goal 2: [specific, measurable outcome]

## Successful Mental Models

*Analogies, frameworks, or explanations that resonated with this student:*

- **Model 1:** [Explanation] -> **Why it worked:** [Why this clicked]
- **Model 2:** [Explanation] -> **Why it worked:** [Why this clicked]

## Identified Misconceptions & Fixes

*Patterns of incorrect thinking, and how we corrected them:*

- **Misconception 1:** [What they believed incorrectly] -> **Correction:** [How we helped them see the truth]
- **Misconception 2:** [What they believed incorrectly] -> **Correction:** [How we helped them see the truth]

## Pacing & Constraints

- **Preferred Learning Speed:** [Fast/Moderate/Deliberate] - description
- **Session Duration Preference:** [e.g., "30 min focused bursts" or "2 hour deep dives"]
- **Technical Environment:** [Relevant for coding mode: OS, IDE, language version, etc.]

## Progress Over Time

*Chronological log of sessions, breakthroughs, and setbacks:*

- **Session 1 (YYYY-MM-DD):** [Summary of focus, breakthrough, or challenge]
- **Session 2 (YYYY-MM-DD):** [Summary]

## Quiz Performance Tracking

*Detailed stats from Quiz Mode sessions:*

- **Quiz 1 (YYYY-MM-DD):** Topic: [X] | Questions: [N] | Correct: [N] | Accuracy: [%] | Strengths: [X] | Gaps: [X]
- **Quiz 2 (YYYY-MM-DD):** [...]

## Related Topics & Cross-Links

*Connections to other .md files for relationship inference:*

- **Depends On:** [Links to prerequisite topics]
- **Prerequisite For:** [Links to advanced topics]
- **Reinforced By:** [Links to related topics]
"""
    
    # Write file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[SUCCESS] Created: {filepath}")
        print(f"   Topic: {full_title}")
        print(f"   Mode: {mode}")
        print(f"   Ready to fill in with tutoring sessions!")
    except Exception as e:
        print(f"[ERROR] Error creating file: {e}")
        sys.exit(1)

    # Regenerate knowledge graph to include the new topic
    _regenerate_knowledge_graph(output_dir)


def _regenerate_knowledge_graph(state_dir: str):
    """Run generate-knowledge-graph.py to keep the index current."""
    script_dir = Path(__file__).parent
    graph_script = script_dir / "generate-knowledge-graph.py"

    if not graph_script.exists():
        print(f"[WARNING] generate-knowledge-graph.py not found at {graph_script} — skipping graph update.")
        return

    import subprocess
    result = subprocess.run(
        [sys.executable, str(graph_script), "--dir", state_dir],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(result.stdout.strip())
    else:
        print(f"[WARNING] Knowledge graph update failed: {result.stderr.strip()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a new learning state file with proper schema"
    )
    parser.add_argument(
        "--topic",
        required=True,
        help="Topic name in kebab-case (e.g., 'async-javascript')"
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["Coding", "General"],
        help="Learning mode: 'Coding' or 'General'"
    )
    parser.add_argument(
        "--dir",
        default="tutoring-state",
        help="Output directory (default: tutoring-state/)"
    )
    
    args = parser.parse_args()
    create_state_file(args.topic, args.mode, args.dir)

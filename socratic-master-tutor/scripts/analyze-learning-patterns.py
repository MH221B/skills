#!/usr/bin/env python3
"""
Analyze learning patterns across all state files in tutoring-state/.

Parses markdown state files and generates insights:
  - Learning trends (progress over time)
  - Common misconceptions across topics
  - Topic prerequisites and dependencies
  - Mastery progression by quiz performance
  - Time to mastery estimates

Usage:
  python analyze-learning-patterns.py
  python analyze-learning-patterns.py --dir ./my-tutoring-state
  python analyze-learning-patterns.py --output report.txt
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple


class LearningAnalyzer:
    def __init__(self, state_dir: str = "tutoring-state"):
        self.state_dir = Path(state_dir)
        self.state_files = []
        self.data = {}
        
    def load_state_files(self) -> bool:
        """Load all .md files from state directory."""
        if not self.state_dir.exists():
            print(f"[ERROR] Directory not found: {self.state_dir}")
            return False
        
        self.state_files = list(self.state_dir.glob("*.md"))
        if not self.state_files:
            print(f"[WARNING]  No state files found in {self.state_dir}")
            return False
        
        print(f"[LEARNING] Found {len(self.state_files)} state files")
        return True
    
    def parse_state_file(self, filepath: Path) -> Dict:
        """Parse a single state file."""
        topic = filepath.stem
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        data = {
            "topic": topic,
            "filepath": str(filepath),
            "mode": self._extract_field(content, "Mode"),
            "initiated": self._extract_field(content, "Session Initiated"),
            "last_updated": self._extract_field(content, "Last Updated"),
            "baseline": self._extract_section(content, "Baseline Assessment"),
            "misconceptions": self._extract_misconceptions(content),
            "quiz_performance": self._extract_quiz_performance(content),
            "related_topics": self._extract_related_topics(content),
        }
        
        return data
    
    def _extract_field(self, content: str, field_name: str) -> str:
        """Extract a single field value."""
        pattern = rf"\*\*{field_name}:\*\*\s+(.+?)(?:\n|$)"
        match = re.search(pattern, content)
        return match.group(1).strip() if match else None
    
    def _extract_section(self, content: str, section_name: str) -> List[str]:
        """Extract all bullet points from a section."""
        pattern = rf"## {section_name}(.+?)(?=##|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            return []
        
        section = match.group(1)
        bullets = re.findall(r"^-\s+(.+?)$", section, re.MULTILINE)
        return bullets
    
    def _extract_misconceptions(self, content: str) -> List[Tuple[str, str]]:
        """Extract misconceptions and their corrections."""
        pattern = r"\*\*Misconception \d+:\*\*\s+(.+?)\s+->\s+\*\*Correction:\*\*\s+(.+?)(?:\n-|$)"
        matches = re.findall(pattern, content, re.DOTALL)
        return [(m[0].strip(), m[1].strip()) for m in matches]
    
    def _extract_quiz_performance(self, content: str) -> List[Dict]:
        """Extract quiz performance data."""
        pattern = r"\*\*Quiz \d+ \((.+?)\):\*\*\s+(.+?)(?:\n-|\Z)"
        matches = re.findall(pattern, content, re.DOTALL)
        
        quizzes = []
        for date, details in matches:
            quiz = {
                "date": date,
                "accuracy": self._extract_accuracy(details),
                "strengths": self._extract_list_item(details, "Strengths"),
                "gaps": self._extract_list_item(details, "Gaps"),
            }
            quizzes.append(quiz)
        
        return quizzes
    
    def _extract_accuracy(self, text: str) -> float:
        """Extract accuracy percentage."""
        pattern = r"Accuracy:\s+(\d+)%"
        match = re.search(pattern, text)
        return int(match.group(1)) if match else None
    
    def _extract_list_item(self, text: str, item_name: str) -> str:
        """Extract value after a label."""
        pattern = rf"{item_name}:\s+(.+?)(?:\n|$)"
        match = re.search(pattern, text)
        return match.group(1).strip() if match else None
    
    def _extract_related_topics(self, content: str) -> Dict[str, List[str]]:
        """Extract topic relationships."""
        pattern = r"## Related Topics & Cross-Links(.+?)\Z"
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return {"depends_on": [], "prerequisite_for": [], "reinforced_by": []}
        
        section = match.group(1)
        
        # Extract depends on
        depends = re.findall(
            r"\*\*Depends On:\*\*\s+(.+?)(?:\n|$)",
            section
        )
        depends_list = depends[0].split(",") if depends else []
        
        # Extract prerequisite for
        prereq = re.findall(
            r"\*\*Prerequisite For:\*\*\s+(.+?)(?:\n|$)",
            section
        )
        prereq_list = prereq[0].split(",") if prereq else []
        
        # Extract reinforced by
        reinforced = re.findall(
            r"\*\*Reinforced By:\*\*\s+(.+?)(?:\n|$)",
            section
        )
        reinforced_list = reinforced[0].split(",") if reinforced else []
        
        return {
            "depends_on": [t.strip() for t in depends_list if t.strip()],
            "prerequisite_for": [t.strip() for t in prereq_list if t.strip()],
            "reinforced_by": [t.strip() for t in reinforced_list if t.strip()],
        }
    
    def analyze(self) -> Dict:
        """Run full analysis."""
        print("\n[ANALYZE] Analyzing learning patterns...\n")
        
        # Load all files
        for filepath in self.state_files:
            try:
                self.data[filepath.stem] = self.parse_state_file(filepath)
            except Exception as e:
                print(f"[WARNING]  Error parsing {filepath.name}: {e}")
        
        # Generate insights
        insights = {
            "summary": self._summary_stats(),
            "topic_network": self._build_topic_network(),
            "misconceptions": self._common_misconceptions(),
            "mastery_progression": self._mastery_progression(),
            "recommendations": self._generate_recommendations(),
        }
        
        return insights
    
    def _summary_stats(self) -> Dict:
        """Generate summary statistics."""
        total_topics = len(self.data)
        total_sessions = sum(
            len(self._extract_sessions(d)) for d in self.data.values()
        )
        
        coding_topics = sum(1 for d in self.data.values() if d["mode"] == "Coding")
        general_topics = total_topics - coding_topics
        
        avg_quiz_accuracy = self._avg_quiz_accuracy()
        
        return {
            "total_topics": total_topics,
            "coding_topics": coding_topics,
            "general_topics": general_topics,
            "total_sessions": total_sessions,
            "average_quiz_accuracy": f"{avg_quiz_accuracy:.1f}%",
        }
    
    def _avg_quiz_accuracy(self) -> float:
        """Calculate average quiz accuracy across all quizzes."""
        all_accuracies = []
        for data in self.data.values():
            for quiz in data.get("quiz_performance", []):
                if quiz.get("accuracy"):
                    all_accuracies.append(quiz["accuracy"])
        
        return sum(all_accuracies) / len(all_accuracies) if all_accuracies else 0
    
    def _extract_sessions(self, data: Dict) -> List[str]:
        """Extract session dates from baseline."""
        # This would need additional parsing logic
        return []
    
    def _build_topic_network(self) -> Dict:
        """Build dependency graph of topics."""
        network = {
            "prerequisites": defaultdict(list),
            "dependents": defaultdict(list),
        }
        
        for topic, data in self.data.items():
            related = data.get("related_topics", {})
            
            # Build depends_on relationships
            for dep in related.get("depends_on", []):
                network["prerequisites"][topic].append(dep)
                network["dependents"][dep].append(topic)
        
        return dict(network)
    
    def _common_misconceptions(self) -> Dict:
        """Find most common misconceptions across topics."""
        misconception_counts = defaultdict(int)
        
        for data in self.data.values():
            for misconception, _ in data.get("misconceptions", []):
                # Simple categorization
                if "async" in misconception.lower() or "wait" in misconception.lower():
                    key = "Async/Timing Misconceptions"
                elif "derivative" in misconception.lower():
                    key = "Derivative/Rate Misconceptions"
                elif "class" in misconception.lower() or "inherit" in misconception.lower():
                    key = "OOP Misconceptions"
                else:
                    key = "Other"
                
                misconception_counts[key] += 1
        
        return dict(sorted(misconception_counts.items(), key=lambda x: x[1], reverse=True))
    
    def _mastery_progression(self) -> Dict:
        """Track mastery over time based on quiz performance."""
        progression = {}
        
        for topic, data in self.data.items():
            quizzes = data.get("quiz_performance", [])
            if quizzes:
                accuracies = [q.get("accuracy", 0) for q in quizzes if q.get("accuracy")]
                if accuracies:
                    progression[topic] = {
                        "initial": accuracies[0],
                        "current": accuracies[-1],
                        "improvement": accuracies[-1] - accuracies[0],
                        "num_quizzes": len(quizzes),
                    }
        
        return progression
    
    def _generate_recommendations(self) -> List[str]:
        """Generate learning recommendations."""
        recommendations = []
        
        # Check for weak areas
        mastery = self._mastery_progression()
        for topic, progress in mastery.items():
            if progress["current"] < 80:
                recommendations.append(
                    f"[WARNING]  {topic}: {progress['current']}% accuracy. Recommend review session before moving to advanced topics."
                )
        
        # Check for topic sequencing
        network = self._build_topic_network()
        for topic, prereqs in network["prerequisites"].items():
            if prereqs:
                recommendations.append(
                    f"[FORM] {topic} depends on: {', '.join(prereqs)}. Ensure those topics are mastered first."
                )
        
        return recommendations
    
    def print_report(self):
        """Print formatted analysis report."""
        insights = self.analyze()
        
        print("\n" + "="*80)
        print("LEARNING PATTERN ANALYSIS REPORT")
        print("="*80 + "\n")
        
        # Summary
        print("[STATS] SUMMARY")
        print("-" * 40)
        summary = insights["summary"]
        for key, value in summary.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Mastery Progression
        if insights["mastery_progression"]:
            print("\n[PROGRESS] MASTERY PROGRESSION")
            print("-" * 40)
            for topic, progress in insights["mastery_progression"].items():
                improvement = "[UP]" if progress["improvement"] > 0 else "[DOWN]"
                print(f"  {topic}:")
                print(f"    Initial: {progress['initial']}% -> Current: {progress['current']}% {improvement} ({progress['improvement']:+.0f}%)")
                print(f"    Quizzes taken: {progress['num_quizzes']}")
        
        # Topic Network
        if insights["topic_network"]["prerequisites"]:
            print("\n[LINK] TOPIC DEPENDENCIES")
            print("-" * 40)
            for topic, prereqs in insights["topic_network"]["prerequisites"].items():
                if prereqs:
                    print(f"  {topic} ← {', '.join(prereqs)}")
        
        # Recommendations
        if insights["recommendations"]:
            print("\n[TIP] RECOMMENDATIONS")
            print("-" * 40)
            for rec in insights["recommendations"]:
                print(f"  {rec}")
        
        print("\n" + "="*80 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze learning patterns across state files")
    parser.add_argument("--dir", default="tutoring-state", help="State files directory")
    parser.add_argument("--output", help="Output file (default: stdout)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    analyzer = LearningAnalyzer(args.dir)
    
    if not analyzer.load_state_files():
        sys.exit(1)
    
    if args.json:
        insights = analyzer.analyze()
        print(json.dumps(insights, indent=2))
    else:
        analyzer.print_report()


if __name__ == "__main__":
    main()


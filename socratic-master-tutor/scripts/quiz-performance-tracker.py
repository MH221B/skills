#!/usr/bin/env python3
"""
Track and analyze quiz performance over time.

Generates insights from quiz data:
  - Accuracy trends per topic
  - Gap identification (weak areas)
  - Readiness assessment (ready to advance?)
  - Time to mastery estimates
  - Weak topic recommendations

Usage:
  python quiz-performance-tracker.py
  python quiz-performance-tracker.py --topic "async-javascript"
  python quiz-performance-tracker.py --output quiz-report.txt
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class QuizTracker:
    def __init__(self, state_dir: str = "tutoring-state"):
        self.state_dir = Path(state_dir)
        self.quiz_data = defaultdict(list)
        self.state_files = []
        
    def load_quizzes(self) -> bool:
        """Load all quiz data from state files."""
        if not self.state_dir.exists():
            print(f"[ERROR] Directory not found: {self.state_dir}")
            return False
        
        self.state_files = list(self.state_dir.glob("*.md"))
        if not self.state_files:
            print(f"[WARNING]  No state files found in {self.state_dir}")
            return False
        
        for filepath in self.state_files:
            topic = filepath.stem
            quizzes = self._extract_quizzes_from_file(filepath)
            if quizzes:
                self.quiz_data[topic] = quizzes
        
        total_quizzes = sum(len(q) for q in self.quiz_data.values())
        print(f"[LEARNING] Loaded {len(self.state_files)} state files, {total_quizzes} quizzes total")
        
        return bool(self.quiz_data)
    
    def _extract_quizzes_from_file(self, filepath: Path) -> List[Dict]:
        """Extract all quiz entries from a state file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find Quiz Performance Tracking section
        pattern = r"## Quiz Performance Tracking(.+?)(?=##|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            return []
        
        section = match.group(1)
        
        # Extract individual quiz entries
        quiz_pattern = r"\-\s+\*\*Quiz \d+ \((.+?)\):\*\*\s+(.+?)(?=\n\-|\Z)"
        quiz_matches = re.findall(quiz_pattern, section, re.DOTALL)
        
        quizzes = []
        for date_str, details in quiz_matches:
            quiz = self._parse_quiz_entry(date_str, details)
            if quiz:
                quizzes.append(quiz)
        
        return quizzes
    
    def _parse_quiz_entry(self, date_str: str, details: str) -> Optional[Dict]:
        """Parse a single quiz entry."""
        quiz = {
            "date": date_str.strip(),
            "topic": self._extract_field(details, "Topic"),
            "questions": self._extract_number(details, "Questions"),
            "correct": self._extract_number(details, "Correct"),
            "accuracy": self._extract_accuracy(details),
            "strengths": self._extract_field(details, "Strengths"),
            "gaps": self._extract_field(details, "Gaps"),
        }
        
        return quiz if quiz["accuracy"] else None
    
    def _extract_field(self, text: str, field_name: str) -> Optional[str]:
        """Extract a field value."""
        pattern = rf"{field_name}:\s+(.+?)(?:\s\||$)"
        match = re.search(pattern, text)
        return match.group(1).strip() if match else None
    
    def _extract_number(self, text: str, field_name: str) -> Optional[int]:
        """Extract a numeric field."""
        pattern = rf"{field_name}:\s+(\d+)"
        match = re.search(pattern, text)
        return int(match.group(1)) if match else None
    
    def _extract_accuracy(self, text: str) -> Optional[float]:
        """Extract accuracy percentage."""
        pattern = r"Accuracy:\s+(\d+)%"
        match = re.search(pattern, text)
        return int(match.group(1)) if match else None
    
    def get_topic_stats(self, topic: Optional[str] = None) -> Dict:
        """Get statistics for a topic or all topics."""
        if topic:
            if topic not in self.quiz_data:
                return {"error": f"Topic '{topic}' not found"}
            quizzes = self.quiz_data[topic]
        else:
            quizzes = [q for qlist in self.quiz_data.values() for q in qlist]
        
        if not quizzes:
            return {"error": "No quiz data found"}
        
        accuracies = [q["accuracy"] for q in quizzes]
        
        return {
            "total_quizzes": len(quizzes),
            "average_accuracy": sum(accuracies) / len(accuracies),
            "highest_accuracy": max(accuracies),
            "lowest_accuracy": min(accuracies),
            "trend": self._calculate_trend(accuracies),
            "readiness": self._assess_readiness(accuracies),
        }
    
    def _calculate_trend(self, accuracies: List[float]) -> str:
        """Determine if performance is improving or declining."""
        if len(accuracies) < 2:
            return "insufficient data"
        
        early = sum(accuracies[:len(accuracies)//2]) / (len(accuracies)//2)
        late = sum(accuracies[len(accuracies)//2:]) / (len(accuracies) - len(accuracies)//2)
        
        improvement = late - early
        if improvement > 5:
            return f"improving ([UP]{improvement:.1f}%)"
        elif improvement < -5:
            return f"declining ([DOWN]{abs(improvement):.1f}%)"
        else:
            return "stable"
    
    def _assess_readiness(self, accuracies: List[float]) -> str:
        """Assess readiness to move to advanced material."""
        latest = accuracies[-1] if accuracies else 0
        
        if latest >= 90:
            return "Ready for advanced material"
        elif latest >= 75:
            return "Ready to move forward; review weak areas first"
        elif latest >= 60:
            return "Need more practice before advancing"
        else:
            return "Require focused re-learning session"
    
    def identify_weak_topics(self) -> Dict[str, float]:
        """Identify topics with lowest average accuracy."""
        weak = {}
        
        for topic, quizzes in self.quiz_data.items():
            accuracies = [q["accuracy"] for q in quizzes]
            avg = sum(accuracies) / len(accuracies) if accuracies else 100
            
            if avg < 85:
                weak[topic] = avg
        
        return dict(sorted(weak.items(), key=lambda x: x[1]))
    
    def identify_gaps_by_topic(self) -> Dict[str, List[str]]:
        """Extract commonly identified gaps across quizzes."""
        gaps_by_topic = defaultdict(set)
        
        for topic, quizzes in self.quiz_data.items():
            for quiz in quizzes:
                if quiz["gaps"]:
                    # Parse comma-separated gaps
                    gap_list = [g.strip() for g in quiz["gaps"].split(",")]
                    for gap in gap_list:
                        if gap:
                            gaps_by_topic[topic].add(gap)
        
        return {topic: list(gaps) for topic, gaps in gaps_by_topic.items()}
    
    def generate_recommendations(self) -> List[str]:
        """Generate learning recommendations based on quiz performance."""
        recommendations = []
        
        # Identify weak topics
        weak = self.identify_weak_topics()
        for topic, accuracy in weak.items():
            recommendations.append(
                f"[WARNING]  {topic}: {accuracy:.1f}% average accuracy. Recommend review session or tutoring on weak areas."
            )
        
        # Check declining performance
        for topic, quizzes in self.quiz_data.items():
            accuracies = [q["accuracy"] for q in quizzes]
            if len(accuracies) > 1:
                trend = self._calculate_trend(accuracies)
                if "declining" in trend:
                    recommendations.append(
                        f"📉 {topic}: Performance declining. Schedule review session to reinforce learning."
                    )
        
        # Identify topics ready for advancement
        ready = {}
        for topic, quizzes in self.quiz_data.items():
            accuracies = [q["accuracy"] for q in quizzes]
            if accuracies and accuracies[-1] >= 90:
                ready[topic] = accuracies[-1]
        
        if ready:
            for topic, acc in ready.items():
                recommendations.append(
                    f"[OK] {topic}: {acc}% on latest quiz. Ready for advanced material!"
                )
        
        return recommendations
    
    def print_report(self, topic: Optional[str] = None):
        """Print detailed quiz performance report."""
        print("\n" + "="*80)
        print("QUIZ PERFORMANCE REPORT")
        print("="*80 + "\n")
        
        if topic:
            print(f"[STATS] TOPIC: {topic}\n")
            stats = self.get_topic_stats(topic)
            if "error" in stats:
                print(f"[ERROR] {stats['error']}")
            else:
                self._print_stats(stats)
                
                # Detailed quiz history
                print("\n[FORM] QUIZ HISTORY")
                print("-" * 40)
                for quiz in self.quiz_data.get(topic, []):
                    print(f"  {quiz['date']}")
                    print(f"    Accuracy: {quiz['accuracy']}% ({quiz['correct']}/{quiz['questions']})")
                    if quiz["strengths"]:
                        print(f"    Strengths: {quiz['strengths']}")
                    if quiz["gaps"]:
                        print(f"    Gaps: {quiz['gaps']}")
        
        else:
            # Summary across all topics
            print("[STATS] OVERALL SUMMARY\n")
            
            all_stats = self.get_topic_stats()
            if "error" not in all_stats:
                self._print_stats(all_stats)
            
            # Per-topic summary
            if self.quiz_data:
                print("\n[PROGRESS] BY TOPIC")
                print("-" * 40)
                for topic in sorted(self.quiz_data.keys()):
                    stats = self.get_topic_stats(topic)
                    avg = stats.get("average_accuracy", 0)
                    print(f"  {topic}: {avg:.1f}% avg ({stats.get('total_quizzes', 0)} quizzes)")
            
            # Weak topics
            weak = self.identify_weak_topics()
            if weak:
                print("\n[WARNING]  WEAK TOPICS (< 85% accuracy)")
                print("-" * 40)
                for topic, acc in weak.items():
                    print(f"  {topic}: {acc:.1f}%")
            
            # Gaps
            gaps = self.identify_gaps_by_topic()
            if gaps:
                print("\n[ANALYZE] IDENTIFIED GAPS")
                print("-" * 40)
                for topic, gap_list in gaps.items():
                    if gap_list:
                        print(f"  {topic}:")
                        for gap in gap_list:
                            print(f"    - {gap}")
            
            # Recommendations
            recommendations = self.generate_recommendations()
            if recommendations:
                print("\n[TIP] RECOMMENDATIONS")
                print("-" * 40)
                for rec in recommendations:
                    print(f"  {rec}")
        
        print("\n" + "="*80 + "\n")
    
    def _print_stats(self, stats: Dict):
        """Print formatted statistics."""
        if "error" in stats:
            print(f"[ERROR] {stats['error']}")
            return
        
        print(f"  Total Quizzes: {stats.get('total_quizzes', 0)}")
        print(f"  Average Accuracy: {stats.get('average_accuracy', 0):.1f}%")
        print(f"  Range: {stats.get('lowest_accuracy', 0)}% - {stats.get('highest_accuracy', 0)}%")
        print(f"  Trend: {stats.get('trend', 'unknown')}")
        print(f"  Readiness: {stats.get('readiness', 'unknown')}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Track and analyze quiz performance")
    parser.add_argument("--dir", default="tutoring-state", help="State files directory")
    parser.add_argument("--topic", help="Specific topic to analyze")
    parser.add_argument("--output", help="Output file (default: stdout)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    tracker = QuizTracker(args.dir)
    
    if not tracker.load_quizzes():
        sys.exit(1)
    
    if args.json:
        data = {
            "summary": tracker.get_topic_stats(),
            "weak_topics": tracker.identify_weak_topics(),
            "gaps": tracker.identify_gaps_by_topic(),
            "recommendations": tracker.generate_recommendations(),
        }
        print(json.dumps(data, indent=2))
    else:
        if args.output:
            import io
            from contextlib import redirect_stdout
            
            with open(args.output, 'w') as f:
                with redirect_stdout(f):
                    tracker.print_report(args.topic)
            print(f"[OK] Report saved to {args.output}")
        else:
            tracker.print_report(args.topic)


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Resume Journey Map Generator
Creates ASCII art maps from resume/CV data showing professional journey
"""

import re
from datetime import datetime
from typing import List, Dict, Tuple
from dataclasses import dataclass
import argparse


@dataclass
class Milestone:
    """Represents a career milestone"""
    date: datetime
    title: str
    organization: str
    milestone_type: str  # 'education' or 'work'

    def __str__(self):
        return f"{self.title} at {self.organization}"

    def short_label(self) -> str:
        """Generate a concise label for the milestone"""
        if self.milestone_type == 'education':
            return f"{self.title}"
        return f"{self.title} @ {self.organization}"


class ResumeParser:
    """Parse resume text to extract chronological milestones"""

    def __init__(self, resume_text: str):
        self.resume_text = resume_text
        self.milestones: List[Milestone] = []

    def parse(self) -> List[Milestone]:
        """Extract milestones from resume text"""
        # Simple parsing logic - can be enhanced with NLP/ML
        self.milestones = []

        # Split into sections
        lines = self.resume_text.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect section headers
            if re.match(r'(EDUCATION|Education)', line, re.IGNORECASE):
                current_section = 'education'
                continue
            elif re.match(r'(EXPERIENCE|WORK EXPERIENCE|Work Experience|Employment)', line, re.IGNORECASE):
                current_section = 'work'
                continue

            # Parse date patterns
            date_match = re.search(r'(\d{4})\s*-\s*(\d{4}|Present|Current)', line, re.IGNORECASE)
            if date_match:
                start_year = int(date_match.group(1))
                end_text = date_match.group(2)

                # Extract title and organization
                # Format: "Title | Organization | 2020-2022"
                parts = re.split(r'\s*[|\-]\s*', line)

                if len(parts) >= 2:
                    title = parts[0].strip()
                    organization = parts[1].strip()

                    # Remove date from organization if present
                    organization = re.sub(r'\d{4}\s*-\s*(\d{4}|Present|Current)', '', organization).strip()

                    if current_section:
                        milestone = Milestone(
                            date=datetime(start_year, 1, 1),
                            title=title,
                            organization=organization,
                            milestone_type=current_section
                        )
                        self.milestones.append(milestone)

        # Sort by date
        self.milestones.sort(key=lambda m: m.date)
        return self.milestones


class ASCIIJourneyMap:
    """Generate ASCII art journey map"""

    def __init__(self, milestones: List[Milestone], width: int = 80):
        self.milestones = milestones
        self.width = width
        self.map_lines: List[str] = []

    def generate(self) -> str:
        """Generate the ASCII journey map"""
        if not self.milestones:
            return "No milestones found!"

        self.map_lines = []

        # Add title
        title = "═══ PROFESSIONAL JOURNEY MAP ═══"
        self.map_lines.append(title.center(self.width))
        self.map_lines.append("")

        # Generate S-shaped path with nodes
        self._generate_s_path()

        return '\n'.join(self.map_lines)

    def _generate_s_path(self):
        """Generate S-shaped winding path with milestone nodes"""
        nodes_per_row = 2  # Number of milestones per horizontal segment
        current_milestone = 0
        direction = 1  # 1 for left-to-right, -1 for right-to-left

        while current_milestone < len(self.milestones):
            # Determine how many nodes to place in this row
            remaining = len(self.milestones) - current_milestone
            nodes_in_row = min(nodes_per_row, remaining)

            # Get milestones for this row
            row_milestones = self.milestones[current_milestone:current_milestone + nodes_in_row]

            # Draw the path segment with nodes
            if direction == 1:
                self._draw_left_to_right_segment(row_milestones)
            else:
                self._draw_right_to_left_segment(row_milestones)

            current_milestone += nodes_in_row

            # Add connecting path to next row if there are more milestones
            if current_milestone < len(self.milestones):
                if direction == 1:
                    self._draw_right_curve()
                else:
                    self._draw_left_curve()

            # Alternate direction
            direction *= -1

    def _draw_left_to_right_segment(self, milestones: List[Milestone]):
        """Draw a left-to-right path segment with milestones"""
        if len(milestones) == 1:
            # Single milestone
            label = milestones[0].short_label()
            year = milestones[0].date.year

            # Node with label
            node_line = f"    ╭─────[ {year} ]─────╮"
            self.map_lines.append(node_line)

            label_line = f"    │ {label[:40].ljust(40)} │"
            self.map_lines.append(label_line)

            bottom_line = "────┤                                          ├───>"
            self.map_lines.append(bottom_line)
            self.map_lines.append("")

        else:
            # Two milestones
            m1, m2 = milestones[0], milestones[1]

            # First milestone
            label1 = m1.short_label()[:25]
            year1 = m1.date.year

            node_line = f"    ╭──[ {year1} ]──╮"
            self.map_lines.append(node_line)

            label_line = f"    │ {label1.ljust(25)} │"
            self.map_lines.append(label_line)

            # Connection to second milestone
            label2 = m2.short_label()[:25]
            year2 = m2.date.year

            path_line = f"────┤           ├───────────>"
            self.map_lines.append(path_line)

            self.map_lines.append("")

            node_line2 = f"                            ╭──[ {year2} ]──╮"
            self.map_lines.append(node_line2)

            label_line2 = f"                            │ {label2.ljust(25)} │"
            self.map_lines.append(label_line2)

            bottom_line2 = "                       ─────┤           ├───>"
            self.map_lines.append(bottom_line2)
            self.map_lines.append("")

    def _draw_right_to_left_segment(self, milestones: List[Milestone]):
        """Draw a right-to-left path segment with milestones"""
        if len(milestones) == 1:
            # Single milestone
            label = milestones[0].short_label()
            year = milestones[0].date.year

            node_line = f"                                 ╭─────[ {year} ]─────╮"
            self.map_lines.append(node_line)

            label_line = f"                                 │ {label[:40].ljust(40)} │"
            self.map_lines.append(label_line)

            bottom_line = "    <───┤                                          ├────"
            self.map_lines.append(bottom_line)
            self.map_lines.append("")

        else:
            # Two milestones
            m1, m2 = milestones[0], milestones[1]

            # First milestone (right side)
            label1 = m1.short_label()[:25]
            year1 = m1.date.year

            node_line = f"                                      ╭──[ {year1} ]──╮"
            self.map_lines.append(node_line)

            label_line = f"                                      │ {label1.ljust(25)} │"
            self.map_lines.append(label_line)

            path_line = f"                  <───────────┤           ├────"
            self.map_lines.append(path_line)

            self.map_lines.append("")

            # Second milestone (left side)
            label2 = m2.short_label()[:25]
            year2 = m2.date.year

            node_line2 = f"         ╭──[ {year2} ]──╮"
            self.map_lines.append(node_line2)

            label_line2 = f"         │ {label2.ljust(25)} │"
            self.map_lines.append(label_line2)

            bottom_line2 = "    <────┤           ├─────"
            self.map_lines.append(bottom_line2)
            self.map_lines.append("")

    def _draw_right_curve(self):
        """Draw a curve connecting right side to next row"""
        self.map_lines.append("                                                          │")
        self.map_lines.append("                                                          │")
        self.map_lines.append("                                                          ╰──╮")
        self.map_lines.append("                                                             │")
        self.map_lines.append("                                                             ▼")
        self.map_lines.append("")

    def _draw_left_curve(self):
        """Draw a curve connecting left side to next row"""
        self.map_lines.append("    │")
        self.map_lines.append("    │")
        self.map_lines.append("    ╰──╮")
        self.map_lines.append("       │")
        self.map_lines.append("       ▼")
        self.map_lines.append("")


def main():
    parser = argparse.ArgumentParser(
        description='Generate ASCII art journey map from resume/CV'
    )
    parser.add_argument(
        'resume_file',
        help='Path to resume text file'
    )
    parser.add_argument(
        '-w', '--width',
        type=int,
        default=80,
        help='Width of ASCII art output (default: 80)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file (default: print to stdout)'
    )

    args = parser.parse_args()

    # Read resume file
    try:
        with open(args.resume_file, 'r', encoding='utf-8') as f:
            resume_text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.resume_file}' not found")
        return 1
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1

    # Parse resume
    resume_parser = ResumeParser(resume_text)
    milestones = resume_parser.parse()

    if not milestones:
        print("Warning: No milestones found in resume")
        print("Make sure your resume has EDUCATION and EXPERIENCE sections")
        print("with dates in format: YYYY-YYYY or YYYY-Present")
        return 1

    print(f"Found {len(milestones)} milestones:")
    for m in milestones:
        print(f"  - {m.date.year}: {m}")
    print()

    # Generate ASCII map
    map_generator = ASCIIJourneyMap(milestones, width=args.width)
    ascii_map = map_generator.generate()

    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(ascii_map)
        print(f"Journey map saved to: {args.output}")
    else:
        print(ascii_map)

    return 0


if __name__ == '__main__':
    exit(main())

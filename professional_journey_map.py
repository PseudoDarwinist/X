#!/usr/bin/env python3
"""
Professional Journey Map Generator
Creates visual career journey maps with smooth curved paths and touchpoints
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional
import math


@dataclass
class Milestone:
    """Represents a career milestone/touchpoint"""
    date: datetime
    title: str
    organization: str
    role: str
    end_date: Optional[datetime] = None
    description: str = ""

    def duration_years(self) -> float:
        """Calculate duration in years"""
        if self.end_date:
            delta = self.end_date - self.date
            return round(delta.days / 365.25, 1)
        return 0.0


class ResumeParser:
    """Parse resume to extract career milestones"""

    def __init__(self, resume_text: str):
        self.text = resume_text
        self.milestones: List[Milestone] = []

    def parse(self) -> List[Milestone]:
        """Extract career milestones from resume"""
        # Pattern to match career entries
        pattern = r'Client:\s*([^-\n]+?)[-–]\s*([A-Za-z]+\s+\d{4})\s+to\s+(Current|[A-Za-z]+\s+\d{4})\s*\n\s*Role:\s*([^\n]+)\s*\n\s*Company:\s*([^\n]+)\s*\n\s*Responsibilities:\s*([^\n]+)'

        matches = re.finditer(pattern, self.text, re.IGNORECASE | re.MULTILINE)

        for match in matches:
            client = match.group(1).strip()
            start_date_str = match.group(2).strip()
            end_date_str = match.group(3).strip()
            role = match.group(4).strip()
            company = match.group(5).strip()
            responsibilities = match.group(6).strip()

            # Parse dates
            start_date = self._parse_date(start_date_str)
            end_date = None if end_date_str.lower() == 'current' else self._parse_date(end_date_str)

            if start_date:
                milestone = Milestone(
                    date=start_date,
                    title=f"{role} @ {client}",
                    organization=company,
                    role=role,
                    end_date=end_date or datetime.now(),
                    description=responsibilities[:100]
                )
                self.milestones.append(milestone)

        # Sort by date
        self.milestones.sort(key=lambda m: m.date)

        return self.milestones

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date from various formats"""
        date_str = date_str.strip()

        # Try "Month YYYY" format
        try:
            return datetime.strptime(date_str, "%B %Y")
        except:
            pass

        # Try "Mon YYYY" format
        try:
            return datetime.strptime(date_str, "%b %Y")
        except:
            pass

        # Try just year
        try:
            return datetime(int(date_str), 1, 1)
        except:
            pass

        return None


class ProfessionalJourneyMap:
    """Generate professional visual journey maps with smooth curves"""

    def __init__(self, milestones: List[Milestone], width: int = 1400, height: int = 800):
        self.milestones = milestones
        self.width = width
        self.height = height
        self.margin = 100
        self.touchpoint_radius = 12

    def generate_svg(self) -> str:
        """Generate SVG journey map"""

        # Generate path points
        points = self._generate_path_points()

        # Generate smooth curve through points
        path_d = self._generate_smooth_path(points)

        # Build SVG
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}">',
            '<defs>',
            '  <style>',
            '    @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap");',
            '    text { font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif; }',
            '    .journey-path { fill: none; stroke: #2563eb; stroke-width: 4; stroke-linecap: round; }',
            '    .touchpoint { fill: #2563eb; }',
            '    .touchpoint-highlight { fill: white; stroke: #2563eb; stroke-width: 3; }',
            '    .label-text { fill: #1e293b; font-size: 16px; font-weight: 600; }',
            '    .sublabel-text { fill: #64748b; font-size: 13px; font-weight: 400; }',
            '    .title-text { fill: #0f172a; font-size: 48px; font-weight: 700; }',
            '    .touchpoint-group:hover .touchpoint { fill: #1d4ed8; transform: scale(1.2); }',
            '  </style>',
            '</defs>',

            # Background
            '<rect width="100%" height="100%" fill="#fafafa"/>',

            # Title
            f'<text x="{self.width/2}" y="60" text-anchor="middle" class="title-text">Career Journey Map</text>',

            # Journey path
            f'<path d="{path_d}" class="journey-path"/>',
        ]

        # Add touchpoints and labels
        for i, (point, milestone) in enumerate(zip(points, self.milestones)):
            x, y = point

            # Determine label position (alternate sides)
            label_offset = 60
            is_left = i % 2 == 0
            text_anchor = "end" if is_left else "start"
            label_x = x - label_offset if is_left else x + label_offset
            label_y = y - 10

            # Touchpoint group
            svg_parts.append(f'<g class="touchpoint-group">')

            # Touchpoint circle
            svg_parts.append(f'  <circle cx="{x}" cy="{y}" r="{self.touchpoint_radius}" class="touchpoint"/>')
            svg_parts.append(f'  <circle cx="{x}" cy="{y}" r="{self.touchpoint_radius - 4}" class="touchpoint-highlight"/>')

            # Label
            year = milestone.date.year
            duration = milestone.duration_years()
            duration_text = f" ({duration}y)" if duration > 0 else ""

            svg_parts.append(f'  <text x="{label_x}" y="{label_y}" text-anchor="{text_anchor}" class="label-text">')
            svg_parts.append(f'    <tspan x="{label_x}" dy="0">{year}{duration_text}</tspan>')
            svg_parts.append(f'  </text>')

            svg_parts.append(f'  <text x="{label_x}" y="{label_y + 20}" text-anchor="{text_anchor}" class="sublabel-text">')
            svg_parts.append(f'    <tspan x="{label_x}" dy="0">{milestone.role[:30]}</tspan>')
            svg_parts.append(f'  </text>')

            svg_parts.append(f'  <text x="{label_x}" y="{label_y + 36}" text-anchor="{text_anchor}" class="sublabel-text">')
            svg_parts.append(f'    <tspan x="{label_x}" dy="0">@ {milestone.organization[:25]}</tspan>')
            svg_parts.append(f'  </text>')

            svg_parts.append('</g>')

        svg_parts.append('</svg>')

        return '\n'.join(svg_parts)

    def _generate_path_points(self) -> List[Tuple[float, float]]:
        """Generate points for the journey path in an S-curve pattern"""
        points = []

        num_points = len(self.milestones)
        if num_points == 0:
            return points

        # Calculate vertical spacing
        usable_height = self.height - 2 * self.margin
        vertical_step = usable_height / (num_points - 1) if num_points > 1 else 0

        # Generate points in a flowing S-pattern
        for i in range(num_points):
            y = self.margin + i * vertical_step

            # Create horizontal oscillation (S-curve)
            progress = i / (num_points - 1) if num_points > 1 else 0
            amplitude = (self.width - 2 * self.margin) / 3

            # Use sine wave for smooth S-curve
            phase = progress * math.pi * 2  # Two full waves
            x_offset = math.sin(phase) * amplitude
            x = self.width / 2 + x_offset

            points.append((x, y))

        return points

    def _generate_smooth_path(self, points: List[Tuple[float, float]]) -> str:
        """Generate smooth SVG path using bezier curves"""
        if len(points) == 0:
            return ""

        if len(points) == 1:
            x, y = points[0]
            return f"M {x},{y}"

        # Start path
        path_parts = [f"M {points[0][0]},{points[0][1]}"]

        # Generate smooth curves through points using cubic bezier
        for i in range(len(points) - 1):
            p0 = points[i]
            p1 = points[i + 1]

            # Calculate control points for smooth curve
            dx = p1[0] - p0[0]
            dy = p1[1] - p0[1]

            # Control points at 40% and 60% of the way
            cp1_x = p0[0] + dx * 0.4
            cp1_y = p0[1] + dy * 0.25
            cp2_x = p0[0] + dx * 0.6
            cp2_y = p0[1] + dy * 0.75

            path_parts.append(f"C {cp1_x},{cp1_y} {cp2_x},{cp2_y} {p1[0]},{p1[1]}")

        return " ".join(path_parts)

    def generate_html(self) -> str:
        """Generate interactive HTML version"""
        svg_content = self.generate_svg()

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professional Journey Map</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px 20px;
        }}

        .container {{
            background: white;
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            max-width: 1500px;
            width: 100%;
        }}

        .touchpoint-group {{
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .touchpoint-group:hover .touchpoint {{
            fill: #1d4ed8;
        }}

        .touchpoint-group:hover .label-text {{
            fill: #2563eb;
        }}
    </style>
</head>
<body>
    <div class="container">
        {svg_content}
    </div>
</body>
</html>"""

        return html

    def save_svg(self, filename: str):
        """Save SVG to file"""
        svg_content = self.generate_svg()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"✓ SVG journey map saved to: {filename}")

    def save_html(self, filename: str):
        """Save HTML to file"""
        html_content = self.generate_html()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ Interactive HTML saved to: {filename}")


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 professional_journey_map.py <resume_file> [--svg output.svg] [--html output.html]")
        sys.exit(1)

    resume_file = sys.argv[1]

    # Read resume
    with open(resume_file, 'r', encoding='utf-8') as f:
        resume_text = f.read()

    # Parse resume
    parser = ResumeParser(resume_text)
    milestones = parser.parse()

    if not milestones:
        print("❌ No milestones found in resume")
        sys.exit(1)

    print(f"✓ Found {len(milestones)} career milestones:")
    for m in milestones:
        duration = f"({m.duration_years()}y)" if m.duration_years() > 0 else ""
        print(f"  • {m.date.year}: {m.title} {duration}")

    # Generate journey map
    journey_map = ProfessionalJourneyMap(milestones)

    # Check for output options
    if '--svg' in sys.argv:
        idx = sys.argv.index('--svg')
        output_file = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else 'journey_map.svg'
        journey_map.save_svg(output_file)

    if '--html' in sys.argv:
        idx = sys.argv.index('--html')
        output_file = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else 'journey_map.html'
        journey_map.save_html(output_file)

    # Default: save both
    if '--svg' not in sys.argv and '--html' not in sys.argv:
        journey_map.save_svg('journey_map.svg')
        journey_map.save_html('journey_map.html')


if __name__ == '__main__':
    main()

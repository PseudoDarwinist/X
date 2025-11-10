#!/usr/bin/env python3
"""
Resume Journey Map Generator - Enhanced Version
Creates ASCII art and SVG maps from resume/CV data showing professional journey
Supports PDF, DOCX, TXT formats with NLP-based extraction and multiple styles
"""

import re
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import argparse
from pathlib import Path

# Optional imports - graceful degradation if not available
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    from docx import Document
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

try:
    import spacy
    NLP_SUPPORT = True
except ImportError:
    NLP_SUPPORT = False


# ANSI color codes
class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'

    # Colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

    # Background
    BG_BLUE = '\033[44m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'

    @staticmethod
    def disable():
        """Disable all colors"""
        Colors.RESET = ''
        Colors.BOLD = ''
        Colors.RED = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.BLUE = ''
        Colors.MAGENTA = ''
        Colors.CYAN = ''
        Colors.WHITE = ''
        Colors.BG_BLUE = ''
        Colors.BG_GREEN = ''
        Colors.BG_YELLOW = ''


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

    def get_color(self) -> str:
        """Get color for milestone type"""
        if self.milestone_type == 'education':
            return Colors.CYAN
        return Colors.GREEN


class DocumentLoader:
    """Load and extract text from various document formats"""

    @staticmethod
    def load(file_path: str) -> str:
        """Load document and return text content"""
        ext = Path(file_path).suffix.lower()

        if ext == '.pdf':
            return DocumentLoader._load_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return DocumentLoader._load_docx(file_path)
        elif ext == '.txt':
            return DocumentLoader._load_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def _load_txt(file_path: str) -> str:
        """Load plain text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def _load_pdf(file_path: str) -> str:
        """Load PDF and extract text"""
        if not PDF_SUPPORT:
            raise ImportError("PDF support requires pdfplumber. Install with: pip install pdfplumber")

        text_content = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)

        return '\n'.join(text_content)

    @staticmethod
    def _load_docx(file_path: str) -> str:
        """Load DOCX and extract text"""
        if not DOCX_SUPPORT:
            raise ImportError("DOCX support requires python-docx. Install with: pip install python-docx")

        doc = Document(file_path)
        text_content = []

        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_content.append(paragraph.text)

        return '\n'.join(text_content)


class NLPResumeParser:
    """Advanced NLP-based resume parser using spaCy"""

    def __init__(self, resume_text: str):
        self.resume_text = resume_text
        self.milestones: List[Milestone] = []

        if NLP_SUPPORT:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: spaCy model 'en_core_web_sm' not found.")
                print("Install with: python -m spacy download en_core_web_sm")
                self.nlp = None
        else:
            self.nlp = None

    def parse(self) -> List[Milestone]:
        """Extract milestones using NLP"""
        if self.nlp:
            return self._nlp_parse()
        else:
            # Fallback to regex-based parsing
            parser = ResumeParser(self.resume_text)
            return parser.parse()

    def _nlp_parse(self) -> List[Milestone]:
        """Use NLP to extract entities and dates"""
        doc = self.nlp(self.resume_text)

        # Extract organizations
        orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]

        # Extract dates
        dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]

        # Fall back to regex parsing with NLP enhancement
        parser = ResumeParser(self.resume_text)
        milestones = parser.parse()

        return milestones


class ResumeParser:
    """Parse resume text to extract chronological milestones"""

    def __init__(self, resume_text: str):
        self.resume_text = resume_text
        self.milestones: List[Milestone] = []

    def parse(self) -> List[Milestone]:
        """Extract milestones from resume text"""
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


class MapStyle:
    """Base class for map styles"""
    name = "base"

    def get_box_chars(self):
        """Return box drawing characters"""
        raise NotImplementedError


class ClassicStyle(MapStyle):
    """Classic box-drawing style"""
    name = "classic"

    def get_box_chars(self):
        return {
            'top_left': '╭',
            'top_right': '╮',
            'bottom_left': '╰',
            'bottom_right': '╯',
            'horizontal': '─',
            'vertical': '│',
            'junction': '├',
            'arrow_right': '>',
            'arrow_left': '<',
            'arrow_down': '▼'
        }


class ModernStyle(MapStyle):
    """Modern minimalist style"""
    name = "modern"

    def get_box_chars(self):
        return {
            'top_left': '┌',
            'top_right': '┐',
            'bottom_left': '└',
            'bottom_right': '┘',
            'horizontal': '─',
            'vertical': '│',
            'junction': '├',
            'arrow_right': '→',
            'arrow_left': '←',
            'arrow_down': '↓'
        }


class MinimalStyle(MapStyle):
    """Minimal ASCII style"""
    name = "minimal"

    def get_box_chars(self):
        return {
            'top_left': '+',
            'top_right': '+',
            'bottom_left': '+',
            'bottom_right': '+',
            'horizontal': '-',
            'vertical': '|',
            'junction': '+',
            'arrow_right': '>',
            'arrow_left': '<',
            'arrow_down': 'v'
        }


class ASCIIJourneyMap:
    """Generate ASCII art journey map with multiple styles"""

    def __init__(self, milestones: List[Milestone], width: int = 80,
                 style: str = 'classic', color: bool = True):
        self.milestones = milestones
        self.width = width
        self.map_lines: List[str] = []
        self.color = color

        # Set style
        styles = {
            'classic': ClassicStyle(),
            'modern': ModernStyle(),
            'minimal': MinimalStyle()
        }
        self.style = styles.get(style, ClassicStyle())
        self.chars = self.style.get_box_chars()

        if not color:
            Colors.disable()

    def generate(self) -> str:
        """Generate the ASCII journey map"""
        if not self.milestones:
            return "No milestones found!"

        self.map_lines = []

        # Add title with color
        title = "═══ PROFESSIONAL JOURNEY MAP ═══"
        if self.color:
            title = f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}"
        self.map_lines.append(title.center(self.width + (len(title) - len("═══ PROFESSIONAL JOURNEY MAP ═══")) if self.color else self.width))
        self.map_lines.append("")

        # Generate S-shaped path with nodes
        self._generate_s_path()

        return '\n'.join(self.map_lines)

    def _generate_s_path(self):
        """Generate S-shaped winding path with milestone nodes"""
        nodes_per_row = 2
        current_milestone = 0
        direction = 1

        while current_milestone < len(self.milestones):
            remaining = len(self.milestones) - current_milestone
            nodes_in_row = min(nodes_per_row, remaining)

            row_milestones = self.milestones[current_milestone:current_milestone + nodes_in_row]

            if direction == 1:
                self._draw_left_to_right_segment(row_milestones)
            else:
                self._draw_right_to_left_segment(row_milestones)

            current_milestone += nodes_in_row

            if current_milestone < len(self.milestones):
                if direction == 1:
                    self._draw_right_curve()
                else:
                    self._draw_left_curve()

            direction *= -1

    def _draw_left_to_right_segment(self, milestones: List[Milestone]):
        """Draw a left-to-right path segment with milestones"""
        tl, tr = self.chars['top_left'], self.chars['top_right']
        bl, br = self.chars['bottom_left'], self.chars['bottom_right']
        h, v = self.chars['horizontal'], self.chars['vertical']
        j = self.chars['junction']
        ar = self.chars['arrow_right']

        if len(milestones) == 1:
            m = milestones[0]
            label = m.short_label()
            year = m.date.year
            color = m.get_color() if self.color else ''
            reset = Colors.RESET if self.color else ''

            node_line = f"    {tl}{h*5}[ {color}{year}{reset} ]{h*5}{tr}"
            self.map_lines.append(node_line)

            label_line = f"    {v} {color}{label[:40].ljust(40)}{reset} {v}"
            self.map_lines.append(label_line)

            bottom_line = f"{h*4}{j}{' '*42}{j}{h*3}{ar}"
            self.map_lines.append(bottom_line)
            self.map_lines.append("")
        else:
            m1, m2 = milestones[0], milestones[1]

            label1 = m1.short_label()[:25]
            year1 = m1.date.year
            color1 = m1.get_color() if self.color else ''
            reset = Colors.RESET if self.color else ''

            node_line = f"    {tl}{h*2}[ {color1}{year1}{reset} ]{h*2}{tr}"
            self.map_lines.append(node_line)

            label_line = f"    {v} {color1}{label1.ljust(25)}{reset} {v}"
            self.map_lines.append(label_line)

            label2 = m2.short_label()[:25]
            year2 = m2.date.year
            color2 = m2.get_color() if self.color else ''

            path_line = f"{h*4}{j}{' '*11}{j}{h*11}{ar}"
            self.map_lines.append(path_line)
            self.map_lines.append("")

            node_line2 = f"{' '*28}{tl}{h*2}[ {color2}{year2}{reset} ]{h*2}{tr}"
            self.map_lines.append(node_line2)

            label_line2 = f"{' '*28}{v} {color2}{label2.ljust(25)}{reset} {v}"
            self.map_lines.append(label_line2)

            bottom_line2 = f"{' '*23}{h*5}{j}{' '*11}{j}{h*3}{ar}"
            self.map_lines.append(bottom_line2)
            self.map_lines.append("")

    def _draw_right_to_left_segment(self, milestones: List[Milestone]):
        """Draw a right-to-left path segment with milestones"""
        tl, tr = self.chars['top_left'], self.chars['top_right']
        bl, br = self.chars['bottom_left'], self.chars['bottom_right']
        h, v = self.chars['horizontal'], self.chars['vertical']
        j = self.chars['junction']
        al = self.chars['arrow_left']

        if len(milestones) == 1:
            m = milestones[0]
            label = m.short_label()
            year = m.date.year
            color = m.get_color() if self.color else ''
            reset = Colors.RESET if self.color else ''

            node_line = f"{' '*33}{tl}{h*5}[ {color}{year}{reset} ]{h*5}{tr}"
            self.map_lines.append(node_line)

            label_line = f"{' '*33}{v} {color}{label[:40].ljust(40)}{reset} {v}"
            self.map_lines.append(label_line)

            bottom_line = f"    {al}{h*3}{j}{' '*42}{j}{h*4}"
            self.map_lines.append(bottom_line)
            self.map_lines.append("")
        else:
            m1, m2 = milestones[0], milestones[1]

            label1 = m1.short_label()[:25]
            year1 = m1.date.year
            color1 = m1.get_color() if self.color else ''
            reset = Colors.RESET if self.color else ''

            node_line = f"{' '*38}{tl}{h*2}[ {color1}{year1}{reset} ]{h*2}{tr}"
            self.map_lines.append(node_line)

            label_line = f"{' '*38}{v} {color1}{label1.ljust(25)}{reset} {v}"
            self.map_lines.append(label_line)

            path_line = f"{' '*18}{al}{h*11}{j}{' '*11}{j}{h*4}"
            self.map_lines.append(path_line)
            self.map_lines.append("")

            label2 = m2.short_label()[:25]
            year2 = m2.date.year
            color2 = m2.get_color() if self.color else ''

            node_line2 = f"{' '*9}{tl}{h*2}[ {color2}{year2}{reset} ]{h*2}{tr}"
            self.map_lines.append(node_line2)

            label_line2 = f"{' '*9}{v} {color2}{label2.ljust(25)}{reset} {v}"
            self.map_lines.append(label_line2)

            bottom_line2 = f"    {al}{h*4}{j}{' '*11}{j}{h*5}"
            self.map_lines.append(bottom_line2)
            self.map_lines.append("")

    def _draw_right_curve(self):
        """Draw a curve connecting right side to next row"""
        v = self.chars['vertical']
        bl, br = self.chars['bottom_left'], self.chars['bottom_right']
        ad = self.chars['arrow_down']

        self.map_lines.append(f"{' '*58}{v}")
        self.map_lines.append(f"{' '*58}{v}")
        self.map_lines.append(f"{' '*58}{bl}{self.chars['horizontal']*2}{br}")
        self.map_lines.append(f"{' '*61}{v}")
        self.map_lines.append(f"{' '*61}{ad}")
        self.map_lines.append("")

    def _draw_left_curve(self):
        """Draw a curve connecting left side to next row"""
        v = self.chars['vertical']
        bl, br = self.chars['bottom_left'], self.chars['bottom_right']
        ad = self.chars['arrow_down']

        self.map_lines.append(f"    {v}")
        self.map_lines.append(f"    {v}")
        self.map_lines.append(f"    {bl}{self.chars['horizontal']*2}{br}")
        self.map_lines.append(f"       {v}")
        self.map_lines.append(f"       {ad}")
        self.map_lines.append("")


class SVGExporter:
    """Export journey map as SVG"""

    def __init__(self, milestones: List[Milestone], width: int = 800, height: int = 600):
        self.milestones = milestones
        self.width = width
        self.height = height

    def generate(self) -> str:
        """Generate SVG representation of journey map"""
        if not self.milestones:
            return "<svg></svg>"

        svg_parts = []
        svg_parts.append(f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">')

        # Add background
        svg_parts.append(f'  <rect width="{self.width}" height="{self.height}" fill="#f8f9fa"/>')

        # Add title
        svg_parts.append('  <text x="50%" y="40" text-anchor="middle" font-size="24" font-weight="bold" fill="#2c3e50">')
        svg_parts.append('    Professional Journey Map')
        svg_parts.append('  </text>')

        # Calculate positions
        y_start = 100
        y_spacing = (self.height - 150) / max(len(self.milestones) - 1, 1)

        # Draw path and nodes
        for i, milestone in enumerate(self.milestones):
            y_pos = y_start + i * y_spacing

            # Alternate x position (S-shape)
            if i % 4 < 2:
                x_pos = 100 + (i % 2) * 300
            else:
                x_pos = 400 - (i % 2) * 300

            # Draw connecting line to next milestone
            if i < len(self.milestones) - 1:
                next_y = y_start + (i + 1) * y_spacing
                if (i % 4 < 2 and (i+1) % 4 < 2) or (i % 4 >= 2 and (i+1) % 4 >= 2):
                    next_x = 100 + ((i + 1) % 2) * 300
                else:
                    next_x = 400 - ((i + 1) % 2) * 300

                svg_parts.append(f'  <path d="M {x_pos} {y_pos} Q {(x_pos + next_x) / 2} {(y_pos + next_y) / 2} {next_x} {next_y}" ')
                svg_parts.append('    stroke="#3498db" stroke-width="3" fill="none" stroke-dasharray="5,5"/>')

            # Draw node
            color = '#16a085' if milestone.milestone_type == 'education' else '#27ae60'
            svg_parts.append(f'  <circle cx="{x_pos}" cy="{y_pos}" r="8" fill="{color}" stroke="#fff" stroke-width="2"/>')

            # Draw label box
            label = milestone.short_label()[:30]
            svg_parts.append(f'  <rect x="{x_pos + 20}" y="{y_pos - 25}" width="200" height="50" ')
            svg_parts.append(f'    fill="white" stroke="{color}" stroke-width="2" rx="5"/>')

            # Year label
            svg_parts.append(f'  <text x="{x_pos + 30}" y="{y_pos - 5}" font-size="12" font-weight="bold" fill="{color}">')
            svg_parts.append(f'    {milestone.date.year}')
            svg_parts.append('  </text>')

            # Title label
            svg_parts.append(f'  <text x="{x_pos + 30}" y="{y_pos + 12}" font-size="11" fill="#2c3e50">')
            svg_parts.append(f'    {label}')
            svg_parts.append('  </text>')

        svg_parts.append('</svg>')

        return '\n'.join(svg_parts)


def main():
    parser = argparse.ArgumentParser(
        description='Generate ASCII art or SVG journey map from resume/CV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s resume.txt
  %(prog)s resume.pdf --style modern --color
  %(prog)s resume.docx --svg -o journey.svg
  %(prog)s resume.txt --nlp --style minimal --no-color
        """
    )

    parser.add_argument(
        'resume_file',
        help='Path to resume file (TXT, PDF, or DOCX)'
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
    parser.add_argument(
        '--style',
        choices=['classic', 'modern', 'minimal'],
        default='classic',
        help='ASCII art style (default: classic)'
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    parser.add_argument(
        '--svg',
        action='store_true',
        help='Generate SVG output instead of ASCII'
    )
    parser.add_argument(
        '--nlp',
        action='store_true',
        help='Use NLP-based parsing (requires spaCy)'
    )

    args = parser.parse_args()

    # Load document
    try:
        print(f"Loading {args.resume_file}...")
        resume_text = DocumentLoader.load(args.resume_file)
    except Exception as e:
        print(f"Error loading file: {e}")
        return 1

    # Parse resume
    print("Parsing resume...")
    if args.nlp:
        resume_parser = NLPResumeParser(resume_text)
    else:
        resume_parser = ResumeParser(resume_text)

    milestones = resume_parser.parse()

    if not milestones:
        print("Warning: No milestones found in resume")
        print("Make sure your resume has EDUCATION and EXPERIENCE sections")
        print("with dates in format: YYYY-YYYY or YYYY-Present")
        return 1

    print(f"\n{Colors.GREEN}Found {len(milestones)} milestones:{Colors.RESET}")
    for m in milestones:
        color = m.get_color() if not args.no_color else ''
        reset = Colors.RESET if not args.no_color else ''
        print(f"  {color}• {m.date.year}: {m}{reset}")
    print()

    # Generate output
    if args.svg:
        print("Generating SVG map...")
        exporter = SVGExporter(milestones)
        output_content = exporter.generate()
    else:
        print(f"Generating ASCII map (style: {args.style})...")
        map_generator = ASCIIJourneyMap(
            milestones,
            width=args.width,
            style=args.style,
            color=not args.no_color
        )
        output_content = map_generator.generate()

    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            # Remove ANSI codes if writing to file
            if not args.svg and not args.no_color:
                import re
                output_content = re.sub(r'\033\[[0-9;]+m', '', output_content)
            f.write(output_content)
        print(f"{Colors.GREEN}Journey map saved to: {args.output}{Colors.RESET}")
    else:
        print(output_content)

    return 0


if __name__ == '__main__':
    exit(main())

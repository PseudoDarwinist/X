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

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_SUPPORT = True
except ImportError:
    PIL_SUPPORT = False


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
    end_date: Optional[datetime] = None
    skills: List[str] = None

    def __post_init__(self):
        if self.skills is None:
            self.skills = []

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

    def duration_years(self) -> float:
        """Calculate duration in years"""
        if self.end_date:
            delta = self.end_date - self.date
            return delta.days / 365.25
        return 0.0


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

                # Calculate end date
                if end_text.lower() in ['present', 'current']:
                    end_date = datetime.now()
                else:
                    end_year = int(end_text)
                    end_date = datetime(end_year, 12, 31)

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
                            milestone_type=current_section,
                            end_date=end_date
                        )
                        self.milestones.append(milestone)

        # Sort by date
        self.milestones.sort(key=lambda m: m.date)
        return self.milestones


class CareerStatistics:
    """Analyze career data and generate statistics"""

    def __init__(self, milestones: List[Milestone]):
        self.milestones = milestones
        self.work_milestones = [m for m in milestones if m.milestone_type == 'work']
        self.education_milestones = [m for m in milestones if m.milestone_type == 'education']

    def total_experience_years(self) -> float:
        """Calculate total years of work experience"""
        if not self.work_milestones:
            return 0.0

        total_days = 0
        for milestone in self.work_milestones:
            if milestone.end_date:
                delta = milestone.end_date - milestone.date
                total_days += delta.days

        return round(total_days / 365.25, 1)

    def average_job_tenure(self) -> float:
        """Calculate average time spent at each job"""
        if not self.work_milestones:
            return 0.0

        total_years = sum(m.duration_years() for m in self.work_milestones if m.end_date)
        count = len([m for m in self.work_milestones if m.end_date])

        return round(total_years / count, 1) if count > 0 else 0.0

    def total_companies(self) -> int:
        """Count unique companies"""
        companies = set(m.organization for m in self.work_milestones)
        return len(companies)

    def total_degrees(self) -> int:
        """Count education degrees"""
        return len(self.education_milestones)

    def career_gaps(self) -> List[Dict]:
        """Detect gaps in career timeline"""
        gaps = []
        sorted_milestones = sorted(self.work_milestones, key=lambda m: m.date)

        for i in range(len(sorted_milestones) - 1):
            current = sorted_milestones[i]
            next_ms = sorted_milestones[i + 1]

            if current.end_date and next_ms.date:
                gap_days = (next_ms.date - current.end_date).days

                # Consider gaps > 30 days
                if gap_days > 30:
                    gaps.append({
                        'start': current.end_date,
                        'end': next_ms.date,
                        'duration_months': round(gap_days / 30.44),
                        'after': current.title,
                        'before': next_ms.title
                    })

        return gaps

    def career_progression_score(self) -> int:
        """Calculate career progression score (0-100)"""
        score = 50  # Base score

        # More experience = higher score
        years = self.total_experience_years()
        score += min(years * 2, 20)

        # Education bonus
        score += min(self.total_degrees() * 5, 15)

        # Progression indicators (looking for seniority keywords)
        seniority_keywords = ['senior', 'lead', 'principal', 'staff', 'director', 'manager', 'vp', 'chief']
        has_progression = any(
            any(keyword in m.title.lower() for keyword in seniority_keywords)
            for m in self.work_milestones
        )
        if has_progression:
            score += 15

        return min(score, 100)

    def get_current_role(self) -> Optional[Milestone]:
        """Get current/most recent role"""
        if not self.milestones:
            return None

        # Find milestone with most recent end date or Present
        current = max(self.work_milestones, key=lambda m: m.end_date if m.end_date else m.date, default=None)
        return current

    def generate_dashboard(self, color: bool = True) -> str:
        """Generate ASCII art statistics dashboard"""
        lines = []

        # Title
        title = "📊 CAREER STATISTICS DASHBOARD"
        if color:
            title = f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}"
        lines.append(title)
        lines.append("═" * 50)
        lines.append("")

        # Experience
        years = self.total_experience_years()
        exp_icon = "📅" if color else "[EXP]"
        exp_text = f"{exp_icon} Total Experience: {years} years"
        if color:
            exp_text = f"{exp_icon} Total Experience: {Colors.GREEN}{years}{Colors.RESET} years"
        lines.append(exp_text)

        # Average tenure
        tenure = self.average_job_tenure()
        tenure_icon = "⏱️ " if color else "[AVG]"
        tenure_text = f"{tenure_icon} Average Job Tenure: {tenure} years"
        if color:
            tenure_text = f"{tenure_icon} Average Job Tenure: {Colors.CYAN}{tenure}{Colors.RESET} years"
        lines.append(tenure_text)

        # Companies
        companies = self.total_companies()
        comp_icon = "🏢" if color else "[CMP]"
        lines.append(f"{comp_icon} Companies Worked: {companies}")

        # Education
        degrees = self.total_degrees()
        edu_icon = "🎓" if color else "[EDU]"
        lines.append(f"{edu_icon} Degrees Earned: {degrees}")

        # Current role
        current = self.get_current_role()
        if current:
            curr_icon = "💼" if color else "[NOW]"
            curr_text = f"{curr_icon} Current Role: {current.title}"
            if color:
                curr_text = f"{curr_icon} Current Role: {Colors.YELLOW}{current.title}{Colors.RESET}"
            lines.append(curr_text)

        lines.append("")

        # Career progression score
        score = self.career_progression_score()
        prog_icon = "📈" if color else "[SCR]"
        prog_text = f"{prog_icon} Career Progression Score: {score}/100"

        # Progress bar
        filled = int(score / 10)
        bar = "█" * filled + "░" * (10 - filled)
        if color:
            if score >= 80:
                bar = f"{Colors.GREEN}{bar}{Colors.RESET}"
            elif score >= 60:
                bar = f"{Colors.YELLOW}{bar}{Colors.RESET}"
            else:
                bar = f"{Colors.RED}{bar}{Colors.RESET}"
            prog_text = f"{prog_icon} Career Progression Score: {Colors.BOLD}{score}/100{Colors.RESET}"

        lines.append(prog_text)
        lines.append(f"   {bar}")
        lines.append("")

        # Career gaps
        gaps = self.career_gaps()
        if gaps:
            gap_icon = "⚠️ " if color else "[GAP]"
            gap_title = f"{gap_icon} Career Gaps Detected: {len(gaps)}"
            if color:
                gap_title = f"{gap_icon} Career Gaps Detected: {Colors.YELLOW}{len(gaps)}{Colors.RESET}"
            lines.append(gap_title)

            for gap in gaps[:3]:  # Show max 3 gaps
                months = gap['duration_months']
                gap_text = f"   • {months} months gap ({gap['start'].strftime('%Y')} - {gap['end'].strftime('%Y')})"
                lines.append(gap_text)

            if len(gaps) > 3:
                lines.append(f"   ... and {len(gaps) - 3} more")
            lines.append("")

        lines.append("═" * 50)

        return '\n'.join(lines)


class SkillsExtractor:
    """Extract and visualize skills from resume"""

    # Common technical skills to look for
    SKILL_CATEGORIES = {
        'programming': [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'ruby',
            'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'bash', 'shell'
        ],
        'web': [
            'html', 'css', 'react', 'angular', 'vue', 'node.js', 'nodejs', 'express',
            'django', 'flask', 'spring', 'asp.net', 'jquery', 'bootstrap', 'tailwind'
        ],
        'data': [
            'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
            'pandas', 'numpy', 'spark', 'hadoop', 'kafka', 'airflow'
        ],
        'ml_ai': [
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras',
            'scikit-learn', 'nlp', 'computer vision', 'neural networks', 'ai'
        ],
        'cloud': [
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins',
            'ci/cd', 'devops', 'cloud computing'
        ],
        'tools': [
            'git', 'github', 'gitlab', 'jira', 'confluence', 'slack', 'agile', 'scrum'
        ]
    }

    def __init__(self, resume_text: str, milestones: List[Milestone] = None):
        self.resume_text = resume_text.lower()
        self.milestones = milestones or []
        self.skills = []

    def extract_skills(self) -> List[str]:
        """Extract skills from resume text"""
        found_skills = set()

        # Extract from all categories
        for category, skills_list in self.SKILL_CATEGORIES.items():
            for skill in skills_list:
                if skill in self.resume_text:
                    found_skills.add(skill.title())

        self.skills = sorted(list(found_skills))
        return self.skills

    def generate_skills_timeline(self, color: bool = True) -> str:
        """Generate ASCII art skills timeline"""
        if not self.skills:
            self.extract_skills()

        if not self.skills:
            return "No skills detected. Add a SKILLS section to your resume."

        lines = []

        # Title
        title = "💡 SKILLS TIMELINE"
        if color:
            title = f"{Colors.BOLD}{Colors.MAGENTA}{title}{Colors.RESET}"
        lines.append(title)
        lines.append("═" * 50)
        lines.append("")

        # Group skills by decade or milestone period
        if self.milestones:
            # Show skills evolution over career
            work_milestones = [m for m in self.milestones if m.milestone_type == 'work']

            if work_milestones:
                # Early career (first 2 milestones)
                early_years = [m.date.year for m in work_milestones[:2]]
                if early_years:
                    year_range = f"{min(early_years)}-{max(early_years)}" if len(early_years) > 1 else str(early_years[0])
                    lines.append(f"📅 Early Career ({year_range})")
                    # Show subset of skills (simulated - first 40%)
                    early_skills = self.skills[:max(1, len(self.skills) * 2 // 5)]
                    for skill in early_skills:
                        skill_color = Colors.CYAN if color else ''
                        reset = Colors.RESET if color else ''
                        lines.append(f"   {skill_color}▪{reset} {skill}")
                    lines.append("")

                # Mid career
                if len(work_milestones) >= 4:
                    mid_years = [m.date.year for m in work_milestones[2:4]]
                    year_range = f"{min(mid_years)}-{max(mid_years)}" if len(mid_years) > 1 else str(mid_years[0])
                    lines.append(f"📅 Mid Career ({year_range})")
                    mid_skills = self.skills[:max(1, len(self.skills) * 3 // 5)]
                    for skill in mid_skills:
                        skill_color = Colors.YELLOW if color else ''
                        reset = Colors.RESET if color else ''
                        lines.append(f"   {skill_color}▪{reset} {skill}")
                    lines.append("")

                # Recent/Current
                if len(work_milestones) > 4:
                    recent_years = [m.date.year for m in work_milestones[-2:]]
                    year_range = f"{min(recent_years)}-Present"
                    lines.append(f"📅 Recent ({year_range})")
                    for skill in self.skills:
                        skill_color = Colors.GREEN if color else ''
                        reset = Colors.RESET if color else ''
                        lines.append(f"   {skill_color}▪{reset} {skill}")
                    lines.append("")

        else:
            # Simple list if no milestones
            lines.append("📋 All Skills:")
            for skill in self.skills:
                lines.append(f"   ▪ {skill}")
            lines.append("")

        # Summary
        summary = f"Total Skills: {len(self.skills)}"
        if color:
            summary = f"Total Skills: {Colors.BOLD}{Colors.GREEN}{len(self.skills)}{Colors.RESET}"
        lines.append(summary)

        lines.append("═" * 50)

        return '\n'.join(lines)

    def generate_skills_cloud(self, color: bool = True, width: int = 50) -> str:
        """Generate ASCII art skills cloud/bar chart"""
        if not self.skills:
            self.extract_skills()

        if not self.skills:
            return "No skills detected."

        lines = []

        # Title
        title = "☁️  SKILLS CLOUD"
        if color:
            title = f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}"
        lines.append(title)
        lines.append("═" * width)
        lines.append("")

        # Show top skills with bars (simulated frequency)
        for i, skill in enumerate(self.skills[:15]):  # Top 15 skills
            # Simulate skill "strength" (could be improved with actual frequency counting)
            strength = max(5, 15 - i)  # Decreasing strength
            bar_length = min(strength, width - len(skill) - 5)
            bar = "█" * bar_length

            if color:
                # Color gradient based on strength
                if strength > 10:
                    bar = f"{Colors.GREEN}{bar}{Colors.RESET}"
                elif strength > 7:
                    bar = f"{Colors.YELLOW}{bar}{Colors.RESET}"
                else:
                    bar = f"{Colors.CYAN}{bar}{Colors.RESET}"

            lines.append(f"{skill.ljust(20)} {bar}")

        lines.append("")
        lines.append("═" * width)

        return '\n'.join(lines)


class AchievementExtractor:
    """Extract and highlight quantified achievements from resume"""

    # Patterns for quantified achievements
    ACHIEVEMENT_PATTERNS = [
        r'(\d+%)',  # Percentages
        r'(\$[\d,]+[KMB]?)',  # Money
        r'(increased|improved|reduced|decreased|grew|generated|saved|achieved)\s+.*?(\d+%|\d+x|\$[\d,]+)',
        r'(\d+\+?)\s+(users|customers|clients|employees|team|members)',
        r'(led|managed|supervised)\s+.*?(\d+)',
        r'(\d+[xX])',  # Multipliers (2x, 3X, etc.)
        r'(top|#)\s*(\d+)',  # Rankings
        r'(won|awarded|received)\s+.*?(award|prize|recognition)',
    ]

    def __init__(self, resume_text: str):
        self.resume_text = resume_text
        self.achievements = []

    def extract_achievements(self) -> List[Dict]:
        """Extract achievement statements with metrics"""
        achievements = []
        lines = self.resume_text.split('\n')

        for line in lines:
            line = line.strip()
            if not line or len(line) < 20:  # Skip short lines
                continue

            # Check if line contains achievement indicators
            has_metric = False
            metrics_found = []

            for pattern in self.ACHIEVEMENT_PATTERNS:
                matches = re.findall(pattern, line, re.IGNORECASE)
                if matches:
                    has_metric = True
                    for match in matches:
                        if isinstance(match, tuple):
                            metrics_found.extend([m for m in match if m])
                        else:
                            metrics_found.append(match)

            if has_metric:
                achievements.append({
                    'text': line,
                    'metrics': list(set(metrics_found)),  # Remove duplicates
                    'category': self._categorize_achievement(line)
                })

        self.achievements = achievements
        return achievements

    def _categorize_achievement(self, text: str) -> str:
        """Categorize achievement by type"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['revenue', 'sales', 'profit', 'money', '$']):
            return 'financial'
        elif any(word in text_lower for word in ['team', 'led', 'managed', 'supervised']):
            return 'leadership'
        elif any(word in text_lower for word in ['improved', 'optimized', 'enhanced', 'performance']):
            return 'improvement'
        elif any(word in text_lower for word in ['developed', 'built', 'created', 'launched']):
            return 'creation'
        elif any(word in text_lower for word in ['reduced', 'decreased', 'saved']):
            return 'efficiency'
        elif any(word in text_lower for word in ['award', 'recognition', 'won', 'achieved']):
            return 'recognition'
        else:
            return 'general'

    def generate_achievements_report(self, color: bool = True) -> str:
        """Generate ASCII art achievements report"""
        if not self.achievements:
            self.extract_achievements()

        if not self.achievements:
            return "No quantified achievements detected.\nTip: Add metrics and numbers to your accomplishments!"

        lines = []

        # Title
        title = "🏆 KEY ACHIEVEMENTS"
        if color:
            title = f"{Colors.BOLD}{Colors.YELLOW}{title}{Colors.RESET}"
        lines.append(title)
        lines.append("═" * 70)
        lines.append("")

        # Group by category
        categories = {}
        for ach in self.achievements:
            cat = ach['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(ach)

        # Category icons and colors
        category_info = {
            'financial': ('💰', 'Financial Impact', Colors.GREEN),
            'leadership': ('👥', 'Leadership', Colors.BLUE),
            'improvement': ('📈', 'Performance Improvement', Colors.MAGENTA),
            'creation': ('🚀', 'Product/Project Creation', Colors.CYAN),
            'efficiency': ('⚡', 'Efficiency Gains', Colors.YELLOW),
            'recognition': ('🎖️ ', 'Awards & Recognition', Colors.GREEN),
            'general': ('✨', 'Other Achievements', Colors.WHITE)
        }

        for category, achievements in categories.items():
            icon, title, cat_color = category_info.get(category, ('•', category.title(), Colors.WHITE))

            cat_title = f"{icon} {title}"
            if color:
                cat_title = f"{cat_color}{cat_title}{Colors.RESET}"

            lines.append(cat_title)
            lines.append("─" * 70)

            for ach in achievements:
                # Highlight metrics in the text
                text = ach['text']

                if color and ach['metrics']:
                    # Highlight each metric
                    for metric in ach['metrics']:
                        text = text.replace(metric, f"{Colors.BOLD}{Colors.YELLOW}{metric}{Colors.RESET}")

                # Indent and bullet point
                wrapped_lines = self._wrap_text(text, 65)
                for i, wrapped_line in enumerate(wrapped_lines):
                    if i == 0:
                        lines.append(f"  • {wrapped_line}")
                    else:
                        lines.append(f"    {wrapped_line}")

            lines.append("")

        # Summary
        total = len(self.achievements)
        summary = f"Total Quantified Achievements: {total}"
        if color:
            summary = f"Total Quantified Achievements: {Colors.BOLD}{Colors.GREEN}{total}{Colors.RESET}"
        lines.append(summary)

        # Show metric breakdown
        all_metrics = []
        for ach in self.achievements:
            all_metrics.extend(ach['metrics'])

        # Count percentage achievements
        percentages = [m for m in all_metrics if '%' in m]
        dollar_amounts = [m for m in all_metrics if '$' in m]

        if percentages or dollar_amounts:
            lines.append("")
            lines.append("Metrics Summary:")
            if percentages:
                lines.append(f"  • Percentage improvements: {len(percentages)}")
            if dollar_amounts:
                lines.append(f"  • Financial metrics: {len(dollar_amounts)}")

        lines.append("")
        lines.append("═" * 70)

        return '\n'.join(lines)

    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to specified width"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            # Remove ANSI codes for length calculation
            word_length = len(re.sub(r'\033\[[0-9;]+m', '', word))

            if current_length + word_length + 1 <= width:
                current_line.append(word)
                current_length += word_length + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length

        if current_line:
            lines.append(' '.join(current_line))

        return lines if lines else [text]


class ResumeScorer:
    """Score and analyze resume quality - minimalist approach"""

    def __init__(self, resume_text: str, milestones: List[Milestone]):
        self.resume_text = resume_text
        self.milestones = milestones
        self.score = 0
        self.feedback = []

    def calculate_score(self) -> int:
        """Calculate overall resume score (0-100) - simple and clean"""
        score = 0
        self.feedback = []

        # Content completeness (30 points)
        content_score = self._score_content()
        score += content_score

        # Quantified achievements (25 points)
        achievements_score = self._score_achievements()
        score += achievements_score

        # Experience quality (25 points)
        experience_score = self._score_experience()
        score += experience_score

        # Skills presence (20 points)
        skills_score = self._score_skills()
        score += skills_score

        self.score = min(score, 100)
        return self.score

    def _score_content(self) -> int:
        """Score content completeness"""
        score = 0
        text_lower = self.resume_text.lower()

        # Check for essential sections
        if 'education' in text_lower:
            score += 10
        else:
            self.feedback.append(('warning', 'Add an EDUCATION section'))

        if any(word in text_lower for word in ['experience', 'work', 'employment']):
            score += 10
        else:
            self.feedback.append(('warning', 'Add a WORK EXPERIENCE section'))

        if any(word in text_lower for word in ['skills', 'technologies', 'tools']):
            score += 10
        else:
            self.feedback.append(('warning', 'Add a SKILLS section'))

        return score

    def _score_achievements(self) -> int:
        """Score quantified achievements"""
        extractor = AchievementExtractor(self.resume_text)
        achievements = extractor.extract_achievements()

        count = len(achievements)
        if count == 0:
            score = 0
            self.feedback.append(('improve', 'Add numbers and metrics to show impact'))
        elif count < 3:
            score = 10
            self.feedback.append(('good', f'Found {count} quantified achievements'))
        elif count < 6:
            score = 18
            self.feedback.append(('great', f'Good use of metrics: {count} achievements'))
        else:
            score = 25
            self.feedback.append(('excellent', f'Excellent quantification: {count} achievements'))

        return score

    def _score_experience(self) -> int:
        """Score experience quality"""
        score = 0
        work_milestones = [m for m in self.milestones if m.milestone_type == 'work']

        if not work_milestones:
            self.feedback.append(('warning', 'Add work experience'))
            return 0

        # Years of experience
        total_years = sum(m.duration_years() for m in work_milestones if m.end_date)
        if total_years >= 5:
            score += 10
        elif total_years >= 2:
            score += 7
        elif total_years >= 1:
            score += 5

        # Career progression
        seniority_keywords = ['senior', 'lead', 'principal', 'staff', 'director', 'manager']
        has_progression = any(
            any(keyword in m.title.lower() for keyword in seniority_keywords)
            for m in work_milestones
        )

        if has_progression:
            score += 10
            self.feedback.append(('good', 'Shows career progression'))
        else:
            self.feedback.append(('improve', 'Consider highlighting growth in responsibilities'))

        # Consistency (no large gaps)
        stats = CareerStatistics(self.milestones)
        gaps = stats.career_gaps()
        if not gaps:
            score += 5
        elif len(gaps) <= 1:
            score += 3

        return score

    def _score_skills(self) -> int:
        """Score skills section"""
        extractor = SkillsExtractor(self.resume_text, self.milestones)
        skills = extractor.extract_skills()

        count = len(skills)
        if count == 0:
            score = 0
            self.feedback.append(('warning', 'List your technical skills'))
        elif count < 5:
            score = 10
            self.feedback.append(('improve', f'Add more relevant skills (currently {count})'))
        elif count < 10:
            score = 15
            self.feedback.append(('good', f'{count} skills listed'))
        else:
            score = 20
            self.feedback.append(('excellent', f'Strong skills portfolio: {count} skills'))

        return score

    def generate_report(self, color: bool = True) -> str:
        """Generate clean, minimalist score report"""
        if self.score == 0:
            self.calculate_score()

        lines = []

        # Title - clean and simple
        title = "RESUME SCORE"
        if color:
            title = f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}"
        lines.append(title)
        lines.append("")

        # Score - big and prominent
        score_display = f"{self.score}/100"
        if color:
            if self.score >= 80:
                score_color = Colors.GREEN
            elif self.score >= 60:
                score_color = Colors.YELLOW
            else:
                score_color = Colors.RED
            score_display = f"{Colors.BOLD}{score_color}{self.score}{Colors.RESET}/100"

        lines.append(f"  {score_display}")
        lines.append("")

        # Simple progress bar
        filled = int(self.score / 10)
        bar = "●" * filled + "○" * (10 - filled)
        if color:
            if self.score >= 80:
                bar = f"{Colors.GREEN}{'●' * filled}{Colors.RESET}{'○' * (10 - filled)}"
            elif self.score >= 60:
                bar = f"{Colors.YELLOW}{'●' * filled}{Colors.RESET}{'○' * (10 - filled)}"
            else:
                bar = f"{Colors.RED}{'●' * filled}{Colors.RESET}{'○' * (10 - filled)}"

        lines.append(f"  {bar}")
        lines.append("")

        # Feedback - grouped by type, clean format
        if self.feedback:
            excellent = [f for f in self.feedback if f[0] == 'excellent']
            good = [f for f in self.feedback if f[0] in ['good', 'great']]
            improve = [f for f in self.feedback if f[0] == 'improve']
            warnings = [f for f in self.feedback if f[0] == 'warning']

            if excellent:
                lines.append("Strengths")
                for _, msg in excellent:
                    icon = "✓" if not color else f"{Colors.GREEN}✓{Colors.RESET}"
                    lines.append(f"  {icon} {msg}")
                lines.append("")

            if good:
                if not excellent:
                    lines.append("Strengths")
                for _, msg in good:
                    icon = "✓" if not color else f"{Colors.GREEN}✓{Colors.RESET}"
                    lines.append(f"  {icon} {msg}")
                lines.append("")

            if improve:
                lines.append("Improvements")
                for _, msg in improve:
                    icon = "→" if not color else f"{Colors.YELLOW}→{Colors.RESET}"
                    lines.append(f"  {icon} {msg}")
                lines.append("")

            if warnings:
                lines.append("Required")
                for _, msg in warnings:
                    icon = "!" if not color else f"{Colors.RED}!{Colors.RESET}"
                    lines.append(f"  {icon} {msg}")
                lines.append("")

        # Grade - clean letter grade
        if self.score >= 90:
            grade = "A+"
            grade_text = "Excellent"
        elif self.score >= 85:
            grade = "A"
            grade_text = "Very Strong"
        elif self.score >= 80:
            grade = "A-"
            grade_text = "Strong"
        elif self.score >= 75:
            grade = "B+"
            grade_text = "Good"
        elif self.score >= 70:
            grade = "B"
            grade_text = "Above Average"
        elif self.score >= 60:
            grade = "B-"
            grade_text = "Average"
        elif self.score >= 50:
            grade = "C"
            grade_text = "Needs Work"
        else:
            grade = "D"
            grade_text = "Needs Major Revision"

        if color:
            if self.score >= 80:
                grade = f"{Colors.BOLD}{Colors.GREEN}{grade}{Colors.RESET}"
            elif self.score >= 60:
                grade = f"{Colors.BOLD}{Colors.YELLOW}{grade}{Colors.RESET}"
            else:
                grade = f"{Colors.BOLD}{Colors.RED}{grade}{Colors.RESET}"

        lines.append(f"Grade: {grade} — {grade_text}")

        return '\n'.join(lines)


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


class InteractiveHTMLExporter:
    """Generate minimalist interactive HTML journey map - Apple style"""

    def __init__(self, milestones: List[Milestone]):
        self.milestones = milestones

    def generate(self) -> str:
        """Generate clean, interactive HTML with smooth animations"""
        # Convert milestones to JavaScript data
        milestones_js = []
        for m in self.milestones:
            end_year = m.end_date.year if m.end_date else None
            milestones_js.append({
                'title': m.title,
                'organization': m.organization,
                'start_year': m.date.year,
                'end_year': end_year,
                'type': m.milestone_type
            })

        import json
        milestones_json = json.dumps(milestones_js)

        # Load template
        template_path = Path(__file__).parent / 'templates' / 'journey_interactive.html'

        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            return template.replace('{{MILESTONES_DATA}}', milestones_json)
        else:
            # Inline minimal template if file doesn't exist
            return self._generate_inline_html(milestones_json)

    def _generate_inline_html(self, milestones_json: str) -> str:
        """Generate inline HTML if template file not found"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Career Journey</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #fafafa;
            color: #1d1d1f;
            padding: 60px 20px;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h1 {{ font-size: 48px; font-weight: 600; text-align: center; margin-bottom: 60px; }}
        .timeline {{ position: relative; padding: 20px 0; }}
        .timeline-line {{
            position: absolute; left: 50%; top: 0; bottom: 0; width: 2px;
            background: linear-gradient(180deg, #007aff 0%, #5856d6 100%);
            transform: translateX(-50%); opacity: 0.3;
        }}
        .milestone {{
            position: relative; margin: 60px 0; opacity: 0; transform: translateY(30px);
            transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .milestone.visible {{ opacity: 1; transform: translateY(0); }}
        .milestone:nth-child(odd) {{ text-align: right; padding-right: 55%; }}
        .milestone:nth-child(even) {{ text-align: left; padding-left: 55%; }}
        .milestone-content {{
            background: white; padding: 24px 32px; border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
            display: inline-block; min-width: 300px;
            transition: all 0.3s ease;
        }}
        .milestone-content:hover {{
            transform: scale(1.02);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        }}
        .milestone-dot {{
            position: absolute; left: 50%; top: 24px; width: 16px; height: 16px;
            background: #007aff; border: 4px solid white; border-radius: 50%;
            transform: translateX(-50%); box-shadow: 0 2px 8px rgba(0, 122, 255, 0.3);
            z-index: 10; transition: all 0.3s ease;
        }}
        .milestone-dot.education {{
            background: #5856d6;
            box-shadow: 0 2px 8px rgba(88, 86, 214, 0.3);
        }}
        .milestone-year {{
            font-size: 14px; font-weight: 600; color: #007aff;
            margin-bottom: 4px;
        }}
        .milestone-year.education {{ color: #5856d6; }}
        .milestone-title {{
            font-size: 20px; font-weight: 600; margin-bottom: 8px; color: #1d1d1f;
        }}
        .milestone-org {{ font-size: 16px; color: #6e6e73; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Career Journey</h1>
        <div class="timeline">
            <div class="timeline-line"></div>
        </div>
    </div>
    <script>
        const milestones = {milestones_json};
        const timeline = document.querySelector('.timeline');

        milestones.forEach((milestone, index) => {{
            const div = document.createElement('div');
            div.className = 'milestone';

            const dot = document.createElement('div');
            dot.className = `milestone-dot ${{milestone.type}}`;

            const content = document.createElement('div');
            content.className = 'milestone-content';

            const year = document.createElement('div');
            year.className = `milestone-year ${{milestone.type}}`;
            year.textContent = milestone.start_year + (milestone.end_year ? `-${{milestone.end_year}}` : '-Present');

            const title = document.createElement('div');
            title.className = 'milestone-title';
            title.textContent = milestone.title;

            const org = document.createElement('div');
            org.className = 'milestone-org';
            org.textContent = milestone.organization;

            content.appendChild(year);
            content.appendChild(title);
            content.appendChild(org);

            div.appendChild(dot);
            div.appendChild(content);
            timeline.appendChild(div);

            setTimeout(() => div.classList.add('visible'), index * 150);
        }});
    </script>
</body>
</html>"""


class PNGExporter:
    """Export ASCII art or journey map as PNG image"""

    def __init__(self, content: str, font_size: int = 12, bg_color: str = '#1e1e1e',
                 fg_color: str = '#d4d4d4', width: int = None, height: int = None):
        self.content = content
        self.font_size = font_size
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.width = width
        self.height = height

    def generate(self) -> bytes:
        """Generate PNG image from ASCII content"""
        if not PIL_SUPPORT:
            raise ImportError("PNG export requires Pillow. Install with: pip install Pillow")

        # Remove ANSI color codes
        import re
        clean_content = re.sub(r'\033\[[0-9;]+m', '', self.content)

        # Split into lines
        lines = clean_content.split('\n')

        # Try to load a monospace font, fallback to default
        try:
            # Try common monospace fonts
            font = None
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                "/System/Library/Fonts/Monaco.ttf",  # macOS
                "C:\\Windows\\Fonts\\consola.ttf",  # Windows
                "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, self.font_size)
                    break

            if font is None:
                font = ImageFont.load_default()

        except Exception:
            font = ImageFont.load_default()

        # Calculate dimensions
        if font.getbbox:
            # Newer Pillow versions
            bbox = font.getbbox('X' * 100)
            char_width = (bbox[2] - bbox[0]) / 100
            char_height = bbox[3] - bbox[1]
        else:
            # Older Pillow versions
            char_width = self.font_size * 0.6
            char_height = self.font_size * 1.2

        max_line_length = max(len(line) for line in lines) if lines else 80

        img_width = self.width or int(max_line_length * char_width + 40)
        img_height = self.height or int(len(lines) * char_height + 40)

        # Create image
        image = Image.new('RGB', (img_width, img_height), color=self.bg_color)
        draw = ImageDraw.Draw(image)

        # Draw text
        y_offset = 20
        for line in lines:
            draw.text((20, y_offset), line, fill=self.fg_color, font=font)
            y_offset += char_height

        # Convert to bytes
        from io import BytesIO
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()

    def save(self, filename: str):
        """Save PNG to file"""
        png_data = self.generate()
        with open(filename, 'wb') as f:
            f.write(png_data)


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
        '--png',
        action='store_true',
        help='Generate PNG image output instead of ASCII'
    )
    parser.add_argument(
        '--html',
        action='store_true',
        help='Generate interactive HTML journey map (minimalist design)'
    )
    parser.add_argument(
        '--nlp',
        action='store_true',
        help='Use NLP-based parsing (requires spaCy)'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show career statistics dashboard'
    )
    parser.add_argument(
        '--skills',
        action='store_true',
        help='Show skills timeline and cloud'
    )
    parser.add_argument(
        '--achievements',
        action='store_true',
        help='Extract and display quantified achievements'
    )
    parser.add_argument(
        '--score',
        action='store_true',
        help='Score resume quality and get improvement suggestions'
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

    # Show statistics if requested
    if args.stats:
        stats = CareerStatistics(milestones)
        print(stats.generate_dashboard(color=not args.no_color))
        print()

    # Show skills if requested
    if args.skills:
        skills_extractor = SkillsExtractor(resume_text, milestones)
        print(skills_extractor.generate_skills_timeline(color=not args.no_color))
        print()
        print(skills_extractor.generate_skills_cloud(color=not args.no_color))
        print()

    # Show achievements if requested
    if args.achievements:
        achievement_extractor = AchievementExtractor(resume_text)
        print(achievement_extractor.generate_achievements_report(color=not args.no_color))
        print()

    # Show resume score if requested
    if args.score:
        scorer = ResumeScorer(resume_text, milestones)
        print(scorer.generate_report(color=not args.no_color))
        print()

    # Generate output
    if args.html:
        print("Generating interactive HTML...")
        html_exporter = InteractiveHTMLExporter(milestones)
        html_content = html_exporter.generate()

        output_file = args.output or "journey_map.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"{Colors.GREEN}Interactive HTML saved to: {output_file}{Colors.RESET}")
        print(f"{Colors.CYAN}Open in browser to view the minimalist journey map{Colors.RESET}")

    elif args.png:
        print("Generating PNG image...")
        # First generate ASCII map
        map_generator = ASCIIJourneyMap(
            milestones,
            width=args.width,
            style=args.style,
            color=False  # PNG doesn't support ANSI colors
        )
        ascii_content = map_generator.generate()

        # Convert to PNG
        png_exporter = PNGExporter(ascii_content, font_size=14)

        if args.output:
            png_exporter.save(args.output)
            print(f"{Colors.GREEN}PNG image saved to: {args.output}{Colors.RESET}")
        else:
            # Save to default filename
            default_name = "journey_map.png"
            png_exporter.save(default_name)
            print(f"{Colors.GREEN}PNG image saved to: {default_name}{Colors.RESET}")

    elif args.svg:
        print("Generating SVG map...")
        exporter = SVGExporter(milestones)
        output_content = exporter.generate()

        # Output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_content)
            print(f"{Colors.GREEN}Journey map saved to: {args.output}{Colors.RESET}")
        else:
            print(output_content)

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
                if not args.no_color:
                    import re
                    output_content = re.sub(r'\033\[[0-9;]+m', '', output_content)
                f.write(output_content)
            print(f"{Colors.GREEN}Journey map saved to: {args.output}{Colors.RESET}")
        else:
            print(output_content)

    return 0


if __name__ == '__main__':
    exit(main())

# 🗺️ Resume Journey Map Generator

Transform your resume or CV into a beautiful ASCII art or SVG visualization of your professional journey!

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.6+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🌟 Features

### ✨ Enhanced Features (v2.0)

- **📄 Multiple Input Formats**: Support for TXT, PDF, and DOCX files
- **🤖 NLP-Based Extraction**: Advanced parsing using spaCy for intelligent milestone detection
- **🎨 Multiple Styles**: Choose from Classic, Modern, or Minimal ASCII art styles
- **🌈 Color Support**: Beautiful ANSI color output for terminal display
- **🖼️ SVG Export**: Generate scalable vector graphics for high-quality output
- **🌐 Web Interface**: Beautiful Flask-based web UI for easy resume upload and generation
- **⚡ Fast & Efficient**: Optimized parsing and rendering algorithms

### 📋 Original Features (v1.0)

- Automatic parsing of education and work experience
- Chronological ordering of milestones
- S-shaped ASCII art journey path
- Customizable output width
- File export capabilities

## 📦 Installation

### Quick Install (Basic Features)

```bash
# Clone the repository
git clone <repository-url>
cd resume-journey-map

# Install core dependencies
pip install Flask Werkzeug
```

### Full Install (All Features)

```bash
# Install all dependencies
pip install -r requirements.txt

# Download spaCy language model for NLP features
python -m spacy download en_core_web_sm
```

### Optional: Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 🚀 Usage

### 1. Command Line Interface (Enhanced)

#### Basic Usage

```bash
# TXT file with classic style
python3 resume_journey_map_enhanced.py example_resume.txt

# PDF file with modern style and color
python3 resume_journey_map_enhanced.py resume.pdf --style modern --color

# DOCX file with SVG output
python3 resume_journey_map_enhanced.py resume.docx --svg -o journey.svg

# Use NLP parsing for better extraction
python3 resume_journey_map_enhanced.py resume.pdf --nlp --style minimal
```

#### Advanced Options

```bash
# All options
python3 resume_journey_map_enhanced.py resume.pdf \
  --style modern \
  --svg \
  -o output.svg \
  --nlp \
  -w 100
```

**Available Styles:**
- `classic` - Traditional box-drawing characters (default)
- `modern` - Clean, minimalist Unicode characters
- `minimal` - Simple ASCII characters for maximum compatibility

#### Command Line Options

```
usage: resume_journey_map_enhanced.py [-h] [-w WIDTH] [-o OUTPUT]
                                       [--style {classic,modern,minimal}]
                                       [--no-color] [--svg] [--nlp]
                                       resume_file

Generate ASCII art or SVG journey map from resume/CV

positional arguments:
  resume_file           Path to resume file (TXT, PDF, or DOCX)

optional arguments:
  -h, --help            show this help message and exit
  -w WIDTH, --width WIDTH
                        Width of ASCII art output (default: 80)
  -o OUTPUT, --output OUTPUT
                        Output file (default: print to stdout)
  --style {classic,modern,minimal}
                        ASCII art style (default: classic)
  --no-color            Disable colored output
  --svg                 Generate SVG output instead of ASCII
  --nlp                 Use NLP-based parsing (requires spaCy)
```

### 2. Web Interface

Launch the beautiful web interface:

```bash
python3 web_app.py
```

Then open your browser to: **http://localhost:5000**

#### Web Interface Features:

- 🎨 Drag & drop resume upload
- 🖼️ Live preview of journey map
- 📊 Milestone list visualization
- 💾 Download generated maps
- 📋 Copy to clipboard
- 🎯 Demo mode with example resume
- 🎨 Style and format selection
- 🤖 Optional NLP parsing

### 3. Classic CLI (Original Version)

The original simple version is still available:

```bash
python3 resume_journey_map.py example_resume.txt
python3 resume_journey_map.py resume.txt -o journey.txt -w 100
```

## 📝 Resume Format

Your resume should be a plain text, PDF, or DOCX file with the following structure:

### Required Sections

```
EDUCATION

[Degree] | [Institution] | [Start Year]-[End Year]

WORK EXPERIENCE

[Job Title] | [Company] | [Start Year]-[End Year or Present]
```

### Example Resume

```
JOHN DOE
Software Engineer
john@email.com | (555) 123-4567

EDUCATION

Bachelor of Science in Computer Science | MIT | 2012-2016
Master of Science in Artificial Intelligence | Stanford | 2016-2018

WORK EXPERIENCE

Software Engineering Intern | Google | 2015-2016
Junior Software Engineer | Microsoft | 2018-2019
Software Engineer | Amazon | 2019-2021
Senior Software Engineer | Meta | 2021-2023
Staff Engineer | OpenAI | 2023-Present
```

### Format Requirements

1. **Section Headers**: Use `EDUCATION` and `WORK EXPERIENCE` (case-insensitive)
2. **Date Format**: `YYYY-YYYY` or `YYYY-Present`
3. **Separators**: Use `|` or `-` between fields
4. **File Formats**: `.txt`, `.pdf`, `.docx`, `.doc`

## 🎨 Output Examples

### ASCII Art (Classic Style)

```
                        ═══ PROFESSIONAL JOURNEY MAP ═══

    ╭──[ 2012 ]──╮
    │ Bachelor of Science in CS │
────┤           ├───────────>

                            ╭──[ 2015 ]──╮
                            │ Software Engineering Inte │
                       ─────┤           ├───>

                                                          │
                                                          │
                                                          ╰──╮
                                                             │
                                                             ▼

                                      ╭──[ 2016 ]──╮
                                      │ Master of Science in AI   │
                  <───────────┤           ├────

         ╭──[ 2018 ]──╮
         │ Junior Software Engineer  │
    <────┤           ├─────
```

### Modern Style

```
┌──[ 2012 ]──┐
│ Bachelor of Science in CS │
├───────────→

                            ┌──[ 2015 ]──┐
                            │ Software Engineering Inte │
```

### Minimal Style

```
+--[ 2012 ]--+
| Bachelor of Science in CS |
+----->

                            +--[ 2015 ]--+
                            | Software Engineer Intern |
```

### SVG Output

The SVG output creates a beautiful vector graphic with:
- Curved connecting paths
- Color-coded nodes (education vs. work)
- Year labels and milestone descriptions
- Scalable to any size without quality loss

## 🎨 Color Support

When color is enabled, the terminal output features:
- 🔵 Blue title and headers
- 🟢 Green for work milestones
- 🟦 Cyan for education milestones
- ✨ Bold highlighting for years

Disable colors with `--no-color` flag or when piping to files.

## 🌐 Web Interface Screenshots

The web interface includes:
- Modern gradient design
- Responsive layout
- Drag & drop file upload
- Real-time generation
- Downloadable outputs
- Copy to clipboard functionality

## 📚 Examples

The repository includes multiple example resumes:

### Example Files

1. **example_resume.txt** - Comprehensive tech career (7 milestones)
2. **example_resume_simple.txt** - Data science career (4 milestones)
3. **sample_output.txt** - Pre-generated ASCII output

### Try Examples

```bash
# Classic ASCII
python3 resume_journey_map_enhanced.py example_resume.txt

# Modern style with colors
python3 resume_journey_map_enhanced.py example_resume.txt --style modern

# SVG export
python3 resume_journey_map_enhanced.py example_resume.txt --svg -o journey.svg

# Simple example
python3 resume_journey_map_enhanced.py example_resume_simple.txt --style minimal
```

## 🔧 Customization

### Modifying Map Styles

The application supports three built-in styles, but you can create custom styles by extending the `MapStyle` class:

```python
class CustomStyle(MapStyle):
    name = "custom"

    def get_box_chars(self):
        return {
            'top_left': '╔',
            'top_right': '╗',
            # ... define your characters
        }
```

### Adjusting Path Layout

Modify `nodes_per_row` in the `_generate_s_path()` method to change how many milestones appear per row.

### SVG Customization

Edit the `SVGExporter` class to customize:
- Colors
- Font sizes
- Node sizes
- Path styles
- Dimensions

## 🧪 Testing

Run the included tests:

```bash
# Test with example resumes
python3 resume_journey_map_enhanced.py example_resume.txt
python3 resume_journey_map_enhanced.py example_resume_simple.txt

# Test all styles
python3 resume_journey_map_enhanced.py example_resume.txt --style classic
python3 resume_journey_map_enhanced.py example_resume.txt --style modern
python3 resume_journey_map_enhanced.py example_resume.txt --style minimal

# Test SVG export
python3 resume_journey_map_enhanced.py example_resume.txt --svg -o test.svg

# Test web interface
python3 web_app.py
# Visit http://localhost:5000 and use demo button
```

## 🐛 Troubleshooting

### "No milestones found in resume"

**Solution:**
- Ensure `EDUCATION` and `WORK EXPERIENCE` section headers exist
- Check date format: `YYYY-YYYY` or `YYYY-Present`
- Verify separator usage: `|` between fields

### PDF/DOCX Import Errors

**Solution:**
```bash
pip install pdfplumber python-docx
```

### NLP Features Not Working

**Solution:**
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

### Web Interface Not Starting

**Solution:**
```bash
pip install Flask Werkzeug
# Check port 5000 is not in use
# Try different port: python3 web_app.py --port 8080
```

### Color Output Issues

**Solution:**
- Use `--no-color` flag for plain output
- Some terminals don't support ANSI colors
- Colors are automatically disabled when piping to files

### Character Encoding Problems

**Solution:**
- Save resume as UTF-8 encoding
- Use modern terminal with Unicode support
- Try `minimal` style for ASCII-only output

## 🚀 Advanced Usage

### Batch Processing

```bash
# Process multiple resumes
for file in resumes/*.txt; do
  python3 resume_journey_map_enhanced.py "$file" \
    --svg -o "output/$(basename "$file" .txt).svg"
done
```

### Integration with Other Tools

```bash
# Generate and view SVG
python3 resume_journey_map_enhanced.py resume.pdf --svg -o journey.svg
open journey.svg  # macOS
xdg-open journey.svg  # Linux

# Generate and copy to clipboard
python3 resume_journey_map_enhanced.py resume.txt | pbcopy  # macOS
python3 resume_journey_map_enhanced.py resume.txt | xclip   # Linux
```

### Using as a Library

```python
from resume_journey_map_enhanced import (
    DocumentLoader, ResumeParser, ASCIIJourneyMap, SVGExporter
)

# Load resume
text = DocumentLoader.load('resume.pdf')

# Parse milestones
parser = ResumeParser(text)
milestones = parser.parse()

# Generate ASCII map
ascii_gen = ASCIIJourneyMap(milestones, style='modern', color=True)
ascii_output = ascii_gen.generate()

# Generate SVG
svg_gen = SVGExporter(milestones, width=1000, height=800)
svg_output = svg_gen.generate()
```

## 🤝 Contributing

Contributions are welcome! Here are some ideas:

### Enhancement Ideas

- 🔍 Better NLP parsing algorithms
- 🌍 Multi-language support
- 📊 Timeline/Gantt chart style maps
- 🎨 More ASCII art styles
- 📱 Mobile-responsive web interface
- 🔗 LinkedIn API integration
- 📈 Career statistics and insights
- 🎯 Skill highlighting
- 📅 Interactive timeline
- 🌙 Dark mode for web interface

### Code Quality

- ✅ Add unit tests
- 📖 Improve documentation
- 🔍 Add type hints
- ⚡ Performance optimizations
- 🐛 Bug fixes

## 📄 License

This project is open source under the MIT License. Feel free to use, modify, and distribute.

## 👨‍💻 Author

Created with ❤️ for visualizing professional journeys

## 🙏 Acknowledgments

- **spaCy** - Advanced NLP library
- **pdfplumber** - PDF text extraction
- **python-docx** - DOCX file parsing
- **Flask** - Web framework
- **Unicode Consortium** - Box-drawing characters

## 📊 Version History

### Version 2.0 (Enhanced) - Current
- ✅ PDF and DOCX support
- ✅ NLP-based extraction
- ✅ Multiple map styles
- ✅ Color terminal output
- ✅ SVG export
- ✅ Web interface
- ✅ Improved parsing

### Version 1.0 (Original)
- ✅ Basic TXT parsing
- ✅ ASCII art generation
- ✅ S-shaped path
- ✅ CLI interface

---

## 🎯 Quick Start Commands

```bash
# Install
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Generate ASCII (classic style)
python3 resume_journey_map_enhanced.py resume.txt

# Generate SVG
python3 resume_journey_map_enhanced.py resume.pdf --svg -o journey.svg

# Start web interface
python3 web_app.py

# Try demo
python3 resume_journey_map_enhanced.py example_resume.txt --style modern
```

**Enjoy mapping your career journey!** 🗺️✨

---

For issues, questions, or suggestions, please open an issue on GitHub.

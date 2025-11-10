# Resume Journey Map Generator

Transform your resume or CV into a beautiful ASCII art visualization of your professional journey!

## Overview

This application parses a resume/CV and creates an ASCII art "map" showing your career progression through time. The map features an S-shaped path with nodes representing key milestones like education and work experience.

## Features

- **Automatic Parsing**: Extracts education and work experience from structured resume text
- **Chronological Ordering**: Automatically sorts milestones by date
- **ASCII Art Visualization**: Creates a visually appealing S-shaped journey path
- **Customizable Width**: Adjust output width to fit your display
- **File Export**: Save the generated map to a file

## Requirements

- Python 3.6 or higher
- No external dependencies required (uses only Python standard library)

## Installation

Simply clone or download this repository:

```bash
git clone <repository-url>
cd resume-journey-map
```

## Usage

### Basic Usage

```bash
python3 resume_journey_map.py example_resume.txt
```

### Save to File

```bash
python3 resume_journey_map.py example_resume.txt -o my_journey.txt
```

### Custom Width

```bash
python3 resume_journey_map.py example_resume.txt -w 100
```

### Help

```bash
python3 resume_journey_map.py --help
```

## Resume Format

Your resume should be a plain text file with the following structure:

```
EDUCATION

[Degree] | [Institution] | [Start Year]-[End Year]

WORK EXPERIENCE

[Job Title] | [Company] | [Start Year]-[End Year]
```

### Example Resume

```
JOHN DOE
Software Engineer

EDUCATION

Bachelor of Science in Computer Science | MIT | 2012-2016
Master of Science in AI | Stanford | 2016-2018

WORK EXPERIENCE

Software Engineering Intern | Google | 2015-2016
Junior Software Engineer | Microsoft | 2018-2019
Senior Software Engineer | Meta | 2021-Present
```

### Format Requirements

1. **Section Headers**: Use `EDUCATION` and `WORK EXPERIENCE` (or `EXPERIENCE`) headers
2. **Date Format**: Use `YYYY-YYYY` or `YYYY-Present` for date ranges
3. **Separators**: Use `|` or `-` to separate title, organization, and dates
4. **Case Insensitive**: Section headers are case-insensitive

## Example Output

```
                        ═══ PROFESSIONAL JOURNEY MAP ═══

    ╭──[ 2012 ]──╮
    │ Bachelor of Science in Co │
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

## How It Works

1. **Parsing**: The `ResumeParser` class reads your resume and extracts milestones using regex patterns
2. **Sorting**: Milestones are automatically sorted chronologically by date
3. **Map Generation**: The `ASCIIJourneyMap` class creates an S-shaped path
4. **Node Placement**: Each milestone is placed as a node along the path with year and description

## Customization

You can customize the ASCII art by modifying the `ASCIIJourneyMap` class:

- **Path characters**: Change the box drawing characters in the `_draw_*` methods
- **Nodes per row**: Adjust `nodes_per_row` in `_generate_s_path()`
- **Node style**: Modify the box design in drawing methods
- **Spacing**: Adjust indentation and spacing values

## Advanced Features

### Parsing Different Formats

The parser uses flexible regex patterns and can handle various formats:

```
# Format 1 (recommended)
Software Engineer | Google | 2020-2023

# Format 2
Software Engineer - Google - 2020-2023

# Format 3
Software Engineer | Google 2020-2023
```

### Labels

- **Education**: Shows degree name
- **Work**: Shows "Title @ Company"
- Labels are automatically truncated to fit the node width

## Examples

Two example resumes are provided:

1. **example_resume.txt**: A comprehensive tech career journey
2. **example_resume_simple.txt**: A simpler data science career path

Try them out:

```bash
python3 resume_journey_map.py example_resume.txt
python3 resume_journey_map.py example_resume_simple.txt
```

## Troubleshooting

### "No milestones found in resume"

This means the parser couldn't find properly formatted milestones. Make sure:

- You have `EDUCATION` and `WORK EXPERIENCE` section headers
- Dates are in `YYYY-YYYY` or `YYYY-Present` format
- Lines contain both title/degree and organization

### Truncated Labels

If your milestone descriptions are too long, they'll be truncated. You can:

- Use shorter organization names
- Increase the width with `-w` flag
- Modify the label truncation length in the code

### Character Encoding Issues

Make sure your resume file is saved as UTF-8 encoding, especially if it contains special characters.

## Contributing

Contributions are welcome! Some ideas for enhancements:

- Support for PDF and DOCX resume parsing
- More sophisticated NLP-based parsing
- Multiple map styles (linear, circular, tree-based)
- Color output support (using ANSI codes)
- Web interface
- Export to SVG or other formats

## License

This project is open source. Feel free to use, modify, and distribute.

## Author

Created with ❤️ for visualizing professional journeys

---

**Enjoy mapping your career journey!** 🗺️

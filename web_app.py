#!/usr/bin/env python3
"""
Resume Journey Map - Web Interface
Flask-based web application for generating journey maps from resumes
"""

from flask import Flask, render_template, request, send_file, jsonify
import os
import tempfile
from pathlib import Path
from werkzeug.utils import secure_filename

# Import from enhanced version
from resume_journey_map_enhanced import (
    DocumentLoader, ResumeParser, NLPResumeParser,
    ASCIIJourneyMap, SVGExporter, Colors
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and generate journey map"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Supported: TXT, PDF, DOCX'}), 400

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Get parameters
        style = request.form.get('style', 'classic')
        output_format = request.form.get('format', 'ascii')
        use_nlp = request.form.get('nlp', 'false') == 'true'

        # Load and parse resume
        resume_text = DocumentLoader.load(filepath)

        if use_nlp:
            parser = NLPResumeParser(resume_text)
        else:
            parser = ResumeParser(resume_text)

        milestones = parser.parse()

        if not milestones:
            return jsonify({
                'error': 'No milestones found in resume. Make sure it has EDUCATION and EXPERIENCE sections.'
            }), 400

        # Generate output
        if output_format == 'svg':
            exporter = SVGExporter(milestones, width=1000, height=800)
            output = exporter.generate()
            content_type = 'image/svg+xml'
        else:
            # Disable colors for web output
            Colors.disable()
            map_generator = ASCIIJourneyMap(milestones, width=80, style=style, color=False)
            output = map_generator.generate()
            content_type = 'text/plain'

        # Clean up uploaded file
        os.remove(filepath)

        return jsonify({
            'success': True,
            'output': output,
            'content_type': content_type,
            'milestone_count': len(milestones),
            'milestones': [
                {
                    'year': m.date.year,
                    'title': m.title,
                    'organization': m.organization,
                    'type': m.milestone_type
                }
                for m in milestones
            ]
        })

    except Exception as e:
        # Clean up on error
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500


@app.route('/demo')
def demo():
    """Demo with example resume"""
    example_resume = """
JANE DOE
Software Engineer

EDUCATION

Bachelor of Science in Computer Science | MIT | 2012-2016
Master of Science in AI | Stanford | 2016-2018

WORK EXPERIENCE

Software Engineering Intern | Google | 2015-2016
Junior Software Engineer | Microsoft | 2018-2019
Software Engineer | Amazon | 2019-2021
Senior Software Engineer | Meta | 2021-2023
Staff Engineer | OpenAI | 2023-Present
    """

    parser = ResumeParser(example_resume)
    milestones = parser.parse()

    Colors.disable()
    map_generator = ASCIIJourneyMap(milestones, width=80, style='classic', color=False)
    output = map_generator.generate()

    return jsonify({
        'success': True,
        'output': output,
        'content_type': 'text/plain',
        'milestone_count': len(milestones)
    })


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)

    print("Starting Resume Journey Map Web Server...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

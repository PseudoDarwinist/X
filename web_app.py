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

# Import from professional journey map
from professional_journey_map import ResumeParser, ProfessionalJourneyMap

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

ALLOWED_EXTENSIONS = {'txt'}


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
        return jsonify({'error': 'Invalid file type. Only TXT files are supported.'}), 400

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Load and parse resume
        with open(filepath, 'r', encoding='utf-8') as f:
            resume_text = f.read()

        parser = ResumeParser(resume_text)
        milestones = parser.parse()

        if not milestones:
            return jsonify({
                'error': 'No milestones found in resume. Make sure it has career history with dates.'
            }), 400

        # Generate professional visual journey map
        journey_map = ProfessionalJourneyMap(milestones, width=1400, height=800)

        # Get format preference
        output_format = request.form.get('format', 'html')

        if output_format == 'svg':
            output = journey_map.generate_svg()
            content_type = 'image/svg+xml'
        else:
            output = journey_map.generate_html()
            content_type = 'text/html'

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
    """Demo with Chetan's resume"""
    # Load the example resume
    with open('chetan_resume.txt', 'r', encoding='utf-8') as f:
        example_resume = f.read()

    parser = ResumeParser(example_resume)
    milestones = parser.parse()

    journey_map = ProfessionalJourneyMap(milestones, width=1400, height=800)
    output = journey_map.generate_html()

    return jsonify({
        'success': True,
        'output': output,
        'content_type': 'text/html',
        'milestone_count': len(milestones)
    })


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)

    print("Starting Resume Journey Map Web Server...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify, send_file
from utils.pdf_handler import PDFHandler
from utils.docx_handler import DocxHandler
from utils.nlp_processor import NLPProcessor
from utils.resume_formatter import ResumeFormatter
import os
from config import Config

app = Flask(__name__)

# Configure upload and output directories
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'outputs')

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Initialize resume formatter
resume_formatter = ResumeFormatter(OUTPUT_FOLDER)

@app.route('/')
def index():
    return "Resume Parser and Formatter API is running!"

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save the file
    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)
    
    # Process the file based on its extension
    if filename.lower().endswith('.pdf'):
        handler = PDFHandler(filename)
    elif filename.lower().endswith('.docx'):
        handler = DocxHandler(filename)
    else:
        return jsonify({'error': 'Unsupported file format'}), 400
    
    # Extract text
    text = handler.extract_text()
    
    # Process with NLP
    nlp_processor = NLPProcessor()
    processed_data = nlp_processor.process_resume(text)
    
    return jsonify({
        'message': 'File processed successfully',
        'filename': file.filename,
        'data': processed_data
    })

@app.route('/format', methods=['POST'])
def format_resume():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Get the desired output format from request
    output_format = request.args.get('format', 'pdf')  # Default to PDF
    
    # Create a formatted version of the resume
    formatted_resume = {
        "header": {
            "name": data.get("PERSON", [""])[0],
            "location": data.get("LOC", [""])[0],
            "contact": {
                "email": data.get("EMAIL", [""])[0],
                "phone": data.get("PHONE", [""])[0],
                "linkedin": data.get("LINKEDIN", [""])[0]
            }
        },
        "experience": [
            {
                "title": exp.get("title", ""),
                "company": exp.get("company", ""),
                "duration": exp.get("duration", ""),
                "description": exp.get("description", "")
            }
            for exp in data.get("EXPERIENCE", [])
        ],
        "education": [
            {
                "degree": edu.get("degree", ""),
                "institution": edu.get("institution", ""),
                "year": edu.get("year", "")
            }
            for edu in data.get("EDUCATION", [])
        ],
        "skills": data.get("SKILLS", []),
        "certifications": data.get("CERTIFICATIONS", [])
    }
    
    # Generate the formatted resume
    output_path = resume_formatter.format_resume(formatted_resume, output_format)
    
    # Send the file back to the client
    if output_format == 'pdf':
        return send_file(output_path, as_attachment=True, mimetype='application/pdf')
    else:
        return send_file(output_path, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

@app.route('/status/<filename>', methods=['GET'])
def get_status(filename):
    # Check if the file exists in uploads
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(upload_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Check if the formatted version exists
    formatted_pdf_path = os.path.join(OUTPUT_FOLDER, f"formatted_{filename}.pdf")
    formatted_docx_path = os.path.join(OUTPUT_FOLDER, f"formatted_{filename}.docx")
    
    pdf_exists = os.path.exists(formatted_pdf_path)
    docx_exists = os.path.exists(formatted_docx_path)
    
    return jsonify({
        'filename': filename,
        'uploaded': True,
        'formatted_pdf': pdf_exists,
        'formatted_docx': docx_exists,
        'output_paths': {
            'pdf': formatted_pdf_path if pdf_exists else None,
            'docx': formatted_docx_path if docx_exists else None
        }
    })

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad Request',
        'message': str(error)
    }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': str(error)
    }), 404

@app.errorhandler(Exception)
def handle_error(error):
    return jsonify({
        'error': 'Internal Server Error',
        'message': str(error)
    }), 500

if __name__ == '__main__':
    app.run(debug=True)
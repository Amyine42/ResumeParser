from flask import Flask, request, jsonify
from utils.pdf_handler import PDFHandler
from utils.docx_handler import DocxHandler
from utils.nlp_processor import NLPProcessor
import os
from config import Config

app = Flask(__name__)

# Configure upload and output directories
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'outputs')

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

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

if __name__ == '__main__':
    app.run(debug=True)
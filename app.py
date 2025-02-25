import os
import sys
import json
from flask import Flask, request, render_template
from pypdf import PdfReader
from docx import Document  # Import docx support
from resumeparser import ats_extractor

sys.path.insert(0, os.path.abspath(os.getcwd()))

UPLOAD_PATH = os.path.join(os.getcwd(), "uploads")  # Use absolute path
if not os.path.exists(UPLOAD_PATH):
    os.makedirs(UPLOAD_PATH)  # Ensure folder exists

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', data={})  # Ensure data is initialized

@app.route("/process", methods=["POST"])
def ats():
    if 'pdf_doc' not in request.files:
        return "No file uploaded!"

    doc = request.files['pdf_doc']
    if doc.filename == "":
        return "No selected file!"

    file_ext = doc.filename.split('.')[-1].lower()
    if file_ext not in ['pdf', 'docx']:
        return "Invalid file format. Please upload a PDF or Word document."

    doc_path = os.path.join(UPLOAD_PATH, f"file.{file_ext}")
    
    try:
        doc.save(doc_path)  # Save file securely
    except Exception as e:
        return f"Error saving file: {str(e)}"

    resume_text = _read_file_from_path(doc_path, file_ext)
    extracted_data = ats_extractor(resume_text)

    return render_template('index.html', data=extracted_data)  # Send structured data to frontend

def _read_file_from_path(path, file_ext):
    """Reads text from a PDF or DOCX file."""
    text = ""
    if os.path.exists(path):
        if file_ext == "pdf":
            reader = PdfReader(path)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif file_ext == "docx":
            doc = Document(path)
            text = " ".join([para.text for para in doc.paragraphs])
    else:
        return "Error: File not found!"
    
    return text

if __name__ == "__main__":
    app.run(port=8000, debug=True)

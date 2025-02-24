import os
import sys
import json
from flask import Flask, request, render_template
from pypdf import PdfReader
from resumeparser import ats_extractor

sys.path.insert(0, os.path.abspath(os.getcwd()))

UPLOAD_PATH = r"__DATA__"
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', data={})  # Ensure data is initialized

@app.route("/process", methods=["POST"])
def ats():
    doc = request.files['pdf_doc']
    doc_path = os.path.join(UPLOAD_PATH, "file.pdf")
    doc.save(doc_path)

    resume_text = _read_file_from_path(doc_path)
    extracted_data = ats_extractor(resume_text)

    return render_template('index.html', data=extracted_data)  # Send structured data to frontend

def _read_file_from_path(path):
    reader = PdfReader(path)
    text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

if __name__ == "__main__":
    app.run(port=8000, debug=True)

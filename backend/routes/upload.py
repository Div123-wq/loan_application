import os
import json
import uuid
import tempfile
from flask import Blueprint, request, jsonify
from services.ocr_service import extract_text_from_file

upload_bp = Blueprint('upload', __name__)

# In-memory document store (session-based)
document_store = {}


@upload_bp.route('/api/upload', methods=['POST'])
def upload_document():
    """Upload and extract text from a loan document (PDF or image)."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided. Send a file with key 'file'."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected."}), 400

    allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.webp', '.tiff', '.bmp'}
    _, ext = os.path.splitext(file.filename.lower())
    if ext not in allowed_extensions:
        return jsonify({"error": f"Unsupported file type: {ext}. Allowed: PDF, PNG, JPG, JPEG, WEBP, TIFF, BMP"}), 400

    try:
        file_bytes = file.read()
        extracted = extract_text_from_file(file_bytes, file.filename)

        doc_id = str(uuid.uuid4())
        document_store[doc_id] = {
            "doc_id": doc_id,
            "filename": file.filename,
            "text": extracted["text"],
            "is_image": extracted["is_image"],
            "image_b64": extracted.get("image_b64"),
            "file_size": len(file_bytes),
            "char_count": len(extracted["text"]),
        }

        return jsonify({
            "success": True,
            "doc_id": doc_id,
            "filename": file.filename,
            "extracted_chars": len(extracted["text"]),
            "is_image": extracted["is_image"],
            "preview": extracted["text"][:300] + "..." if len(extracted["text"]) > 300 else extracted["text"],
            "message": "Document uploaded and text extracted successfully."
        })

    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500


@upload_bp.route('/api/document/<doc_id>', methods=['GET'])
def get_document(doc_id):
    """Retrieve stored document info."""
    doc = document_store.get(doc_id)
    if not doc:
        return jsonify({"error": "Document not found. Please upload again."}), 404
    return jsonify({
        "doc_id": doc_id,
        "filename": doc["filename"],
        "char_count": doc["char_count"],
        "is_image": doc["is_image"],
    })


def get_document_text(doc_id: str) -> str:
    """Helper to retrieve document text from store."""
    doc = document_store.get(doc_id)
    if not doc:
        raise ValueError(f"Document {doc_id} not found.")
    return doc.get("text", "")

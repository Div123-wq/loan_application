import base64
import io
from PIL import Image

# Robust PDF parser selection with pure-python fallback
has_fitz = False
try:
    import fitz  # PyMuPDF
    has_fitz = True
except Exception:
    pass

has_pypdf = False
try:
    import pypdf
    has_pypdf = True
except Exception:
    pass


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF file using the best available parser."""
    if has_fitz:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            full_text = []
            for page_num, page in enumerate(doc):
                text = page.get_text("text")
                full_text.append(f"--- Page {page_num + 1} ---\n{text}")
            doc.close()
            return "\n".join(full_text)
        except Exception:
            pass
            
    # Fallback to pure Python pypdf
    if has_pypdf:
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            full_text = []
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                full_text.append(f"--- Page {page_num + 1} ---\n{text}")
            return "\n".join(full_text)
        except Exception as e:
            return f"Error extracting with pure-python parser: {str(e)}"
            
    # Absolute basic text fallback
    return file_bytes.decode("utf-8", errors="ignore")


def extract_text_from_image(file_bytes: bytes) -> str:
    """Convert image to base64 for vision analysis."""
    img = Image.open(io.BytesIO(file_bytes))
    # Convert to RGB if needed
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=90)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def extract_text_from_file(file_bytes: bytes, filename: str) -> dict:
    """
    Route extraction based on file type.
    Returns {"text": str, "is_image": bool, "image_b64": str|None}
    """
    fname = filename.lower()
    if fname.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
        return {"text": text, "is_image": False, "image_b64": None}
    elif fname.endswith((".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp")):
        image_b64 = extract_text_from_image(file_bytes)
        return {"text": "", "is_image": True, "image_b64": image_b64}
    else:
        # Try PDF first, then treat as text
        try:
            text = extract_text_from_pdf(file_bytes)
            return {"text": text, "is_image": False, "image_b64": None}
        except Exception:
            text = file_bytes.decode("utf-8", errors="ignore")
            return {"text": text, "is_image": False, "image_b64": None}


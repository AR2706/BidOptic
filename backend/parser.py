# parser.py
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

def extract_text_from_pdf(pdf_path):
    """Converts PDF to images, then runs OCR."""
    pages = convert_from_path(pdf_path)
    full_text = ""
    
    for page in pages:
        text = pytesseract.image_to_string(page)
        full_text += text + "\n"
        
    return full_text

def extract_text_from_image(image_path):
    """Runs OCR on a scanned photograph/jpeg."""
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)
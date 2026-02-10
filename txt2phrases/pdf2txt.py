# pdf2txt.py
import os
from pathlib import Path
from PyPDF2 import PdfReader

def convert_pdf_to_text(pdf_path, output_folder):
    """
    Convert a single PDF file to a TXT file and save it.
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)
        
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        txt_path = os.path.join(output_folder, base_name + ".txt")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        return txt_path
    except Exception as e:
        print(f"[ERROR] Failed to process {pdf_path}: {e}")
        return None


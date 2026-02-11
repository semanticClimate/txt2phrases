# pdf2txt.py
import os
from pathlib import Path
from PyPDF2 import PdfReader

def convert_pdf_to_text(pdf_path, output_folder):
    """
    Convert a single PDF file to a TXT file and save it.
    """
    try:
        from pathlib import Path
        
        # Convert to Path if needed and ensure it's a string for PdfReader
        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            print(f"[ERROR] PDF file not found: {pdf_path}")
            return None
        
        reader = PdfReader(str(pdf_path_obj))
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        # Ensure output folder exists
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        base_name = pdf_path_obj.stem
        txt_path = Path(output_path, f"{base_name}.txt")

        txt_path.write_text(text, encoding="utf-8")
        return str(txt_path)
    except Exception as e:
        print(f"[ERROR] Failed to process {pdf_path}: {e}")
        return None


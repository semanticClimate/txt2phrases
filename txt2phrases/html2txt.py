import os
from bs4 import BeautifulSoup

def convert_html_to_text(html_path, output_folder):
    """
    Convert a single HTML file to plain text and save it.
    """
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text(separator="\n", strip=True)

        base_name = os.path.splitext(os.path.basename(html_path))[0]
        txt_path = os.path.join(output_folder, base_name + ".txt")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        return txt_path
    except Exception as e:
        print(f"[ERROR] Failed to process {html_path}: {e}")
        return None




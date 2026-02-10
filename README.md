# txt2phrases

`txt2phrases` is a Python library and CLI tool designed for processing and analyzing text data.  
It provides a streamlined pipeline for converting documents (HTML, PDF) into plain text, extracting keywords using AI models, and classifying keywords into specific and general categories using TF-IDF.

---

## ✨ Features

### 1. **PDF to Text Conversion**
- Extract plain text from PDF files for further processing.

### 2. **HTML to Text Conversion**
- Convert HTML documents into clean, plain text.

### 3. **AI-Powered Keyword Extraction**
- Use advanced NLP models (e.g., Hugging Face Transformers) to extract and rank the most important keywords from text files.

### 4. **Automated Pipeline**
- Run the entire pipeline (PDF/HTML → TXT → Keywords) with a single command.

### 5. **Batch Processing**
- Process single files or entire directories efficiently.

### 6. **Configurable Parameters**
- Customize thresholds, batch sizes, and output formats to suit your needs.

---

## 🧩 Installation

Install `txt2phrases` directly from PyPI:

```bash
pip install txt2phrases
```

---

## 🚀 Quick Start

```bash
# Convert PDF to text
txt2phrases pdf2txt -i document.pdf -o output_folder

# Convert HTML to text
txt2phrases html2txt -i webpage.html -o output_folder

# Extract keywords from text files
txt2phrases keyphrases -i text_files/ -o keywords/ -n 500

# Run complete pipeline
txt2phrases auto -i pygetpapers_output/ -o results/ -n 100
```

---

## 🐍 Python API

```python
from txt2phrases import (
    convert_pdf_to_text,
    convert_html_to_text, 
    KeywordExtraction,
    classify_keywords_split_files
)

# Convert PDF to text
txt_path = convert_pdf_to_text("document.pdf", "output_folder")

# Extract keywords
extractor = KeywordExtraction(
    input_path="text_files/",
    output_folder="keywords/",
    top_n=1000
)
extractor.extract()
```
---

## 🧠 CLI Commands

### 📄 `pdf2txt`
Convert PDF files to text format.

```bash
txt2phrases pdf2txt -i input.pdf -o output_folder
txt2phrases pdf2txt -i pdfs_directory/ -o text_output/
```

---

### 🌐 `html2txt`
Convert HTML files to clean text format.

```bash
txt2phrases html2txt -i webpage.html -o output_folder
txt2phrases html2txt -i html_directory/ -o text_output/
```

---

### 🔑 `keyphrases`
Extract keyphrases from text files using advanced NLP models.

```bash
txt2phrases keyphrases -i text.txt -o keywords/ -n 500
txt2phrases keyphrases -i text_directory/ -o keywords/ -n 1000
```

---

### ⚙️ `auto`
Complete processing pipeline for PyGetPapers output or PDF directories.

```bash
txt2phrases auto -i pygetpapers_output/ -o results/ -n 200
txt2phrases auto -i pdf_collection/ -o results/ -n 100
```

---

## 🔍 Advanced Features
---

### 2. **Complete Research Pipeline**

```bash
# Download papers with PyGetPapers
pygetpapers -q "machine learning" -o papers/ -k 100

# Process and analyze  
txt2phrases auto -i papers/ -o analysis/ -n 200

# Classify results
python -c "
from txt2phrases import classify_keywords_split_files
classify_keywords_split_files('analysis/', 'classified/', threshold=0.7)
"
```

---

## 📦 Output Formats

- **Text Conversion:** `.txt` files with extracted text  
- **Keyword Extraction:** `.csv` files containing keyword and count columns  

---

## 🧱 Requirements

To use `txt2phrases`, ensure you have the following installed:

- **Python 3.8+**
- **Dependencies:**
  - `beautifulsoup4>=4.9.0`: For HTML parsing  
  - `pandas>=1.0.0`: For data manipulation and CSV export  
  - `tqdm>=4.50.0`: For progress bars during batch processing  
  - `transformers>=4.0.0`: For AI-powered keyword extraction  
  - `scikit-learn>=1.0.0`: For TF-IDF-based keyword classification  
  - `PyPDF2>=2.0.0`: For PDF text extraction
  - `torch>=1.7.0`: For running NLP models  

**Important:** Install dependencies before running tests or using the library:

```bash
pip install -r requirements.txt
```

Or install the package with dependencies:

```bash
pip install -e .
```

---

## 📚 Documentation

For full documentation and examples, visit the [GitHub repository](https://github.com/semanticClimate/txt2phrases).

---

## 📄 License

This project is licensed under the **MIT License** — see the `LICENSE` file for details.


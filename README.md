# txt2phrases

`txt2phrases` is a Python library and CLI tool designed for processing and analyzing text data.  
It provides a streamlined pipeline for converting documents (HTML, XML, PDF) into plain text, extracting keywords using AI models, merging and classifying keywords into specific and general categories using TF-IDF.

---

## ✨ Features

### 1. **PDF to Text Conversion**
- Extract plain text from PDF files for further processing.

### 2. **HTML to Text Conversion**
- Convert HTML documents into clean, plain text.

### 3. **XML to Text Conversion**
- Convert scientific full-text XML (JATS format, e.g. from 'pygetpapers' `-x` option) into clean, plain text.
- Automatically strips references/bibliography and acknowledgements by default, so downstream keyword extraction isn't polluted with citation text.

### 4. **AI-Powered Keyword Extraction**
- Use advanced NLP models (e.g., Hugging Face Transformers) to extract and rank the most important keywords from text files.
- Automatically filters out journal names, licence/boilerplate text, and other non-content noise using a built-in stopword list (extendable with your own).
- Merges casing variants of the same keyword (e.g. `"Climate anxiety"` and `"climate anxiety"`) so they aren't counted as two separate terms.
- Optional JSON output alongside CSV for each processed file.

### 5. **Keyword Merging**
- Combine keyword CSVs from multiple documents into a single ranked CSV, with counts aggregated across sources.

### 6. **Keyword Classification**
- Classify keywords as general (shared across documents) or specific (unique to one document) using TF-IDF.
- Casing variants of the same keyword across different documents (e.g. `"Age"` vs `"age"`) are merged before classifying, so they aren't miscounted as separate, falsely "document-specific" keywords.

### 7. **Automated Pipeline**
- Run the entire pipeline (PDF/HTML → TXT → Keywords) with a single command.

### 8. **Batch Processing**
- Process single files or entire directories efficiently.

### 9. **Configurable Parameters**
- Customize thresholds, stopwords, batch sizes, and output formats to suit your needs.

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

# Convert XML to text
txt2phrases xml2txt -i papers_xml/ -o output_folder

# Extract keywords from text files
txt2phrases keyphrases -i text_files/ -o keywords/ -n 500

# Merge keyword CSVs from multiple documents into one
txt2phrases merge -i keywords/ -o merged.csv

# Classify keywords as general or document-specific
txt2phrases classify -i keywords/ -o classified/

# Run complete pipeline
txt2phrases auto -i pygetpapers_output/ -o results/ -n 100
```

---

## 🐍 Python API

```python
from txt2phrases import (
    convert_pdf_to_text,
    convert_html_to_text,
    convert_xml_to_text,
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

# Classify keywords as general/specific
classify_keywords_split_files("keywords/", "classified/", threshold=0.7)
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

### 📰 `xml2txt`
Convert scientific full-text XML (JATS format) to clean text format.

```bash
txt2phrases xml2txt -i fulltext.xml -o output_folder
txt2phrases xml2txt -i papers_xml/ -o text_output/
```

**Options:**

| Flag | Description |
|---|---|
| `--keep-references` | Keep the references/bibliography section (`<back>`/`<ref-list>` in JATS XML) instead of stripping it by default. |

By default, the references/bibliography and acknowledgements sections (JATS `<back>`) are stripped before extracting text, since these are a heavy source of journal-name and author-name noise for downstream keyword extraction:

```bash
# References and acknowledgements stripped by default
txt2phrases xml2txt -i fulltext.xml -o output_folder

# Keep everything, including references
txt2phrases xml2txt -i fulltext.xml -o output_folder --keep-references
```

When given a directory, `xml2txt` searches recursively — this matters for pygetpapers-style output, where every paper's XML is named `fulltext.xml` but nested in its own subfolder (`papers_xml/PMC12345/fulltext.xml`). Each output is automatically renamed after its parent folder (`PMC12345.txt`) so multiple papers don't collide on the generic `fulltext.txt` name. A normally-named file (e.g. `paper1.xml`) keeps its own name unchanged.

```bash
# papers_xml/PMC11111111/fulltext.xml, papers_xml/PMC22222222/fulltext.xml, ...
# -> text_output/PMC11111111.txt, text_output/PMC22222222.txt, ...
txt2phrases xml2txt -i papers_xml/ -o text_output/
```

---

### 🔑 `keyphrases`
Extract keyphrases from text files using advanced NLP models.

```bash
txt2phrases keyphrases -i text.txt -o keywords/ -n 500
txt2phrases keyphrases -i text_directory/ -o keywords/ -n 1000
```

**Options:**

| Flag | Description |
|---|---|
| `-n, --top_n` | Number of top keywords to keep per file (default: 1000) |
| `--stopwords PATH` | Path to a custom stopwords file (one term per line, `#` for comments). Merged with the built-in default list. |
| `--no-default-stopwords` | Disable the built-in stopword list; only terms from `--stopwords` (if given) are filtered. |
| `--case-sensitive` | Treat casing variants (e.g. `"Climate anxiety"` vs `"climate anxiety"`) as distinct keywords instead of merging them. Default: case-insensitive. |
| `--json` | Also write a `<name>_keywords.json` file alongside the CSV for each input file. |

```bash
# Add your own stopwords on top of the defaults
txt2phrases keyphrases -i text/ -o keywords/ --stopwords my_stopwords.txt

# Disable the built-in list entirely, use only your own
txt2phrases keyphrases -i text/ -o keywords/ --stopwords my_stopwords.txt --no-default-stopwords

# Also write JSON alongside CSV
txt2phrases keyphrases -i text/ -o keywords/ --json
```

Example `my_stopwords.txt`:

```
# lines starting with # are ignored
Outcome Risk
Sample characteristics
```

**JSON output format** (`<name>_keywords.json`):

```json
{
  "document": "paper1",
  "generated_at": "2026-09-23T10:11:51.822204+00:00",
  "n_keyphrases": 394,
  "keyphrases": [
    {"keyword": "climate anxiety", "count": 76, "rank": 1},
    {"keyword": "climate change", "count": 25, "rank": 2}
  ]
}
```

---

### 🔀 `merge`
Merge multiple keyword CSV files (as produced by `keyphrases`) into a single, aggregated CSV. Counts for the same keyword across files are summed.

```bash
# Merge all CSVs in a directory
txt2phrases merge -i keywords/ -o merged.csv

# Merge specific files
txt2phrases merge -i file1_keywords.csv file2_keywords.csv -o merged.csv

# Merge with top 100 keywords, sorted alphabetically
txt2phrases merge -i keywords/ -o top100.csv --top-n 100 --sort-by keyword
```

**Options:**

| Flag | Description |
|---|---|
| `-n, --top-n` | Keep only the top N keywords after merging |
| `--sort-by` | Sort by `count` (default, descending) or `keyword` (alphabetical) |
| `--case-sensitive` | Treat casing variants (e.g. `"Climate anxiety"` vs `"climate anxiety"`) as distinct keywords instead of merging them. Default: case-insensitive. |

By default, keywords that differ only in case are merged into one row, with counts summed and the most-frequent original casing kept as the display form (so acronyms like `CCAS` or `UK` are left untouched, since they only ever appear in one casing):

```bash
# climate anxiety,145 + Climate anxiety,34  ->  climate anxiety,179
txt2phrases merge -i keywords/ -o merged.csv

# Opt out and keep casing variants as separate rows
txt2phrases merge -i keywords/ -o merged.csv --case-sensitive
```

---

### 🧮 `classify`
Classify keywords as general (shared across documents) or specific (unique to one document) using TF-IDF.

```bash
txt2phrases classify -i keywords/ -o classified/
txt2phrases classify -i keywords/ -o classified/ --threshold 0.7 --min-freq 3
```

**Options:**

| Flag | Description |
|---|---|
| `-t, --threshold` | TF-IDF score (0-1) above which a keyword counts as "specific" to a document (default: 0.6) |
| `-m, --min-freq` | Minimum count within a document for a keyword to be considered at all (default: 5) |
| `--case-sensitive` | Treat casing variants (e.g. `"Age"` in one document's CSV vs `"age"` in another's) as distinct keywords instead of merging them before classifying. Default: case-insensitive. |

For each input CSV (`<name>.csv` or `<name>_keywords.csv`), produces `<name>_specific_keywords.csv` plus a combined `general_specific_keywords.csv` listing, for every keyword, which documents it's general vs. specific to.

By default, keywords that differ only in case across different documents' CSVs (e.g. `"Age"` in one file, `"age"` in another) are merged into a single keyword before TF-IDF is computed. Without this, the same real-world keyword split across two castings would each look artificially concentrated in whichever documents happened to use that casing, and could be misclassified as "specific" to both instead of correctly recognized as "general":

```bash
# "Age" (paper1) and "age" (paper2) merge into one row before classifying
txt2phrases classify -i keywords/ -o classified/

# Opt out and keep casing variants as separate keywords
txt2phrases classify -i keywords/ -o classified/ --case-sensitive
```

A higher threshold requires a keyword to be more exclusive to one document before it's called "specific"; a lower threshold is more permissive. See the Advanced Features section below for guidance on choosing a value.

---

### ⚙️ `auto`
Complete processing pipeline for `pygetpapers` output or PDF directories: converts PDFs to text and extracts keywords in one step. Automatically applies the same default stopword filtering and case-insensitive consolidation as `keyphrases` (not yet configurable from `auto` directly — use the `pdf2txt` → `keyphrases` → `merge`/`classify` commands separately if you need `--stopwords`, `--json`, or `--case-sensitive` control at this stage).

```bash
txt2phrases auto -i pygetpapers_output/ -o results/ -n 200
txt2phrases auto -i pdf_collection/ -o results/ -n 100
```

Output layout:

```
results/
├── txt/                       # converted text, one file per document
│   ├── paper1.txt
│   └── paper2.txt
├── paper1_keywords.csv        # written directly into results/, not a subfolder
└── paper2_keywords.csv
```

---

## 🔍 Advanced Features

### 1. **Choosing a `classify` threshold**

The TF-IDF score used by `classify` is a concentration measure between 0 and 1: a keyword found only in one document scores close to 1.0; a keyword split evenly across several documents scores lower. As a rough guide:

- **Higher threshold (0.8-0.9):** stricter — only near-exclusive terms count as "specific"
- **Lower threshold (0.4-0.5):** looser — terms shared across a few documents can still count as "specific" to each

Try comparing two thresholds on the same data (e.g. `0.5` vs `0.7`) before settling on a value, especially with a small number of documents.

### 2. **Complete Research Pipeline**

```bash
# Download papers with pygetpapers
pygetpapers -q "machine learning" -o papers/ -k 100

# Process and analyze
txt2phrases auto -i papers/ -o analysis/ -n 200

# Merge all keyword CSVs into one ranked list
txt2phrases merge -i analysis/ -o merged.csv

# Classify results
txt2phrases classify -i analysis/ -o classified/ --threshold 0.7
```

### 3. **Filtering out domain-specific noise**

The built-in stopword list covers common journal names and licence/boilerplate text, but every domain has its own artifacts (truncated table headers, section titles picked up as keyphrases, etc). If you spot noise the defaults don't catch, add it to a custom stopwords file and pass it to `keyphrases`:

```bash
txt2phrases keyphrases -i text/ -o keywords/ --stopwords my_stopwords.txt
```

---

## 📦 Output Formats

- **Text Conversion:** `.txt` files with extracted text
- **Keyword Extraction:** `.csv` files containing `keyword` and `count` columns, plus optional `.json` (see the `keyphrases` command above)
- **Merged Keywords:** a single `.csv` with aggregated `keyword`/`count` columns
- **Classification:** per-document `<name>_specific_keywords.csv` (`keyword`, `tfidf`, `count`) plus a combined `general_specific_keywords.csv` (`keyword`, `General`, `Specific`)

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
  - `lxml>=4.6.0`: For XML parsing
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

This project is licensed under the **Apache License** — see the `LICENSE` file for details.

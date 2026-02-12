# Graphviz diagrams – summary

This directory holds two Graphviz diagrams for the txt2phrases project: a **static** view of modules and dependencies, and a **flow** view of pipelines and file formats.

---

## static.dot / static.svg

**Purpose:** Static description of the codebase – which modules exist and how they depend on each other.

**Contents:**

- **txt2phrases package (cluster):**  
  `cli` (entry point), `pdf2txt`, `html2txt`, `keyword`, `merge`, `pygetpaper`, `classify_specific`. Each box is a module with its main entry (e.g. `convert_pdf_to_text()`, `merge_keyphrase_csvs()`).

- **CLI → modules:** The CLI subcommands (`pdf2txt`, `html2txt`, `keyphrases`, `auto`) dispatch to the corresponding modules. The `merge` module is not yet a CLI command; it is used by scripts.

- **Auto pipeline:** `pygetpaper` implements the `auto` command and uses `pdf2txt` and `keyword` (find PDFs → convert to TXT → extract keyphrases).

- **External dependencies (cluster):** PyPDF2, BeautifulSoup, transformers (Hugging Face), pandas, scikit-learn. Edges from package modules to these show which library each module uses.

**Convention:** Boxes = modules/runnable units; edges = “uses” or “dispatches to”. Top-to-bottom layout.

---

## flow.dot / flow.svg

**Purpose:** Data flow – which inputs go through which steps and become which outputs.

**Contents:**

- **Data (ellipses, yellow):** PDF(s), HTML(s), .txt, *_keywords.csv, merged.csv, and classification outputs (*_specific_keywords.csv, general_specific_keywords.csv).

- **Processes (rounded boxes, blue):** pdf2txt, html2txt, keyphrases, merge (script), auto, classify_specific (Python).

- **Main flows:**
  - **Document conversion:** PDF → pdf2txt → TXT; HTML → html2txt → TXT.
  - **Keyphrases:** TXT → keyphrases → *_keywords.csv.
  - **Merge:** *_keywords.csv → merge → merged.csv (aggregated counts).
  - **Auto:** PDF → auto → TXT (convert) and → *_keywords.csv (keyphrases) in one run.
  - **Classification (optional):** *_keywords.csv → classify_specific → specific/general CSVs.

**Convention:** Left-to-right flow where possible; ellipses = file types/data; rounded boxes = pipeline steps.

---

## Files in this directory

| File        | Role |
|------------|------|
| **static.dot** | Source for static structure diagram. |
| **flow.dot**   | Source for data-flow diagram. |
| **static.svg** | Rendered static diagram (from `dot -Tsvg`). |
| **flow.svg**   | Rendered flow diagram (from `dot -Tsvg`). |
| **README.md**  | Quick reference and rendering commands. |
| **summary.md** | This summary. |

To regenerate the SVGs after editing the `.dot` files, see **README.md**.

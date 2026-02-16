# Summary – India plant reports keyphrase extraction (2026-02-16)

Summary of work on extracting keyphrases from annual reports of plant research organisations in India: directory structure, scripts, make-like behaviour, and keyphrase × institution matrix outputs.

---

## 1. Task and scope

- **Goal:** Extract keywords from annual reports of plant research organisations in India using txt2phrases (PDF → text → keyphrases).
- **Location:** `Examples/otvirare/india_plant_reports/` (branch: `reports`).
- **Deliverables:** Per-report and merged keyword CSVs; keyphrase × institution matrix as CSV, as a plain HTML table, and as a jQuery DataTables page (table in DOM).

---

## 2. Institutions and reports

**Two batches of 10 institutions each (20 total).**

- **Batch 1:** ICAR, NBPGR, IIHR, IARI, CPCRI, IIVR, BSI, PPVFRA, NIPGR, IIPR.  
  Reports obtained (PDFs downloaded or present): NBPGR, CPCRI, IIVR, PPVFRA (4). Others have `DOWNLOAD_STATUS.md` with links or “manual download” notes.
- **Batch 2:** CTCRI, NRRI, IIOR, CICR, IISR, SBI, CIRCOT, IIWBR, CTRI, CRIJAF.  
  Reports obtained: CTCRI, NRRI, IIOR, SBI, CIRCOT, IIWBR (6). CICR, IISR, CTRI, CRIJAF documented for manual download or site check.

Each institution has a subdirectory (e.g. `nbpgr/`, `ctcri/`) containing any downloaded PDF, `DOWNLOAD_STATUS.md`, and (after extraction) `.txt` and `*_keywords.csv` files.

---

## 3. Scripts

### 3.1 `scripts/extract_keywords_from_reports.py`

- **Pipeline:** Find PDFs in institution subdirs → convert to `.txt` (pdf2txt) → extract keyphrases → write `*_keywords.csv` per report; optionally merge all keyword CSVs into one.
- **Make-like behaviour:**  
  - Skips PDF→TXT if the corresponding `.txt` already exists.  
  - Skips keyphrase extraction if `*_keywords.csv` already exists for that `.txt`.  
- **`--merge-only`:** Skips conversion and extraction; only builds the merged CSV from existing `*_keywords.csv` files (e.g. `merged_keywords.csv`).
- **Requirement:** Package must be installed (`pip install -e .`). No `sys.path` manipulation.

### 3.2 `scripts/build_keyphrase_table.py`

- **Input:** All `*_keywords.csv` under institution subdirs (multiple CSVs per institution are summed per keyphrase).
- **Outputs:**  
  - **(a) CSV:** `keyphrase_matrix.csv` – rows = keyphrases, columns = institutions; cell = count or blank if zero; extra columns **Total** (sum of counts) and **N_institutions** (number of non-zero cells in that row).  
  - **(b) DataTables HTML:** `keyphrase_datatables.html` – normal HTML `<table>` with `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>`; DataTables is initialised on that table (DOM-sourced data per [DataTables docs](https://datatables.net/examples/data_sources/dom.html)). Search, sort, pagination; default sort by Total descending.  
  - **(c) Plain HTML table:** `keyphrase_table.html` – same `<table>` markup with no JavaScript.
- **Institution headers:** Each institution column `<th>` has `title="Full institution name"` and the header cell content is `<a href="home page URL">institution_id</a>`. Full names and URLs come from `INSTITUTION_INFO` in the script (all 20 institutions).
- **Run:** `python scripts/build_keyphrase_table.py` (default reports-dir: `Examples/otvirare/india_plant_reports`). Optional `--csv`, `--html`, `--html-table` to set output paths.

---

## 4. Output files (under `Examples/otvirare/india_plant_reports/`)

| File | Description |
|------|-------------|
| `merged_keywords.csv` | Corpus-level keyword counts (one row per keyphrase, columns `keyword`, `count`). |
| `keyphrase_matrix.csv` | Keyphrase × institution matrix; blank for zero; columns include Total and N_institutions. |
| `keyphrase_datatables.html` | HTML with full `<table>` and DataTables initialised on it (search, sort, pagination). Institution headers: `title` = full name, `<a href="...">` = home page. |
| `keyphrase_table.html` | Same matrix as a static HTML table (no JavaScript). |

Per-institution dirs contain: PDF(s), `DOWNLOAD_STATUS.md`, `.txt` (from pdf2txt), and `*_keywords.csv` (from keyphrase extraction).

---

## 5. Conventions and decisions

- **No sys.path:** Scripts assume `txt2phrases` is installed; no runtime `sys.path` changes.
- **Make-like skip:** Extract script only converts PDFs and runs extraction when the corresponding output file is missing.
- **Merge-only:** Single option to refresh the merged CSV without re-running conversion or extraction.
- **Institution columns:** Matrix uses institution directory names as column IDs (e.g. `nbpgr`, `ctcri`). Multiple reports in one institution are aggregated by summing counts per keyphrase.

---

## 6. How to run (recap)

```bash
# Install (required for extract script)
pip install -e .

# Full pipeline: convert PDFs → extract keyphrases → merge
python scripts/extract_keywords_from_reports.py --merge

# Only rebuild merged CSV from existing *_keywords.csv
python scripts/extract_keywords_from_reports.py --merge-only

# Build keyphrase × institution matrix (CSV + DataTables HTML)
python scripts/build_keyphrase_table.py
```

---

## 7. Progress (follow-up)

- **DataTables with normal HTML table:** `keyphrase_datatables.html` was changed from DataTables-with-JSON to a full `<table>` in the DOM; DataTables is initialised on that table (DOM-sourced data) so the markup is standard HTML.
- **Plain HTML table:** `keyphrase_table.html` added as a static table with no JavaScript.
- **Institution header accessibility:** Each institution `<th>` now has `title="Full institution name"` and the cell content is `<a href="home page">id</a>`. `INSTITUTION_INFO` in `build_keyphrase_table.py` holds full name and URL for all 20 institutions; shared `_build_table_html()` generates the table for both HTML outputs.

---

## 8. References

- Task and institution tables: `Examples/otvirare/india_plant_reports/README.md`
- Merge feature and script conventions: `docs/summary/2026-02-12-session-summary.md`

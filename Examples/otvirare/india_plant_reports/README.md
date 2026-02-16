# India plant research organisations – annual reports

**Branch:** `reports`  
**Task:** Extract keywords from annual reports of plant research organisations in India.

---

## Task

1. Identify plant research organisations in India that publish annual reports.
2. Obtain the latest annual report (PDF) for each.
3. Use txt2phrases to convert PDFs to text and extract keyphrases.
4. Optionally merge keyword CSVs for corpus-level analysis.

---

## Initial findings and institutions table

Ten organisations were identified with links to recent annual reports:

| # | Organisation | Focus | Link to recent report(s) |
|---|---------------------------|--------------------------------|----------------------------------------------------------------|
| 1 | **Indian Council of Agricultural Research (ICAR)** | Overall agricultural & crop research | [Annual reports](https://www.icar.org.in/en/annual-report) (e.g. 2024–25, 2023–24) |
| 2 | **ICAR–National Bureau of Plant Genetic Resources (NBPGR)** | Plant genetic resources, germplasm | [Annual reports](https://nbpgr.org.in/nbpgr2023/annual-reports-2/) · [2023 PDF](https://nbpgr.org.in/nbpgr2023/wp-content/uploads/2024/07/Annual-report-2023_ICAR-NBPGR.pdf) |
| 3 | **ICAR–Indian Institute of Horticultural Research (IIHR)** | Horticulture, fruits & vegetables | [Annual reports](https://www.iihr.res.in/annual-reports) (2008–2024) |
| 4 | **ICAR–Indian Agricultural Research Institute (IARI)** | Crop science, breeding, Pusa | [Annual reports archive](https://www.iari.res.in/en/annual-reports-archive.php) · [2024 PDF](https://new.iari.res.in/files/Publication/annual_report/IARI_Annual_Report_2024_28072025.pdf) |
| 5 | **ICAR–Central Plantation Crops Research Institute (CPCRI)** | Coconut, palm, cocoa | [2023 annual report PDF](https://cpcri.gov.in/filemgr/webfs/publication/CPCRI_ANNUAL_REPORT2023.pdf) |
| 6 | **ICAR–Indian Institute of Vegetable Research (IIVR)** | Vegetable crops, Varanasi | [Site](https://icariivr.org.in/) · [2017–18 PDF](https://icariivr.org.in/wp-content/uploads/2025/11/Annual-Report-2017-2018English.pdf) |
| 7 | **Botanical Survey of India (BSI)** | Floristic surveys, plant taxonomy | [Annual reports](https://bsi.gov.in/annual-reports-of-bsi/en) · [2023–24 PDF](https://bsi.gov.in/uploads/documents/reports/annualReportBsi/hindi/BSI_Annual_Report_2023-2024.pdf) |
| 8 | **Protection of Plant Varieties and Farmers' Rights Authority (PPVFRA)** | Plant variety registration | [2021–22 annual report PDF](https://plantauthority.gov.in/sites/default/files/final-annual-report-2021-22-eng.pdf) |
| 9 | **National Institute of Plant Genome Research (NIPGR)** | Plant genomics (DBT) | [NIPGR](https://www.nipgr.ac.in/) – annual reports via library/institute pages |
| 10 | **ICAR–Indian Institute of Pulses Research (IIPR)** | Pulses, grain legumes | See [ICAR annual report](https://www.icar.org.in/en/annual-report) and [IIPR](https://iipr.icar.gov.in/) for institute-level reports |

---

## Second batch: 10 more institutions

| # | Organisation | Focus | Link / status |
|---|---------------------------|--------------------------------|----------------------------------------------------------------|
| 11 | **ICAR–Central Tuber Crops Research Institute (CTCRI)** | Tuber crops (cassava, sweet potato, yams, aroids) | 2024 report downloaded |
| 12 | **ICAR–National Rice Research Institute (NRRI)** | Rice research, Cuttack | 2017–18 report downloaded |
| 13 | **ICAR–Indian Institute of Oilseeds Research (IIOR)** | Oilseeds (castor, sunflower, etc.) | 2022 report downloaded |
| 14 | **ICAR–Central Institute for Cotton Research (CICR)** | Cotton research, Nagpur | [Annual reports](https://cicr.org.in/resources/resource-cicr-annual-reports/) – manual download |
| 15 | **ICAR–Indian Institute of Spices Research (IISR)** | Spices, Kozhikode | [Annual reports](http://spices.res.in/annual-report) – manual download |
| 16 | **ICAR–Sugarcane Breeding Institute (SBI)** | Sugarcane, Coimbatore | 2024 report downloaded |
| 17 | **ICAR–Central Institute for Research on Cotton Technology (CIRCOT)** | Cotton technology, Mumbai | 2020 report downloaded |
| 18 | **ICAR–Indian Institute of Wheat and Barley Research (IIWBR)** | Wheat & barley, Karnal | Director’s report 2023–24 downloaded |
| 19 | **ICAR–Central Tobacco Research Institute (CTRI)** | Tobacco, Rajahmundry | [Site](https://ctri.icar.gov.in/) – check for report |
| 20 | **ICAR–Central Research Institute for Jute and Allied Fibres (CRIJAF)** | Jute and allied fibres, Barrackpore | [Site](https://crijaf.icar.gov.in/) – check for report |

---

## Directory layout

Each institution has a subdirectory under `india_plant_reports/`:

**Batch 1:** `icar/`, `nbpgr/`, `iihr/`, `iari/`, `cpcri/`, `iivr/`, `bsi/`, `ppvfra/`, `nipgr/`, `iipr/`

**Batch 2:** `ctcri/`, `nrri/`, `iior/`, `cicr/`, `iisr/`, `sbi/`, `circot/`, `iiwbr/`, `ctri/`, `crijaf/`

Within each: downloaded PDF (if any), and a short `DOWNLOAD_STATUS.md` explaining what was downloaded or why not.

---

## Script

- **`scripts/extract_keywords_from_reports.py`** – Intended to run pdf2txt and keyphrase extraction over `Examples/otvirare/india_plant_reports` (and optionally merge). Created but not run; await user instructions.

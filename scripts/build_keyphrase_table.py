#!/usr/bin/env python3
"""
Build a keyphrase × institution matrix from *_keywords.csv files.

Outputs:
  (a) CSV: rows = keyphrases, columns = institutions; cell = count or blank if zero.
           Extra columns: Total (sum of counts), N_institutions (number of non-zero cells).
  (b) HTML + jQuery DataTables: same data in a sortable, searchable table.

Requires package installed: pip install -e .

  python scripts/build_keyphrase_table.py
  python scripts/build_keyphrase_table.py --reports-dir Examples/otvirare/india_plant_reports
"""
import argparse
import csv
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORTS_DIR = Path(PROJECT_ROOT, "Examples", "otvirare", "india_plant_reports")

INSTITUTION_DIRS = [
    "icar", "nbpgr", "iihr", "iari", "cpcri", "iivr", "bsi", "ppvfra", "nipgr", "iipr",
    "ctcri", "nrri", "iior", "cicr", "iisr", "sbi", "circot", "iiwbr", "ctri", "crijaf",
]


def _collect_keyword_csvs(reports_dir: Path):
    """Yield (institution_id, csv_path) for each *_keywords.csv in institution subdirs."""
    for inst in INSTITUTION_DIRS:
        inst_dir = reports_dir / inst
        if not inst_dir.is_dir():
            continue
        for csv_path in sorted(inst_dir.glob("*_keywords.csv")):
            yield (inst, csv_path)


def _load_matrix(reports_dir: Path):
    """
    Load all *_keywords.csv and build:
      - data: dict[keyphrase][institution] = count
      - institutions: ordered list of institution ids (column order)
    """
    # Discover institutions and their CSVs (may be multiple per institution)
    inst_to_csvs = {}
    for inst, csv_path in _collect_keyword_csvs(reports_dir):
        inst_to_csvs.setdefault(inst, []).append(csv_path)
    institutions = sorted(inst_to_csvs.keys())

    data = {}
    for inst in institutions:
        for csv_path in inst_to_csvs[inst]:
            with open(csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    kw = row.get("keyword", "").strip()
                    if not kw:
                        continue
                    try:
                        count = int(row.get("count", 0))
                    except (ValueError, TypeError):
                        count = 0
                    if count <= 0:
                        continue
                    if kw not in data:
                        data[kw] = {}
                    data[kw][inst] = data[kw].get(inst, 0) + count

    return data, institutions


def _build_rows(data, institutions):
    """Build list of rows: (keyphrase, count_per_inst..., total, n_institutions)."""
    rows = []
    for keyphrase, inst_counts in data.items():
        total = sum(inst_counts.values())
        n_institutions = len(inst_counts)
        rows.append((keyphrase, inst_counts, total, n_institutions))
    # Sort by total descending, then by keyphrase
    rows.sort(key=lambda r: (-r[2], r[0]))
    return rows


def write_csv(reports_dir: Path, out_csv: Path, data, institutions, rows):
    """Write matrix CSV; blank cell when count is zero."""
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = ["keyword"] + institutions + ["Total", "N_institutions"]
        writer.writerow(header)
        for keyphrase, inst_counts, total, n_institutions in rows:
            row = [keyphrase]
            for inst in institutions:
                c = inst_counts.get(inst, 0)
                row.append(c if c else "")
            row.append(total)
            row.append(n_institutions)
            writer.writerow(row)


def write_datatables_html(reports_dir: Path, out_html: Path, institutions, rows):
    """Write a single HTML file with embedded data and jQuery DataTables."""
    # Build JSON data for DataTables: array of arrays [keyword, count1, count2, ..., total, n_inst]
    table_rows = []
    for keyphrase, inst_counts, total, n_institutions in rows:
        row = [keyphrase]
        for inst in institutions:
            c = inst_counts.get(inst, 0)
            row.append(c if c else "")
        row.append(total)
        row.append(n_institutions)
        table_rows.append(row)

    columns = [{"title": "Keyword"}] + [{"title": inst} for inst in institutions] + [
        {"title": "Total"},
        {"title": "N_institutions"},
    ]
    columns_js = json.dumps(columns)
    data_js = json.dumps(table_rows)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Keyphrase × Institution matrix</title>
  <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
</head>
<body>
  <div class="container" style="margin: 1em;">
    <h1>Keyphrase × Institution matrix</h1>
    <p>Rows = keyphrases, columns = institutions. Blank = zero. Total = sum of counts; N_institutions = number of reports containing the keyphrase.</p>
    <table id="keyphrase-table" class="display" style="width:100%"></table>
  </div>
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
  <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
  <script>
    var keyphraseColumns = {columns_js};
    var keyphraseData = {data_js};
    $(document).ready(function() {{
      $('#keyphrase-table').DataTable({{
        data: keyphraseData,
        columns: keyphraseColumns,
        pageLength: 50,
        order: [[keyphraseColumns.length - 2, 'desc']],
        columnDefs: [
          {{ targets: 0, width: '15%' }},
          {{ targets: -1, width: '8%' }},
          {{ targets: -2, width: '8%' }}
        ]
      }});
    }});
  </script>
</body>
</html>
"""
    out_html.write_text(html_content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Build keyphrase × institution matrix (CSV + DataTables HTML)."
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=DEFAULT_REPORTS_DIR,
        help=f"Root directory containing institution subdirs (default: {DEFAULT_REPORTS_DIR})",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Output CSV path (default: <reports-dir>/keyphrase_matrix.csv)",
    )
    parser.add_argument(
        "--html",
        type=Path,
        default=None,
        help="Output HTML path (default: <reports-dir>/keyphrase_datatables.html)",
    )
    args = parser.parse_args()

    if not args.reports_dir.exists():
        print(f"Reports directory not found: {args.reports_dir}", file=sys.stderr)
        sys.exit(1)

    data, institutions = _load_matrix(args.reports_dir)
    if not institutions:
        print("No *_keywords.csv files found in institution subdirs.", file=sys.stderr)
        sys.exit(1)

    rows = _build_rows(data, institutions)
    out_csv = args.csv or (args.reports_dir / "keyphrase_matrix.csv")
    out_html_path = args.html or (args.reports_dir / "keyphrase_datatables.html")

    write_csv(args.reports_dir, out_csv, data, institutions, rows)
    write_datatables_html(args.reports_dir, out_html_path, institutions, rows)

    print(f"CSV:  {out_csv} ({len(rows)} keyphrases, {len(institutions)} institutions)")
    print(f"HTML: {out_html_path}")


if __name__ == "__main__":
    main()

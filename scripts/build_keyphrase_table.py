#!/usr/bin/env python3
"""
Build a keyphrase × institution matrix from *_keywords.csv files.

Outputs:
  (a) CSV: rows = keyphrases, columns = institutions; cell = count or blank if zero.
           Extra columns: Total (sum of counts), N_institutions (number of non-zero cells).
  (b) HTML + jQuery DataTables: same data in a sortable, searchable table.
  (c) Plain HTML table: static <table> with <tr>, <th>, <td> (no JavaScript).

Requires package installed: pip install -e .

  python scripts/build_keyphrase_table.py
  python scripts/build_keyphrase_table.py --reports-dir Examples/otvirare/india_plant_reports
"""
import argparse
import csv
import html
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORTS_DIR = Path(PROJECT_ROOT, "Examples", "otvirare", "india_plant_reports")

INSTITUTION_DIRS = [
    "icar", "nbpgr", "iihr", "iari", "cpcri", "iivr", "bsi", "ppvfra", "nipgr", "iipr",
    "ctcri", "nrri", "iior", "cicr", "iisr", "sbi", "circot", "iiwbr", "ctri", "crijaf",
]

# Full name and home page URL per institution id (for <th title=""> and <a href="">)
INSTITUTION_INFO = {
    "icar": {"name": "Indian Council of Agricultural Research", "url": "https://www.icar.org.in/"},
    "nbpgr": {"name": "ICAR–National Bureau of Plant Genetic Resources", "url": "https://nbpgr.org.in/"},
    "iihr": {"name": "ICAR–Indian Institute of Horticultural Research", "url": "https://www.iihr.res.in/"},
    "iari": {"name": "ICAR–Indian Agricultural Research Institute", "url": "https://www.iari.res.in/"},
    "cpcri": {"name": "ICAR–Central Plantation Crops Research Institute", "url": "https://cpcri.icar.gov.in/"},
    "iivr": {"name": "ICAR–Indian Institute of Vegetable Research", "url": "https://icariivr.org.in/"},
    "bsi": {"name": "Botanical Survey of India", "url": "https://bsi.gov.in/"},
    "ppvfra": {"name": "Protection of Plant Varieties and Farmers' Rights Authority", "url": "https://plantauthority.gov.in/"},
    "nipgr": {"name": "National Institute of Plant Genome Research", "url": "https://www.nipgr.ac.in/"},
    "iipr": {"name": "ICAR–Indian Institute of Pulses Research", "url": "https://iipr.icar.gov.in/"},
    "ctcri": {"name": "ICAR–Central Tuber Crops Research Institute", "url": "https://www.ctcri.org/"},
    "nrri": {"name": "ICAR–National Rice Research Institute", "url": "https://icar-nrri.in/"},
    "iior": {"name": "ICAR–Indian Institute of Oilseeds Research", "url": "https://icar-iior.org.in/"},
    "cicr": {"name": "ICAR–Central Institute for Cotton Research", "url": "https://cicr.org.in/"},
    "iisr": {"name": "ICAR–Indian Institute of Spices Research", "url": "https://spices.res.in/"},
    "sbi": {"name": "ICAR–Sugarcane Breeding Institute", "url": "https://sugarcane.res.in/"},
    "circot": {"name": "ICAR–Central Institute for Research on Cotton Technology", "url": "https://circot.icar.gov.in/"},
    "iiwbr": {"name": "ICAR–Indian Institute of Wheat and Barley Research", "url": "https://www.aicrpwheatbarleyicar.in/"},
    "ctri": {"name": "ICAR–Central Tobacco Research Institute", "url": "https://ctri.icar.gov.in/"},
    "crijaf": {"name": "ICAR–Central Research Institute for Jute and Allied Fibres", "url": "https://crijaf.icar.gov.in/"},
}


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
    """Write HTML with a normal <table> and DataTables initialised on it (DOM-sourced data)."""
    table_html = _build_table_html(institutions, rows, table_id="keyphrase-table", table_class="display")
    # DataTables order: 0-based column index; Total is at index len(institutions) + 1
    total_col_index = len(institutions) + 1
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
{table_html}
  </div>
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
  <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
  <script>
    $(document).ready(function() {{
      $('#keyphrase-table').DataTable({{
        pageLength: 50,
        order: [[{total_col_index}, 'desc']],
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


def _build_table_html(institutions, rows, table_id=None, table_class=None):
    """Build a normal HTML <table> with <thead>, <tbody>, <tr>, <th>, <td>. Returns markup string."""
    def esc(s):
        return html.escape(str(s), quote=True)
    id_attr = f' id="{html.escape(table_id)}"' if table_id else ""
    class_attr = f' class="{html.escape(table_class)}"' if table_class else ""
    lines = [f"    <table{id_attr}{class_attr} style=\"width:100%\">", "      <thead>", "        <tr>", "          <th>keyword</th>"]
    for inst in institutions:
        info = INSTITUTION_INFO.get(inst, {})
        name = info.get("name", inst)
        url = info.get("url", "")
        title_attr = f' title="{esc(name)}"'
        if url:
            cell_content = f'<a href="{esc(url)}">{esc(inst)}</a>'
        else:
            cell_content = esc(inst)
        lines.append(f"          <th{title_attr}>{cell_content}</th>")
    lines.extend([
        "          <th>Total</th>",
        "          <th>N_institutions</th>",
        "        </tr>",
        "      </thead>",
        "      <tbody>",
    ])
    for keyphrase, inst_counts, total, n_institutions in rows:
        cells = [f"          <td>{esc(keyphrase)}</td>"]
        for inst in institutions:
            c = inst_counts.get(inst, 0)
            val = str(c) if c else ""
            cells.append(f"          <td class=\"num\">{esc(val)}</td>")
        cells.append(f"          <td class=\"num\">{total}</td>")
        cells.append(f"          <td class=\"num\">{n_institutions}</td>")
        lines.append("        <tr>")
        lines.extend(cells)
        lines.append("        </tr>")
    lines.extend(["      </tbody>", "    </table>"])
    return "\n".join(lines)


def write_html_table(out_path: Path, institutions, rows):
    """Write a static HTML file with a normal <table>, <tr>, <th>, <td>."""
    table_html = _build_table_html(institutions, rows)
    full = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Keyphrase × Institution matrix</title>
  <style>
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 4px 8px; text-align: left; }}
    th {{ background: #eee; }}
    td.num {{ text-align: right; }}
  </style>
</head>
<body>
  <div style="margin: 1em;">
    <h1>Keyphrase × Institution matrix</h1>
    <p>Rows = keyphrases, columns = institutions. Blank = zero. Total = sum of counts; N_institutions = number of reports containing the keyphrase.</p>
{table_html}
  </div>
</body>
</html>
"""
    out_path.write_text(full, encoding="utf-8")


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
        help="Output DataTables HTML path (default: <reports-dir>/keyphrase_datatables.html)",
    )
    parser.add_argument(
        "--html-table",
        type=Path,
        default=None,
        help="Output plain HTML table path (default: <reports-dir>/keyphrase_table.html)",
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
    out_table_path = args.html_table or (args.reports_dir / "keyphrase_table.html")

    write_csv(args.reports_dir, out_csv, data, institutions, rows)
    write_datatables_html(args.reports_dir, out_html_path, institutions, rows)
    write_html_table(out_table_path, institutions, rows)

    print(f"CSV:   {out_csv} ({len(rows)} keyphrases, {len(institutions)} institutions)")
    print(f"HTML (DataTables): {out_html_path}")
    print(f"HTML (table):      {out_table_path}")


if __name__ == "__main__":
    main()

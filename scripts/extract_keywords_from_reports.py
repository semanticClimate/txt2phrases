#!/usr/bin/env python3
"""
Extract keywords from annual report PDFs under Examples/otvirare/india_plant_reports.

Pipeline:
  1. Find all PDFs in institution subdirectories (icar, nbpgr, iihr, ...).
  2. Convert each PDF to .txt in the same institution directory (pdf2txt).
  3. Run keyphrase extraction on each .txt, writing *_keywords.csv in the same directory.
  4. Optionally merge all *_keywords.csv into one corpus-level CSV.

Make-like: skips PDF→TXT if the .txt already exists; skips keyphrase extraction if
*_keywords.csv already exists for that .txt. Use --merge-only to skip extraction
and only build the merged CSV from existing *_keywords.csv files.

Requires package installed: pip install -e .

  python scripts/extract_keywords_from_reports.py
  python scripts/extract_keywords_from_reports.py --reports-dir Examples/otvirare/india_plant_reports
  python scripts/extract_keywords_from_reports.py --merge --merged-output Examples/otvirare/india_plant_reports/merged_keywords.csv
  python scripts/extract_keywords_from_reports.py -n 500 --merge
  python scripts/extract_keywords_from_reports.py --merge-only   # skip extraction, only build merged CSV
"""
import argparse
import sys
from pathlib import Path

from txt2phrases.keyword import KeywordExtraction
from txt2phrases.merge import merge_keyphrase_csvs
from txt2phrases.pdf2txt import convert_pdf_to_text


def _txt_path_for_pdf(pdf_path: Path) -> Path:
    """Path of .txt that would be produced from this PDF (same dir, same stem)."""
    return pdf_path.parent / (pdf_path.stem + ".txt")


def _keywords_csv_for_txt(txt_path: Path) -> Path:
    """Path of *_keywords.csv produced from this .txt (same dir)."""
    return txt_path.parent / (txt_path.stem + "_keywords.csv")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORTS_DIR = Path(PROJECT_ROOT, "Examples", "otvirare", "india_plant_reports")

# Subdirectory names under reports_dir (one per institution)
INSTITUTION_DIRS = [
    "icar",
    "nbpgr",
    "iihr",
    "iari",
    "cpcri",
    "iivr",
    "bsi",
    "ppvfra",
    "nipgr",
    "iipr",
    # Second batch
    "ctcri",
    "nrri",
    "iior",
    "cicr",
    "iisr",
    "sbi",
    "circot",
    "iiwbr",
    "ctri",
    "crijaf",
]


def main():
    parser = argparse.ArgumentParser(
        description="Extract keywords from annual report PDFs (pdf2txt → keyphrases, optional merge)."
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=DEFAULT_REPORTS_DIR,
        help=f"Root directory containing institution subdirs (default: {DEFAULT_REPORTS_DIR})",
    )
    parser.add_argument(
        "-n",
        "--top-n",
        type=int,
        default=200,
        help="Top N keywords per report (default: 200)",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="After extraction, merge all *_keywords.csv into one CSV",
    )
    parser.add_argument(
        "--merged-output",
        type=Path,
        default=None,
        help="Output path for merged CSV (default: <reports-dir>/merged_keywords.csv)",
    )
    parser.add_argument(
        "--top-n-merged",
        type=int,
        default=None,
        help="If --merge, keep only top N keywords in merged CSV (default: all)",
    )
    parser.add_argument(
        "--merge-only",
        action="store_true",
        help="Skip PDF→TXT and keyphrase extraction; only merge existing *_keywords.csv (implies --merge)",
    )
    args = parser.parse_args()

    if not args.reports_dir.exists():
        print(f"Reports directory not found: {args.reports_dir}")
        sys.exit(1)

    do_merge = args.merge or args.merge_only

    if not args.merge_only:
        # 1) Convert PDFs to TXT (skip if .txt already exists)
        for inst in INSTITUTION_DIRS:
            inst_dir = args.reports_dir / inst
            if not inst_dir.is_dir():
                continue
            for pdf_path in sorted(inst_dir.glob("*.pdf")):
                txt_path = _txt_path_for_pdf(pdf_path)
                if txt_path.exists():
                    continue
                result = convert_pdf_to_text(str(pdf_path), str(inst_dir))
                if result:
                    print(f"Converted: {pdf_path.name} -> {Path(result).name}")
                else:
                    print(f"Failed to convert: {pdf_path}", file=sys.stderr)

        # 2) Extract keyphrases only for .txt files that don't have *_keywords.csv yet
        for inst in INSTITUTION_DIRS:
            inst_dir = args.reports_dir / inst
            if not inst_dir.is_dir():
                continue
            for txt_path in sorted(inst_dir.glob("*.txt")):
                csv_path = _keywords_csv_for_txt(txt_path)
                if csv_path.exists():
                    continue
                extractor = KeywordExtraction(
                    input_path=str(txt_path),
                    output_folder=str(inst_dir),
                    top_n=args.top_n,
                )
                extractor.extract()
                print(f"Keyphrases: {txt_path.name} -> {csv_path.name}")

    # 3) Merge (when --merge or --merge-only)
    if do_merge:
        csv_paths = []
        for inst in INSTITUTION_DIRS:
            inst_dir = args.reports_dir / inst
            if inst_dir.is_dir():
                csv_paths.extend(sorted(inst_dir.glob("*_keywords.csv")))
        if not csv_paths:
            print("No *_keywords.csv files found to merge.")
            sys.exit(0)
        out_path = args.merged_output or (args.reports_dir / "merged_keywords.csv")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        merge_keyphrase_csvs(
            input_paths=csv_paths,
            output_path=out_path,
            top_n=args.top_n_merged,
        )
        print(f"Merged {len(csv_paths)} CSVs -> {out_path}")


if __name__ == "__main__":
    main()

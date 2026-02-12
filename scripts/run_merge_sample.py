#!/usr/bin/env python3
"""
Merge keyphrase CSV files (keyword, count) with aggregated counts.

Input: CSV file(s) or directory of CSVs. Default input: test/fixtures/merge_sample/
Output: single CSV with summed counts per keyword.

Run with package installed: pip install -e .
  python scripts/run_merge_sample.py
  python scripts/run_merge_sample.py -i test/fixtures/merge_sample -o merged.csv
  python scripts/run_merge_sample.py -i file1.csv file2.csv -o merged.csv --top-n 20
"""
import argparse
from pathlib import Path

import pandas as pd

from txt2phrases.merge import merge_keyphrase_csvs

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = Path(PROJECT_ROOT, "test", "fixtures", "merge_sample")
DEFAULT_OUTPUT = Path(PROJECT_ROOT, "temp", "scripts", "merge_sample", "merged.csv")


def main():
    parser = argparse.ArgumentParser(description="Merge keyphrase CSV files with aggregated counts.")
    parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        default=[str(DEFAULT_INPUT)],
        help="Input CSV file(s) or a single directory path (default: test/fixtures/merge_sample)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output merged CSV path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=None,
        help="Keep only top N keywords by count (default: all)",
    )
    args = parser.parse_args()

    # Resolve input: one path -> directory or file; multiple paths -> list of files
    raw = [Path(p) for p in args.input]
    if len(raw) == 1 and raw[0].is_dir():
        input_paths = raw[0]
    else:
        for p in raw:
            if not p.exists():
                parser.error(f"Input path does not exist: {p}")
        input_paths = raw

    if not Path(args.output).parent.exists():
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    merge_keyphrase_csvs(input_paths=input_paths, output_path=args.output, top_n=args.top_n)

    print(f"Input:  {input_paths}")
    print(f"Output: {args.output}")
    df = pd.read_csv(args.output)
    print(f"Keywords: {len(df)}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()

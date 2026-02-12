#!/usr/bin/env python3
"""
Extract keyphrases from text file(s) and write keyword CSVs.

Input: text file or directory of .txt files. Default input: test/fixtures/sample.txt
Output: directory of *_keywords.csv files. Requires keyphrase model (downloads on first run).

Run with package installed: pip install -e .
  python scripts/run_keyphrases_sample.py
  python scripts/run_keyphrases_sample.py -i test/fixtures/sample.txt -o temp/scripts/keyphrases_out
  python scripts/run_keyphrases_sample.py -i my_docs/ -o keywords/ -n 100
"""
import argparse
import sys
from pathlib import Path

from txt2phrases.keyword import KeywordExtraction

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = Path(PROJECT_ROOT, "test", "fixtures", "sample.txt")
DEFAULT_OUTPUT = Path(PROJECT_ROOT, "temp", "scripts", "keyphrases_sample", "output")


def main():
    parser = argparse.ArgumentParser(description="Extract keyphrases from text file(s).")
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Input .txt file or directory of .txt files (default: test/fixtures/sample.txt)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output directory for keyword CSVs (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "-n",
        "--top-n",
        type=int,
        default=50,
        help="Top N keywords per file (default: 50)",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input not found: {args.input}")
        sys.exit(1)

    args.output.mkdir(parents=True, exist_ok=True)

    extractor = KeywordExtraction(
        input_path=str(args.input),
        output_folder=str(args.output),
        top_n=args.top_n,
    )
    extractor.extract()

    print(f"Input:  {args.input}")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()

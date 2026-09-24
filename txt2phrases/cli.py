# cli.py
import argparse
import sys
import os

# Add the parent directory to Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from txt2phrases.pdf2txt import convert_pdf_to_text
from txt2phrases.html2txt import convert_html_to_text
from txt2phrases.keyword import KeywordExtraction
from txt2phrases.pygetpaper import main as pygetpaper_main
from txt2phrases.merge import merge_keyphrase_csvs
from txt2phrases.classify_specific import classify_keywords_split_files


def main():
    parser = argparse.ArgumentParser(
        description="txt2phrases CLI: PDF/HTML → TXT → keywords",
        prog="txt2phrases"  # Explicitly set the program name
    )
    subparsers = parser.add_subparsers(
        dest="command", 
        required=True,
        help="Available commands"
    )

    # PDF2TXT
    parser_pdf = subparsers.add_parser("pdf2txt", help="Convert PDF(s) to TXT")
    parser_pdf.add_argument("-i", "--input", required=True, help="Input PDF file or folder")
    parser_pdf.add_argument("-o", "--output", required=True, help="Output folder")

    # HTML2TXT
    parser_html = subparsers.add_parser("html2txt", help="Convert HTML(s) to TXT")
    parser_html.add_argument("-i", "--input", required=True, help="Input HTML file or folder")
    parser_html.add_argument("-o", "--output", required=True, help="Output folder")

    # Keyword Extraction
    parser_keyword = subparsers.add_parser("keyphrases", help="Extract keywords from TXT files")
    parser_keyword.add_argument("-i", "--input", required=True, help="Input TXT file or folder")
    parser_keyword.add_argument("-o", "--output", required=True, help="Output folder")
    parser_keyword.add_argument("-n", "--top_n", type=int, default=1000, help="Top N keywords")

    parser_keyword.add_argument(
        "--stopwords", default=None,
        help="Path to a custom stopwords file (one term per line, '#' for comments). "
             "Merged with the built-in default list unless --no-default-stopwords is set."
    )
    parser_keyword.add_argument(
        "--no-default-stopwords", action="store_true",
        help="Disable the built-in stopword list (journal names, licence boilerplate). "
             "Only terms from --stopwords, if given, will be filtered."
    )
    parser_keyword.add_argument(
        "--json", action="store_true",
        help="Also write a <name>_keywords.json file alongside the CSV for each input file."
    )

    parser_keyword.add_argument(
        "--case-sensitive", action="store_true",
        help="Treat casing variants (e.g. 'Climate anxiety' vs 'climate anxiety') as distinct "
             "keywords instead of merging them (default: case-insensitive merging)"
    )
    
    # Auto pipeline
    parser_auto = subparsers.add_parser("auto", help="Run full pipeline: PDF → TXT → keywords")
    parser_auto.add_argument("-i", "--input", required=True, help="Input folder (PDFs or PyGetPapers output)")
    parser_auto.add_argument("-o", "--output", required=True, help="Output folder for TXT and keywords")
    parser_auto.add_argument("-n", "--num_keywords", type=int, default=100, help="Number of top keywords to extract")

    # Merge keyword CSVs
    parser_merge = subparsers.add_parser("merge", help="Merge multiple keyword CSV files")
    parser_merge.add_argument(
        "-i", "--input", required=True, nargs="+",
        help="Input CSV file(s) or a directory containing CSV files"
    )
    parser_merge.add_argument("-o", "--output", required=True, help="Output merged CSV file path")
    parser_merge.add_argument("-n", "--top-n", type=int, default=None, help="Keep only the top N keywords")
    parser_merge.add_argument(
        "--sort-by", choices=["count", "keyword"], default="count",
        help="Sort merged results by 'count' (default) or 'keyword'"
    )

    parser_merge.add_argument(
        "--case-sensitive", action="store_true",
        help="Treat casing variants (e.g. 'Climate anxiety' vs 'climate anxiety') as distinct "
             "keywords instead of merging them (default: case-insensitive merging)"
    )

    # Classify keywords into general/specific
    parser_classify = subparsers.add_parser(
        "classify", help="Classify keywords as general or chapter-specific using TF-IDF"
    )
    parser_classify.add_argument(
        "-i", "--input", required=True,
        help="Input directory containing per-chapter keyword CSVs (keyword, count columns)"
    )
    parser_classify.add_argument("-o", "--output", required=True, help="Output directory for classified CSVs")
    parser_classify.add_argument(
        "-t", "--threshold", type=float, default=0.6,
        help="TF-IDF score threshold above which a keyword counts as 'specific' (default: 0.6)"
    )
    parser_classify.add_argument(
        "-m", "--min-freq", type=int, default=5,
        help="Minimum count within a chapter for a keyword to be considered (default: 5)"
    )

    parser_classify.add_argument(
        "--case-sensitive", action="store_true",
        help="Treat casing variants (e.g. 'Age' in one chapter vs 'age' in another) as distinct "
             "keywords instead of merging them (default: case-insensitive merging)"
    )

    args = parser.parse_args()

    if args.command == "pdf2txt":
        # Handle PDF conversion directly
        from pathlib import Path
        
        input_path = Path(args.input)
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if input_path.is_file() and input_path.suffix.lower() == ".pdf":
            convert_pdf_to_text(input_path, output_path)
            print(f"Converted {input_path} to TXT")
        elif input_path.is_dir():
            pdf_files = list(input_path.glob("*.pdf"))
            print(f"Found {len(pdf_files)} PDF files to convert")
            
            for pdf_file in pdf_files:
                convert_pdf_to_text(pdf_file, output_path)
            
            print(f"All PDF files converted to TXT in: {output_path}")
        else:
            print("No PDF files found.")
            
    elif args.command == "html2txt":
        # Handle HTML conversion directly
        from pathlib import Path
        
        input_path = Path(args.input)
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if input_path.is_file() and input_path.suffix.lower() == ".html":
            convert_html_to_text(input_path, output_path)
            print(f"Converted {input_path} to TXT")
        elif input_path.is_dir():
            html_files = list(input_path.glob("*.html"))
            print(f"Found {len(html_files)} HTML files to convert")
            
            for html_file in html_files:
                convert_html_to_text(html_file, output_path)
            
            print(f"All HTML files converted to TXT in: {output_path}")
        else:
            print("No HTML files found.")
            
    elif args.command == "keyphrases":
        extractor = KeywordExtraction(
            input_path=args.input,
            output_folder=args.output,
            top_n=args.top_n,
            stopwords_path=args.stopwords,
            use_default_stopwords=not args.no_default_stopwords,
            output_json=args.json,
            case_insensitive=not args.case_sensitive,
        )
        extractor.extract()
     
    elif args.command == "auto":
        # Call pygetpaper_main with the parsed arguments
        pygetpaper_main(["-i", args.input, "-o", args.output, "-n", str(args.num_keywords)])

    elif args.command == "merge":
        merge_keyphrase_csvs(
            input_paths=args.input,
            output_path=args.output,
            top_n=args.top_n,
            sort_by=args.sort_by,
            case_insensitive=not args.case_sensitive,
        )

    elif args.command == "classify":
        classify_keywords_split_files(
            input_dir=args.input,
            output_dir=args.output,
            threshold=args.threshold,
            min_freq=args.min_freq,
            case_insensitive=not args.case_sensitive,
        )  

if __name__ == "__main__":
    main()
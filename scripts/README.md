# Sample scripts

Scripts use **test/** for default input data. Output is written under `temp/scripts/` unless you set `-o`. You can override input and output with arguments.

## Running scripts

Install the package first (from project root), then run:

```bash
pip install -e .
python scripts/run_merge_sample.py
python scripts/run_keyphrases_sample.py   # requires model download on first run
```

## User input (files and output)

### run_merge_sample.py

Merge keyphrase CSVs (columns: keyword, count). Default input: `test/fixtures/merge_sample/` (directory of sample CSVs). Default output: `temp/scripts/merge_sample/merged.csv`.

```bash
# Defaults (input: test/fixtures/merge_sample, output: temp/.../merged.csv)
python scripts/run_merge_sample.py

# Custom directory
python scripts/run_merge_sample.py -i test/fixtures/merge_sample -o merged.csv

# Explicit files
python scripts/run_merge_sample.py -i file1.csv file2.csv -o merged.csv

# Limit to top 20 keywords
python scripts/run_merge_sample.py -i my_keywords/ -o top20.csv --top-n 20
```

### run_keyphrases_sample.py

Extract keyphrases from text. Default input: `test/fixtures/sample.txt`. Default output: `temp/scripts/keyphrases_sample/output/`.

```bash
# Defaults (input: test/fixtures/sample.txt, output: temp/.../output/)
python scripts/run_keyphrases_sample.py

# Custom file or directory
python scripts/run_keyphrases_sample.py -i my_doc.txt -o my_keywords/
python scripts/run_keyphrases_sample.py -i my_txts/ -o my_keywords/ -n 100
```

## Output locations (defaults)

- **Merge:** `temp/scripts/merge_sample/merged.csv`
- **Keyphrases:** `temp/scripts/keyphrases_sample/output/*_keywords.csv`

The `temp/` directory is not committed (see `.gitignore`).

import os
import re
import json
from datetime import datetime, timezone
from collections import Counter, defaultdict
import pandas as pd
from tqdm import tqdm
from transformers import (
    TokenClassificationPipeline,
    AutoModelForTokenClassification,
    AutoTokenizer,
)
from transformers.pipelines import AggregationStrategy

from txt2phrases.stopwords import load_stopwords, filter_stopwords


# -----------------------------
# Keyphrase Extraction Pipeline
# -----------------------------
class KeyphraseExtractionPipeline(TokenClassificationPipeline):
    """
    Customized Hugging Face TokenClassificationPipeline
    optimized for extracting keyphrases.
    """

    def __init__(self, model_name):
        super().__init__(
            model=AutoModelForTokenClassification.from_pretrained(model_name),
            tokenizer=AutoTokenizer.from_pretrained(model_name),
        )

    def postprocess(self, *args, **kwargs):
        results = super().postprocess(
            *args,
            aggregation_strategy=AggregationStrategy.SIMPLE,
            **kwargs
        )
        return [result.get("word").strip() for result in results if result.get("word")]


# -----------------------------
# Standalone post-processing helpers
# (kept free of the model/class so they're unit-testable without loading
#  the transformer model)
# -----------------------------
def consolidate_case_variants(counts):
    """
    Merge casing variants of the same keyword (e.g. 'climate anxiety' and
    'Climate anxiety') into a single entry, summing their counts.

    The display form kept for each group is the original-cased variant
    with the highest count (ties broken alphabetically, for deterministic
    output) - this keeps acronyms/proper nouns (e.g. 'CCAS', 'UK') in their
    natural casing as long as that's the (or a tied) dominant variant,
    while still merging casing variants of ordinary phrases into one entry.

    Mirrors the equivalent logic in merge.py's _aggregate_case_insensitive,
    but operates on a Counter of (keyword -> count) rather than a DataFrame
    of per-source rows, since extraction only ever sees one file at a time.
    """
    groups = defaultdict(lambda: defaultdict(int))
    for keyword, count in counts.items():
        groups[keyword.casefold()][keyword] += count

    consolidated = Counter()
    for variants in groups.values():
        total = sum(variants.values())
        display_form = sorted(variants.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        consolidated[display_form] = total

    return consolidated


def rank_keyphrases(
    counts, top_n, exact_stopwords=None, prefix_stopwords=None, case_insensitive=True
):
    """
    Given a {keyword: count} Counter:
      1. filter out stopwords (if any given)
      2. merge casing variants of the same keyword (unless case_insensitive=False)
      3. return the top_n (keyword, count) tuples, most frequent first.
    """
    if exact_stopwords or prefix_stopwords:
        counts = filter_stopwords(counts, exact_stopwords or set(), prefix_stopwords or ())
    if case_insensitive:
        counts = consolidate_case_variants(counts)
    return counts.most_common(top_n)


def write_keyword_outputs(top_keywords, output_folder, base_name, write_json=False):
    """
    Write `top_keywords` (a list of (keyword, count) tuples, most frequent
    first) as a CSV (always) and, if write_json is True, as a companion
    JSON file with the same base name.

    Returns (csv_path, json_path_or_None).
    """
    df = pd.DataFrame(top_keywords, columns=["keyword", "count"])
    output_csv = os.path.join(output_folder, f"{base_name}_keywords.csv")
    df.to_csv(output_csv, index=False)
    print(f"Saved: {output_csv}")

    output_json = None
    if write_json:
        output_json = os.path.join(output_folder, f"{base_name}_keywords.json")
        payload = {
            "document": base_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "n_keyphrases": len(top_keywords),
            "keyphrases": [
                {"keyword": kw, "count": int(count), "rank": i + 1}
                for i, (kw, count) in enumerate(top_keywords)
            ],
        }
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"Saved: {output_json}")

    return output_csv, output_json


# -----------------------------
# Keyword Extraction Class
# -----------------------------
class KeywordExtraction:
    """
    Extracts keywords from a TXT file or folder of TXT files.
    """

    def __init__(
        self,
        input_path,
        output_folder,
        top_n=1000,
        stopwords_path=None,
        use_default_stopwords=True,
        output_json=False,
        case_insensitive=True,
    ):
        self.input_path = input_path
        self.output_folder = output_folder
        self.top_n = top_n
        self.output_json = output_json
        self.case_insensitive = case_insensitive
        self.exact_stopwords, self.prefix_stopwords = load_stopwords(
            custom_path=stopwords_path, use_defaults=use_default_stopwords
        )
        os.makedirs(self.output_folder, exist_ok=True)

        self.model_name = "ml6team/keyphrase-extraction-kbir-inspec"
        self.extractor = KeyphraseExtractionPipeline(model_name=self.model_name)

    def _read_text(self, file_path, method="sentence"):
        """
        Read a single TXT file and split into chunks/sentences.
        """
        with open(file_path, encoding="utf-8") as f:
            full_text = f.read().strip()

        if method == "sentence":
            text = re.split(r'(?<=[.!?])\s+', full_text)
        elif method == "chunk":
            words = full_text.split()
            chunk_size = 300
            text = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        else:
            text = [full_text]

        return text

    def _process_single_file(self, file_path):
        """
        Extract keywords from a single TXT file.
        """
        text_chunks = self._read_text(file_path, method="sentence")
        keyphrases = []

        for i in tqdm(range(0, len(text_chunks), 16), desc=f"Extracting {os.path.basename(file_path)}"):
            batch = text_chunks[i:i + 16]
            batch_phrases_list = self.extractor(batch, batch_size=16)
            for phrases in batch_phrases_list:
                keyphrases.extend(phrases)

        counts = Counter(keyphrases)
        top_keywords = rank_keyphrases(
            counts,
            self.top_n,
            self.exact_stopwords,
            self.prefix_stopwords,
            case_insensitive=self.case_insensitive,
        )

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_csv, output_json = write_keyword_outputs(
            top_keywords, self.output_folder, base_name, write_json=self.output_json
        )
        return output_csv

    def extract(self):
        """
        Handle single file or folder input automatically.
        """
        if os.path.isfile(self.input_path) and self.input_path.lower().endswith(".txt"):
            self._process_single_file(self.input_path)

        elif os.path.isdir(self.input_path):
            txt_files = [f for f in os.listdir(self.input_path) if f.lower().endswith(".txt")]
            print(f"Found {len(txt_files)} text files to process.\n")

            for txt_file in txt_files:
                file_path = os.path.join(self.input_path, txt_file)
                self._process_single_file(file_path)

            print(f"\nAll keyword CSVs saved in: {self.output_folder}")
        else:
            raise ValueError(" Please provide a valid TXT file or folder path.")

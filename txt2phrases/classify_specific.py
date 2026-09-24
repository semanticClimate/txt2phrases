import logging
import os
import pandas as pd
from collections import defaultdict
from argparse import ArgumentParser
from sklearn.feature_extraction.text import TfidfTransformer

logger = logging.getLogger(__name__)


def _consolidate_case_variants_per_chapter(raw_freq):
    """
    Merge casing variants of the same keyword (e.g. 'Age' in one chapter's
    CSV and 'age' in another's) into a single keyword, across ALL chapters.

    Without this, the same real-world keyword extracted with different
    casing in different chapters would be treated as two entirely separate
    keywords by the TF-IDF matrix below - which artificially concentrates
    each casing variant's (lower) count into whichever chapters happened to
    use that casing, making a genuinely shared/general keyword look
    falsely "specific" to each of those chapters instead.

    The display form kept for each group is the original-cased variant
    with the highest total count summed across all chapters (ties broken
    alphabetically, for deterministic output) - mirrors the equivalent
    logic in merge.py and keyword.py's consolidate_case_variants.

    Parameters
    ----------
    raw_freq : dict[str, dict[str, int]]
        {chapter: {keyword: count}}

    Returns
    -------
    dict[str, dict[str, int]]
        {chapter: {keyword: count}}, with casing variants merged and, where
        two variants land in the same chapter, their counts summed.
    """
    variant_totals = defaultdict(lambda: defaultdict(int))
    for kw_counts in raw_freq.values():
        for kw, count in kw_counts.items():
            variant_totals[kw.casefold()][kw] += count

    display_form = {
        cf_key: sorted(variants.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        for cf_key, variants in variant_totals.items()
    }

    consolidated = defaultdict(lambda: defaultdict(int))
    for chapter, kw_counts in raw_freq.items():
        for kw, count in kw_counts.items():
            consolidated[chapter][display_form[kw.casefold()]] += count

    return consolidated


def classify_keywords_split_files(
    input_dir, output_dir, threshold=0.6, min_freq=5, case_insensitive=True
):
    """
    For each chapter, create a separate CSV listing keywords that are 'specific' to it
    according to TF-IDF >= threshold. Also, create a single CSV with general/specific chapters.

    Input: multiple chapter CSVs in `input_dir`, each with columns: keyword, count
    Output:
        - <chapter>_specific_keywords.csv in `output_dir`
        - general_specific_keywords.csv in `output_dir`

    Parameters
    ----------
    case_insensitive : bool
        If True (default), keywords that differ only in case across
        different chapter CSVs (e.g. 'Age' in one file, 'age' in another)
        are treated as the same keyword before computing TF-IDF. If False,
        casing variants are kept as distinct keywords (the old behavior).
    """
    os.makedirs(output_dir, exist_ok=True)

    # --- Load per-chapter frequencies (raw, before min_freq filtering) ---
    chapter_files = [f for f in os.listdir(input_dir) if f.endswith(".csv")]
    if not chapter_files:
        logger.warning(f"No CSV files found in {input_dir}")
        return

    raw_freq = defaultdict(lambda: defaultdict(int))  # {chapter: {keyword: count}}
    chapters = []

    for file in chapter_files:
        chapter = os.path.splitext(file)[0]
        chapters.append(chapter)
        df = pd.read_csv(os.path.join(input_dir, file))
        if not {"keyword", "count"}.issubset(df.columns):
            raise ValueError(f"{file} must contain 'keyword' and 'count' columns")
        for _, row in df.iterrows():
            raw_freq[chapter][str(row["keyword"])] += int(row["count"])

    chapters = sorted(chapters)

    if case_insensitive:
        raw_freq = _consolidate_case_variants_per_chapter(raw_freq)

    # --- Apply min_freq filtering on the (possibly consolidated) counts ---
    keyword_chapter_freq = defaultdict(dict)  # {keyword: {chapter: count}}
    for chapter, kw_counts in raw_freq.items():
        for kw, count in kw_counts.items():
            if count >= min_freq:
                keyword_chapter_freq[kw][chapter] = count

    keywords = list(keyword_chapter_freq.keys())

    if not keywords:
        # create empty files if no keywords pass min_freq
        for chapter in chapters:
            pd.DataFrame(columns=["keyword", "tfidf", "count"]).to_csv(
                os.path.join(output_dir, f"{chapter}_specific_keywords.csv"), index=False
            )
        pd.DataFrame(columns=["keyword", "General", "Specific"]).to_csv(
            os.path.join(output_dir, "general_specific_keywords.csv"), index=False
        )
        logger.info("No keywords passed min_freq. Empty files created.")
        return

    # --- Build keyword x chapter matrix ---
    data = []
    for kw in keywords:
        row = [keyword_chapter_freq[kw].get(ch, 0) for ch in chapters]
        data.append(row)
    df_matrix = pd.DataFrame(data, index=keywords, columns=chapters)

    # --- TF-IDF over (keywords x chapters) ---
    transformer = TfidfTransformer()
    tfidf_matrix = transformer.fit_transform(df_matrix)  # sparse

    # --- For each chapter, collect specific keywords ---
    for j, chapter in enumerate(chapters):
        rows = []
        for i, keyword in enumerate(df_matrix.index):
            score = tfidf_matrix[i, j]
            freq_in_chapter = int(df_matrix.iloc[i, j])
            if score >= threshold and freq_in_chapter > 0:
                rows.append((keyword, float(score), freq_in_chapter))
        rows.sort(key=lambda x: (x[1], x[2]), reverse=True)
        pd.DataFrame(rows, columns=["keyword", "tfidf", "count"]).to_csv(
            os.path.join(output_dir, f"{chapter}_specific_keywords.csv"), index=False
        )
        logger.info(f"Saved {chapter}_specific_keywords.csv ({len(rows)} keywords)")

    # --- Generate general/specific keywords file ---
    general_specific_rows = []
    for i, keyword in enumerate(df_matrix.index):
        specific_chapters = []
        general_chapters = []
        for j, chapter in enumerate(chapters):
            score = tfidf_matrix[i, j]
            if score >= threshold:
                specific_chapters.append(chapter)
            else:
                general_chapters.append(chapter)
        general_specific_rows.append((
            keyword,
            " ".join(general_chapters),
            " ".join(specific_chapters)
        ))

    out_df = pd.DataFrame(general_specific_rows, columns=["keyword", "General", "Specific"])
    out_path = os.path.join(output_dir, "general_specific_keywords.csv")
    out_df.to_csv(out_path, index=False)
    logger.info(f"Saved general_specific_keywords.csv ({len(out_df)} keywords)")

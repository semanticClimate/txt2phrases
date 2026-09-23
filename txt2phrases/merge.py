# merge.py
"""
Merge multiple keyphrase CSV files (as produced by `txt2phrases keyphrases`)
into a single CSV, aggregating counts for duplicate keywords.

Input CSVs are expected to have `keyword` and `count` columns, matching the
output of txt2phrases.keyword.KeywordExtraction.
"""
import os
from pathlib import Path

import pandas as pd


def _collect_csv_paths(input_paths):
    """
    Normalize `input_paths` (a single path, a directory, or a list of paths)
    into a flat list of existing .csv file paths.
    """
    if isinstance(input_paths, (str, Path)):
        input_paths = [input_paths]

    csv_paths = []
    for raw_path in input_paths:
        path = Path(raw_path)
        if path.is_dir():
            found = sorted(path.glob("*.csv"))
            if not found:
                print(f"[WARN] No CSV files found in directory: {path}")
            csv_paths.extend(found)
        elif path.is_file() and path.suffix.lower() == ".csv":
            csv_paths.append(path)
        else:
            print(f"[WARN] Skipping invalid CSV path: {path}")

    return csv_paths


def _load_keyword_counts(csv_path):
    """
    Load a single keyword CSV and return a DataFrame with clean
    `keyword` (str) and `count` (int) columns. Rows with a missing
    keyword or a non-numeric count are dropped with a warning.
    """
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"[ERROR] Failed to read {csv_path}: {e}")
        return pd.DataFrame(columns=["keyword", "count"])

    if not {"keyword", "count"}.issubset(df.columns):
        print(f"[WARN] {csv_path} missing 'keyword'/'count' columns, skipping.")
        return pd.DataFrame(columns=["keyword", "count"])

    df = df[["keyword", "count"]].copy()
    df["keyword"] = df["keyword"].astype(str).str.strip()
    df = df[df["keyword"] != ""]

    df["count"] = pd.to_numeric(df["count"], errors="coerce")
    n_bad = df["count"].isna().sum()
    if n_bad:
        print(f"[WARN] {csv_path}: dropped {n_bad} row(s) with non-numeric count.")
    df = df.dropna(subset=["count"])
    df["count"] = df["count"].astype(int)

    return df


def _aggregate_case_insensitive(combined):
    """
    Group keywords case-insensitively (e.g. 'climate anxiety' and
    'Climate anxiety' are the same keyword), summing their counts.

    The display form for each group is chosen as the original-cased
    variant with the highest total count across all sources (ties
    broken alphabetically, for deterministic output). This keeps
    acronyms/proper nouns (e.g. 'CCAS', 'UK') in their natural casing
    as long as that casing is the (or a tied) dominant one, while still
    merging casing variants of ordinary phrases into a single row.
    """
    combined = combined.copy()
    combined["_group_key"] = combined["keyword"].str.lower()

    # Total count per (group_key, original-cased variant), to pick the
    # dominant display form for each group.
    variant_totals = (
        combined.groupby(["_group_key", "keyword"], as_index=False)["count"].sum()
    )
    variant_totals = variant_totals.sort_values(
        by=["_group_key", "count", "keyword"], ascending=[True, False, True]
    )
    display_forms = variant_totals.drop_duplicates(subset="_group_key", keep="first")
    display_forms = display_forms.rename(columns={"keyword": "_display_keyword"})[
        ["_group_key", "_display_keyword"]
    ]

    # Total count per group, across all casing variants.
    group_totals = combined.groupby("_group_key", as_index=False)["count"].sum()

    merged = group_totals.merge(display_forms, on="_group_key", how="left")
    merged = merged.rename(columns={"_display_keyword": "keyword"})[["keyword", "count"]]

    return merged


def merge_keyphrase_csvs(input_paths, output_path, top_n=None, sort_by="count", case_insensitive=True):
    """
    Merge one or more keyphrase CSV files into a single aggregated CSV.

    Parameters
    ----------
    input_paths : str | Path | list[str | Path]
        A single CSV file, a directory containing CSV files, or a list
        mixing either of those.
    output_path : str | Path
        Path to the merged output CSV.
    top_n : int | None
        If set, keep only the top N keywords after aggregation/sorting.
    sort_by : str
        'count' (default, descending) or 'keyword' (ascending, alphabetical).
    case_insensitive : bool
        If True (default), keywords that differ only in case (e.g.
        'climate anxiety' vs 'Climate anxiety') are merged into a single
        row, with counts summed and the most-frequent casing kept as the
        display form. If False, casing variants are kept as separate rows.

    Returns
    -------
    str | None
        Path to the written CSV, or None if nothing was merged.
    """
    if sort_by not in {"count", "keyword"}:
        raise ValueError("sort_by must be 'count' or 'keyword'")

    csv_paths = _collect_csv_paths(input_paths)
    if not csv_paths:
        print("[ERROR] No valid CSV files found to merge.")
        return None

    print(f"Merging {len(csv_paths)} CSV file(s)...")

    frames = [_load_keyword_counts(p) for p in csv_paths]
    combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=["keyword", "count"])

    if combined.empty:
        merged = pd.DataFrame(columns=["keyword", "count"])
    else:
        if case_insensitive:
            merged = _aggregate_case_insensitive(combined)
        else:
            merged = combined.groupby("keyword", as_index=False)["count"].sum()

        if sort_by == "count":
            merged = merged.sort_values(by=["count", "keyword"], ascending=[False, True])
        else:
            merged = merged.sort_values(by="keyword", ascending=True)

        merged = merged.reset_index(drop=True)

        if top_n is not None:
            merged = merged.head(top_n)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False)

    print(f"Saved merged CSV: {output_path} ({len(merged)} unique keywords)")
    return str(output_path)

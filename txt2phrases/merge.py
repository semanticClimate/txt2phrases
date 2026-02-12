"""
Merge keyphrase CSV files with aggregated counts.

Input CSVs must have columns: keyword, count.
Output CSV has columns: keyword, count (aggregated).
"""
from pathlib import Path
from typing import Union, List, Optional

import pandas as pd


REQUIRED_COLUMNS = {"keyword", "count"}


def _resolve_input_paths(input_paths: Union[Path, List[Path]]) -> List[Path]:
    """Return a list of CSV file paths from input_paths (list of files or single directory)."""
    if isinstance(input_paths, Path):
        if not input_paths.exists():
            raise FileNotFoundError(f"Input path does not exist: {input_paths}")
        if input_paths.is_dir():
            files = sorted(input_paths.glob("*.csv"))
            if not files:
                raise ValueError(f"No CSV files found in directory: {input_paths}")
            return files
        return [input_paths]

    if not input_paths:
        raise ValueError("No files to merge: input_paths is empty")
    return list(input_paths)


def _read_and_validate_csv(path: Path) -> pd.DataFrame:
    """Read a CSV and validate it has required columns. Raise ValueError if not."""
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required column(s) {sorted(missing)}: {path}")
    return df[["keyword", "count"]]


def merge_keyphrase_csvs(
    input_paths: Union[Path, List[Path]],
    output_path: Path,
    top_n: Optional[int] = None,
    sort_by: str = "count",
) -> None:
    """
    Merge one or more keyword CSVs (columns: keyword, count) into one CSV with aggregated counts.

    :param input_paths: List of CSV file paths, or a single directory Path (will glob for *.csv).
    :param output_path: Path for the merged output CSV.
    :param top_n: If set, keep only the top N keywords by count (descending).
    :param sort_by: 'count' (descending) or 'keyword' (ascending). Default 'count'.
    """
    paths = _resolve_input_paths(input_paths)
    frames = [_read_and_validate_csv(p) for p in paths]
    combined = pd.concat(frames, ignore_index=True)

    aggregated = (
        combined.groupby("keyword", as_index=False)["count"]
        .sum()
        .astype({"count": "int64"})
    )

    if sort_by == "count":
        aggregated = aggregated.sort_values("count", ascending=False)
    else:
        aggregated = aggregated.sort_values("keyword", ascending=True)

    if top_n is not None:
        aggregated = aggregated.head(top_n)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    aggregated.to_csv(output_path, index=False)

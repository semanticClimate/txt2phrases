"""
Phase A tests for merge keyphrase CSV functionality.

Tests drive merge_keyphrase_csvs() in txt2phrases.merge.
Input CSVs have columns: keyword, count.
Output CSV has columns: keyword, count (aggregated).
"""
import pytest
import pandas as pd
from pathlib import Path

from txt2phrases.merge import merge_keyphrase_csvs


class TestMergeKeyphraseCsvsEmptyAndSingle:
    """Empty input and single-file behaviour."""

    def test_empty_input_no_files_raises(self, temp_output_dir):
        """Empty list of input paths raises a clear error (no files to merge)."""
        output_path = Path(temp_output_dir, "merged.csv")
        with pytest.raises((ValueError, FileNotFoundError)) as exc_info:
            merge_keyphrase_csvs(input_paths=[], output_path=output_path)
        assert "empty" in str(exc_info.value).lower() or "no file" in str(exc_info.value).lower(), (
            f"Expected error message to mention empty or no files, got: {exc_info.value}"
        )

    def test_single_csv_passthrough(self, temp_output_dir):
        """Single CSV: output has same keyword/count rows and correct columns."""
        csv_path = Path(temp_output_dir, "single_keywords.csv")
        pd.DataFrame([["climate change", 10], ["machine learning", 8]], columns=["keyword", "count"]).to_csv(
            csv_path, index=False
        )
        output_path = Path(temp_output_dir, "merged.csv")

        merge_keyphrase_csvs(input_paths=[csv_path], output_path=output_path)

        assert output_path.exists(), f"Merged output file {output_path} should exist"
        df = pd.read_csv(output_path)
        assert list(df.columns) == ["keyword", "count"], (
            f"Merged CSV should have columns ['keyword', 'count'], got {list(df.columns)}"
        )
        assert len(df) == 2, f"Merged CSV should have 2 rows for single file, got {len(df)}"
        row0 = df[df["keyword"] == "climate change"].iloc[0]
        assert int(row0["count"]) == 10, f"Expected count 10 for 'climate change', got {row0['count']}"


class TestMergeKeyphraseCsvsAggregation:
    """Two or more CSVs: concatenation and count aggregation."""

    def test_two_csvs_no_overlap_concatenation(self, temp_output_dir):
        """Two CSVs with no overlapping keywords: output has all rows, counts unchanged."""
        dir_path = Path(temp_output_dir, "inputs")
        dir_path.mkdir(parents=True, exist_ok=True)
        Path(dir_path, "a_keywords.csv").write_text("keyword,count\na,1\nb,2\n")
        Path(dir_path, "b_keywords.csv").write_text("keyword,count\nc,3\n")
        output_path = Path(temp_output_dir, "merged.csv")

        merge_keyphrase_csvs(input_paths=[Path(dir_path, "a_keywords.csv"), Path(dir_path, "b_keywords.csv")], output_path=output_path)

        df = pd.read_csv(output_path)
        assert len(df) == 3, f"Expected 3 keywords (a,b,c), got {len(df)}"
        counts = dict(zip(df["keyword"], df["count"].astype(int)))
        assert counts == {"a": 1, "b": 2, "c": 3}, f"Expected {{'a':1,'b':2,'c':3}}, got {counts}"

    def test_two_csvs_overlapping_keywords_aggregated(self, temp_output_dir):
        """Two CSVs with overlapping keywords: counts are summed per keyword."""
        dir_path = Path(temp_output_dir, "inputs")
        dir_path.mkdir(parents=True, exist_ok=True)
        Path(dir_path, "f1.csv").write_text("keyword,count\na,1\nb,2\n")
        Path(dir_path, "f2.csv").write_text("keyword,count\na,3\nb,1\n")
        output_path = Path(temp_output_dir, "merged.csv")

        merge_keyphrase_csvs(input_paths=[Path(dir_path, "f1.csv"), Path(dir_path, "f2.csv")], output_path=output_path)

        df = pd.read_csv(output_path)
        assert len(df) == 2, f"Expected 2 unique keywords (a,b), got {len(df)}"
        counts = dict(zip(df["keyword"], df["count"].astype(int)))
        assert counts["a"] == 4, f"Aggregated count for 'a' should be 4, got {counts.get('a')}"
        assert counts["b"] == 3, f"Aggregated count for 'b' should be 3, got {counts.get('b')}"


class TestMergeKeyphraseCsvsOutputShape:
    """Output columns and ordering."""

    def test_output_has_keyword_and_count_columns_only(self, temp_output_dir):
        """Merged CSV has exactly 'keyword' and 'count' columns."""
        csv_path = Path(temp_output_dir, "one.csv")
        pd.DataFrame([["x", 5]], columns=["keyword", "count"]).to_csv(csv_path, index=False)
        output_path = Path(temp_output_dir, "out.csv")

        merge_keyphrase_csvs(input_paths=[csv_path], output_path=output_path)

        df = pd.read_csv(output_path)
        assert set(df.columns) == {"keyword", "count"}, (
            f"Merged output should have only 'keyword' and 'count', got {set(df.columns)}"
        )

    def test_output_sorted_by_count_descending_by_default(self, temp_output_dir):
        """Merged output is sorted by count descending (highest first)."""
        csv_path = Path(temp_output_dir, "one.csv")
        pd.DataFrame([["low", 1], ["high", 10], ["mid", 5]], columns=["keyword", "count"]).to_csv(
            csv_path, index=False
        )
        output_path = Path(temp_output_dir, "out.csv")

        merge_keyphrase_csvs(input_paths=[csv_path], output_path=output_path)

        df = pd.read_csv(output_path)
        counts = list(df["count"].astype(int))
        assert counts == [10, 5, 1], f"Expected counts descending [10,5,1], got {counts}"


class TestMergeKeyphraseCsvsDirectoryInput:
    """Input as directory: all keyword CSVs in directory are merged."""

    def test_directory_input_merges_all_keyword_csvs(self, temp_output_dir):
        """When input is a directory path, all *_keywords.csv (or *.csv) in it are merged."""
        dir_path = Path(temp_output_dir, "keyword_dir")
        dir_path.mkdir(parents=True, exist_ok=True)
        Path(dir_path, "ch1_keywords.csv").write_text("keyword,count\nalpha,2\nbeta,1\n")
        Path(dir_path, "ch2_keywords.csv").write_text("keyword,count\nalpha,3\ngamma,4\n")
        output_path = Path(temp_output_dir, "merged.csv")

        merge_keyphrase_csvs(input_paths=dir_path, output_path=output_path)

        assert output_path.exists(), f"Merged output {output_path} should exist when merging directory"
        df = pd.read_csv(output_path)
        counts = dict(zip(df["keyword"], df["count"].astype(int)))
        assert counts["alpha"] == 5, f"Aggregated 'alpha' across directory should be 5, got {counts.get('alpha')}"
        assert counts["beta"] == 1 and counts["gamma"] == 4, f"Expected beta=1, gamma=4; got {counts}"


class TestMergeKeyphraseCsvsInvalidInput:
    """Invalid or malformed input raises clear errors."""

    def test_csv_missing_count_column_raises(self, temp_output_dir):
        """CSV with wrong columns (e.g. no 'count') raises a clear error."""
        bad_path = Path(temp_output_dir, "bad.csv")
        bad_path.write_text("keyword,tfidf\nx,0.5\n")
        output_path = Path(temp_output_dir, "out.csv")

        with pytest.raises((ValueError, KeyError)) as exc_info:
            merge_keyphrase_csvs(input_paths=[bad_path], output_path=output_path)

        msg = str(exc_info.value).lower()
        assert "count" in msg or "column" in msg, (
            f"Error message should mention missing 'count' or columns, got: {exc_info.value}"
        )

    def test_csv_missing_keyword_column_raises(self, temp_output_dir):
        """CSV with no 'keyword' column raises a clear error."""
        bad_path = Path(temp_output_dir, "bad.csv")
        bad_path.write_text("phrase,count\nx,1\n")
        output_path = Path(temp_output_dir, "out.csv")

        with pytest.raises((ValueError, KeyError)) as exc_info:
            merge_keyphrase_csvs(input_paths=[bad_path], output_path=output_path)

        msg = str(exc_info.value).lower()
        assert "keyword" in msg or "column" in msg, (
            f"Error message should mention missing 'keyword' or columns, got: {exc_info.value}"
        )


class TestMergeKeyphraseCsvsTopN:
    """Optional top_n parameter limits output rows."""

    def test_top_n_limits_output_rows(self, temp_output_dir):
        """With top_n=2, output has at most 2 data rows (highest counts)."""
        csv_path = Path(temp_output_dir, "many.csv")
        pd.DataFrame(
            [["a", 1], ["b", 10], ["c", 5], ["d", 3]],
            columns=["keyword", "count"],
        ).to_csv(csv_path, index=False)
        output_path = Path(temp_output_dir, "top2.csv")

        merge_keyphrase_csvs(input_paths=[csv_path], output_path=output_path, top_n=2)

        df = pd.read_csv(output_path)
        assert len(df) == 2, f"With top_n=2 expected 2 rows, got {len(df)}"
        # Should be b (10) and c (5)
        keywords = set(df["keyword"])
        assert "b" in keywords and "c" in keywords, f"Expected top two keywords b and c, got {keywords}"


class TestMergeKeyphraseCsvsEmptyFiles:
    """Empty CSV files do not crash merge."""

    def test_empty_csv_file_produces_empty_or_header_only_output(self, temp_output_dir):
        """One valid CSV with no data rows: merge succeeds; output is empty or header-only."""
        empty_path = Path(temp_output_dir, "empty_keywords.csv")
        pd.DataFrame(columns=["keyword", "count"]).to_csv(empty_path, index=False)
        output_path = Path(temp_output_dir, "merged.csv")

        merge_keyphrase_csvs(input_paths=[empty_path], output_path=output_path)

        assert output_path.exists(), f"Merge with empty CSV should still create output file {output_path}"
        df = pd.read_csv(output_path)
        assert list(df.columns) == ["keyword", "count"], f"Output should have keyword, count columns, got {list(df.columns)}"
        assert len(df) == 0, f"Output should have no data rows when input is empty, got {len(df)}"

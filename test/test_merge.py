# Unit tests for the merge module and CLI command.
import sys
from pathlib import Path

import pandas as pd
import pytest

from txt2phrases.merge import merge_keyphrase_csvs
from txt2phrases.cli import main


def _write_csv(path, rows):
    """Helper: write a keyword/count CSV from a list of (keyword, count) tuples."""
    pd.DataFrame(rows, columns=["keyword", "count"]).to_csv(path, index=False)
    return path


class TestMergeFunction:
    """Tests for merge_keyphrase_csvs()."""

    def test_merge_two_files_aggregates_counts(self, temp_output_dir):
        f1 = _write_csv(Path(temp_output_dir, "a_keywords.csv"), [("climate", 5), ("ocean", 2)])
        f2 = _write_csv(Path(temp_output_dir, "b_keywords.csv"), [("climate", 3), ("forest", 1)])
        out = Path(temp_output_dir, "merged.csv")

        result_path = merge_keyphrase_csvs([f1, f2], out)

        assert result_path == str(out)
        df = pd.read_csv(out)
        row = df[df["keyword"] == "climate"].iloc[0]
        assert int(row["count"]) == 8, "counts for duplicate keyword should be summed"
        assert set(df["keyword"]) == {"climate", "ocean", "forest"}

    def test_merge_directory_input(self, temp_output_dir):
        csv_dir = Path(temp_output_dir, "csvs")
        csv_dir.mkdir()
        _write_csv(Path(csv_dir, "a_keywords.csv"), [("drought", 4)])
        _write_csv(Path(csv_dir, "b_keywords.csv"), [("drought", 1), ("flood", 2)])
        out = Path(temp_output_dir, "merged_dir.csv")

        merge_keyphrase_csvs(csv_dir, out)

        df = pd.read_csv(out)
        assert int(df[df["keyword"] == "drought"]["count"].iloc[0]) == 5
        assert len(df) == 2

    def test_merge_top_n_filters_results(self, temp_output_dir):
        f1 = _write_csv(
            Path(temp_output_dir, "a_keywords.csv"),
            [("a", 10), ("b", 5), ("c", 1)],
        )
        out = Path(temp_output_dir, "merged_topn.csv")

        merge_keyphrase_csvs([f1], out, top_n=2)

        df = pd.read_csv(out)
        assert len(df) == 2
        assert list(df["keyword"]) == ["a", "b"], "top-N by count should keep the highest counts"

    def test_merge_sort_by_keyword(self, temp_output_dir):
        f1 = _write_csv(
            Path(temp_output_dir, "a_keywords.csv"),
            [("zebra", 1), ("apple", 1)],
        )
        out = Path(temp_output_dir, "merged_sorted.csv")

        merge_keyphrase_csvs([f1], out, sort_by="keyword")

        df = pd.read_csv(out)
        assert list(df["keyword"]) == ["apple", "zebra"]

    def test_merge_invalid_sort_by_raises(self, temp_output_dir):
        f1 = _write_csv(Path(temp_output_dir, "a_keywords.csv"), [("x", 1)])
        out = Path(temp_output_dir, "merged.csv")

        with pytest.raises(ValueError):
            merge_keyphrase_csvs([f1], out, sort_by="not_a_valid_option")

    def test_merge_no_valid_csvs_returns_none(self, temp_output_dir):
        empty_dir = Path(temp_output_dir, "empty")
        empty_dir.mkdir()
        out = Path(temp_output_dir, "merged.csv")

        result = merge_keyphrase_csvs(empty_dir, out)

        assert result is None

    def test_merge_skips_malformed_csv(self, temp_output_dir):
        good = _write_csv(Path(temp_output_dir, "good_keywords.csv"), [("flood", 3)])
        bad = Path(temp_output_dir, "bad_keywords.csv")
        pd.DataFrame({"not_keyword": ["x"], "not_count": [1]}).to_csv(bad, index=False)
        out = Path(temp_output_dir, "merged.csv")

        result = merge_keyphrase_csvs([good, bad], out)

        assert result == str(out)
        df = pd.read_csv(out)
        assert list(df["keyword"]) == ["flood"]

    def test_merge_drops_non_numeric_counts(self, temp_output_dir):
        path = Path(temp_output_dir, "mixed_keywords.csv")
        pd.DataFrame(
            {"keyword": ["heat", "wave"], "count": [5, "not_a_number"]}
        ).to_csv(path, index=False)
        out = Path(temp_output_dir, "merged.csv")

        merge_keyphrase_csvs([path], out)

        df = pd.read_csv(out)
        assert list(df["keyword"]) == ["heat"]

    def test_merge_case_insensitive_sums_variants(self, temp_output_dir):
        """'climate anxiety' and 'Climate anxiety' should merge into one row by default."""
        f1 = _write_csv(
            Path(temp_output_dir, "a_keywords.csv"),
            [("climate anxiety", 100), ("Climate anxiety", 20), ("women", 25)],
        )
        f2 = _write_csv(
            Path(temp_output_dir, "b_keywords.csv"),
            [("climate anxiety", 45), ("Women", 5)],
        )
        out = Path(temp_output_dir, "merged.csv")

        merge_keyphrase_csvs([f1, f2], out)

        df = pd.read_csv(out)
        assert len(df) == 2, "case variants should be merged into single rows"
        assert int(df[df["keyword"].str.lower() == "climate anxiety"]["count"].iloc[0]) == 165
        assert int(df[df["keyword"].str.lower() == "women"]["count"].iloc[0]) == 30

    def test_merge_case_insensitive_keeps_dominant_casing(self, temp_output_dir):
        """The display form should be the casing variant with the highest total count."""
        f1 = _write_csv(
            Path(temp_output_dir, "a_keywords.csv"),
            [("climate anxiety", 5), ("Climate anxiety", 100)],
        )
        out = Path(temp_output_dir, "merged.csv")

        merge_keyphrase_csvs([f1], out)

        df = pd.read_csv(out)
        assert df["keyword"].iloc[0] == "Climate anxiety", (
            "display form should be the variant with the higher total count"
        )
        assert int(df["count"].iloc[0]) == 105

    def test_merge_case_insensitive_preserves_acronyms(self, temp_output_dir):
        """A keyword with only one casing variant (e.g. an acronym) should be unaffected."""
        f1 = _write_csv(Path(temp_output_dir, "a_keywords.csv"), [("CCAS", 16), ("UK", 14)])
        out = Path(temp_output_dir, "merged.csv")

        merge_keyphrase_csvs([f1], out)

        df = pd.read_csv(out)
        assert set(df["keyword"]) == {"CCAS", "UK"}

    def test_merge_case_sensitive_opt_out(self, temp_output_dir):
        """case_insensitive=False should preserve the old exact-match behavior."""
        f1 = _write_csv(
            Path(temp_output_dir, "a_keywords.csv"),
            [("climate anxiety", 100), ("Climate anxiety", 20)],
        )
        out = Path(temp_output_dir, "merged.csv")

        merge_keyphrase_csvs([f1], out, case_insensitive=False)

        df = pd.read_csv(out)
        assert len(df) == 2, "case-sensitive mode should keep variants as separate rows"
        assert set(df["keyword"]) == {"climate anxiety", "Climate anxiety"}


class TestCliMergeCaseSensitivity:
    """Tests for the `--case-sensitive` CLI flag."""

    def test_merge_cli_default_is_case_insensitive(self, temp_output_dir):
        f1 = _write_csv(
            Path(temp_output_dir, "a_keywords.csv"),
            [("climate change", 10), ("Climate Change", 5)],
        )
        out = Path(temp_output_dir, "merged.csv")

        sys.argv = ["txt2phrases", "merge", "-i", str(f1), "-o", str(out)]
        main()

        df = pd.read_csv(out)
        assert len(df) == 1
        assert int(df["count"].iloc[0]) == 15

    def test_merge_cli_case_sensitive_flag(self, temp_output_dir):
        f1 = _write_csv(
            Path(temp_output_dir, "a_keywords.csv"),
            [("climate change", 10), ("Climate Change", 5)],
        )
        out = Path(temp_output_dir, "merged.csv")

        sys.argv = ["txt2phrases", "merge", "-i", str(f1), "-o", str(out), "--case-sensitive"]
        main()

        df = pd.read_csv(out)
        assert len(df) == 2


class TestCliMerge:
    """Tests for the `txt2phrases merge` CLI command."""

    def test_merge_cli_directory(self, temp_output_dir, capsys):
        csv_dir = Path(temp_output_dir, "csvs")
        csv_dir.mkdir()
        _write_csv(Path(csv_dir, "a_keywords.csv"), [("emissions", 2)])
        _write_csv(Path(csv_dir, "b_keywords.csv"), [("emissions", 3)])
        out = Path(temp_output_dir, "merged.csv")

        sys.argv = ["txt2phrases", "merge", "-i", str(csv_dir), "-o", str(out)]
        main()

        captured = capsys.readouterr()
        assert "Saved merged CSV" in captured.out
        assert out.exists()
        df = pd.read_csv(out)
        assert int(df[df["keyword"] == "emissions"]["count"].iloc[0]) == 5

    def test_merge_cli_multiple_files(self, temp_output_dir, capsys):
        f1 = _write_csv(Path(temp_output_dir, "a_keywords.csv"), [("carbon", 1)])
        f2 = _write_csv(Path(temp_output_dir, "b_keywords.csv"), [("carbon", 1)])
        out = Path(temp_output_dir, "merged.csv")

        sys.argv = ["txt2phrases", "merge", "-i", str(f1), str(f2), "-o", str(out)]
        main()

        df = pd.read_csv(out)
        assert int(df[df["keyword"] == "carbon"]["count"].iloc[0]) == 2

    def test_merge_cli_top_n_option(self, temp_output_dir):
        f1 = _write_csv(
            Path(temp_output_dir, "a_keywords.csv"),
            [("a", 10), ("b", 5), ("c", 1)],
        )
        out = Path(temp_output_dir, "merged.csv")

        sys.argv = ["txt2phrases", "merge", "-i", str(f1), "-o", str(out), "--top-n", "1"]
        main()

        df = pd.read_csv(out)
        assert len(df) == 1
        assert df["keyword"].iloc[0] == "a"

    def test_merge_cli_missing_args(self, capsys):
        sys.argv = ["txt2phrases", "merge"]

        with pytest.raises(SystemExit):
            main()

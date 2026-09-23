# Unit tests for stopword filtering.
from pathlib import Path

from txt2phrases.stopwords import load_stopwords, is_stopword, filter_stopwords


class TestLoadStopwords:
    def test_defaults_only(self):
        exact, prefixes = load_stopwords()
        assert "bmc psychology" in exact
        assert "journal of " in prefixes

    def test_no_defaults_no_custom_is_empty(self):
        exact, prefixes = load_stopwords(use_defaults=False)
        assert exact == set()
        assert prefixes == tuple()

    def test_custom_file_merged_with_defaults(self, tmp_path):
        custom = tmp_path / "custom_stopwords.txt"
        custom.write_text("CCAS\nOutcome Risk\n# a comment\n\n")

        exact, prefixes = load_stopwords(custom_path=custom)

        assert "ccas" in exact
        assert "outcome risk" in exact
        assert "bmc psychology" in exact, "defaults should still be present"

    def test_custom_file_without_defaults(self, tmp_path):
        custom = tmp_path / "custom_stopwords.txt"
        custom.write_text("CCAS\n")

        exact, prefixes = load_stopwords(custom_path=custom, use_defaults=False)

        assert exact == {"ccas"}
        assert prefixes == tuple()

    def test_custom_file_ignores_comments_and_blank_lines(self, tmp_path):
        custom = tmp_path / "custom_stopwords.txt"
        custom.write_text("# comment\n\nreal term\n   \n")

        exact, _ = load_stopwords(custom_path=custom, use_defaults=False)

        assert exact == {"real term"}


class TestIsStopword:
    def test_exact_match_case_insensitive(self):
        exact, prefixes = load_stopwords()
        assert is_stopword("BMC Psychology", exact, prefixes) is True
        assert is_stopword("bmc psychology", exact, prefixes) is True
        assert is_stopword("Bmc Psychology", exact, prefixes) is True

    def test_prefix_match(self):
        exact, prefixes = load_stopwords()
        assert is_stopword("Journal of Environmental Psychology", exact, prefixes) is True
        assert is_stopword("journal of climate anxiety studies", exact, prefixes) is True

    def test_real_content_not_filtered(self):
        exact, prefixes = load_stopwords()
        assert is_stopword("climate anxiety", exact, prefixes) is False
        assert is_stopword("mental health", exact, prefixes) is False
        assert is_stopword("public health policy", exact, prefixes) is False, (
            "should not be filtered just because it shares a word with a journal name"
        )

    def test_empty_string_is_stopword(self):
        exact, prefixes = load_stopwords()
        assert is_stopword("", exact, prefixes) is True
        assert is_stopword("   ", exact, prefixes) is True


class TestFilterStopwords:
    def test_filters_counter(self):
        from collections import Counter

        counts = Counter({"climate anxiety": 100, "BMC Psychology": 13, "women": 32})
        exact, prefixes = load_stopwords()

        filtered = filter_stopwords(counts, exact, prefixes)

        assert "BMC Psychology" not in filtered
        assert filtered["climate anxiety"] == 100
        assert filtered["women"] == 32

    def test_does_not_mutate_input(self):
        from collections import Counter

        counts = Counter({"BMC Psychology": 13, "climate anxiety": 100})
        exact, prefixes = load_stopwords()

        filter_stopwords(counts, exact, prefixes)

        assert "BMC Psychology" in counts, "original Counter should be untouched"

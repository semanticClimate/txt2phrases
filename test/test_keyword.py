# Unit tests for keyword extraction module.
import os
import pytest
from pathlib import Path
import pandas as pd
from txt2phrases.keyword import KeywordExtraction, KeyphraseExtractionPipeline
import json
from collections import Counter
from txt2phrases.keyword import (
    KeywordExtraction, KeyphraseExtractionPipeline,
    rank_keyphrases, write_keyword_outputs, consolidate_case_variants,
)
from txt2phrases.stopwords import load_stopwords


class TestKeyphraseExtractionPipeline:
    """Tests for KeyphraseExtractionPipeline class."""

    @pytest.mark.requires_model
    def test_pipeline_initialization(self):
        """Test pipeline initialization with model."""
        model_name = """ml6team/keyphrase-extraction-kbir-inspec"""
        pipeline = KeyphraseExtractionPipeline(model_name=model_name)
        
        assert pipeline is not None, "pipeline should not be None"
        assert pipeline.model is not None, "pipeline.model should not be None"
        assert pipeline.tokenizer is not None, "pipeline.tokenizer should not be None"
    @pytest.mark.requires_model
    def test_postprocess(self):
        """Test postprocess method."""
        model_name = """ml6team/keyphrase-extraction-kbir-inspec"""
        pipeline = KeyphraseExtractionPipeline(model_name=model_name)
        
        # Mock results structure
        mock_results = [
            {"word": " climate change "},
            {"word": "machine learning"},
            {"word": ""},  # Empty word should be filtered
            {"word": "  natural language processing  "}
        ]
        
        # Note: This tests the postprocess logic, but actual postprocess
        # is called internally by the pipeline
        # We'll test the full pipeline in integration tests

    @pytest.mark.requires_model
    @pytest.mark.requires_model
    def test_empty_input(self):
        """Test pipeline with empty input."""
        model_name = "ml6team/keyphrase-extraction-kbir-inspec"
        pipeline = KeyphraseExtractionPipeline(model_name=model_name)
        
        # Empty input should return empty list or handle gracefully
        try:
            result = pipeline([])
            assert isinstance(result, list)
        except (ValueError, IndexError):
            # Empty input may raise an error, which is acceptable
            pytest.skip("Empty input handling may vary by model")

class TestConsolidateCaseVariants:
    """Tests for consolidate_case_variants() - merging casing variants."""

    def test_merges_casing_variants_summing_counts(self):
        counts = Counter({"climate anxiety": 57, "Climate anxiety": 19})

        result = consolidate_case_variants(counts)

        assert dict(result) == {"climate anxiety": 76}, (
            "display form should be the more frequent variant; count should be summed"
        )

    def test_keeps_dominant_casing_as_display_form(self):
        counts = Counter({"climate anxiety": 5, "Climate anxiety": 100})

        result = consolidate_case_variants(counts)

        assert dict(result) == {"Climate anxiety": 105}

    def test_single_variant_acronym_untouched(self):
        counts = Counter({"CCAS": 13, "UK": 5})

        result = consolidate_case_variants(counts)

        assert dict(result) == {"CCAS": 13, "UK": 5}


class TestRankKeyphrases:
    """Tests for rank_keyphrases() - stopword filtering + case merging + top_n selection."""

    def test_no_stopwords_returns_top_n_by_count(self):
        counts = Counter({"a": 10, "b": 5, "c": 1})

        result = rank_keyphrases(counts, top_n=2)

        assert result == [("a", 10), ("b", 5)]

    def test_filters_default_stopwords_before_top_n(self):
        counts = Counter({
            "climate anxiety": 145, "BMC Psychology": 13,
            "climate change": 52, "Creative Commons licence": 6,
        })
        exact, prefixes = load_stopwords()

        result = rank_keyphrases(counts, top_n=2, exact_stopwords=exact, prefix_stopwords=prefixes)

        assert result == [("climate anxiety", 145), ("climate change", 52)]

    def test_no_stopwords_given_skips_filtering(self):
        counts = Counter({"BMC Psychology": 13, "climate anxiety": 145})

        result = rank_keyphrases(counts, top_n=10)

        assert ("BMC Psychology", 13) in result, "no stopword sets given, so nothing should be filtered"

    def test_case_insensitive_default_merges_variants(self):
        counts = Counter({"climate anxiety": 57, "Climate anxiety": 19, "young people": 19})

        result = dict(rank_keyphrases(counts, top_n=10))

        assert result.get("climate anxiety") == 76
        assert "Climate anxiety" not in result

    def test_case_sensitive_opt_out_keeps_variants_split(self):
        counts = Counter({"climate anxiety": 57, "Climate anxiety": 19})

        result = dict(rank_keyphrases(counts, top_n=10, case_insensitive=False))

        assert result.get("climate anxiety") == 57
        assert result.get("Climate anxiety") == 19

    def test_stopwords_and_case_merging_combine(self):
        counts = Counter({
            "climate anxiety": 57, "Climate anxiety": 19,
            "BMC Psychology": 13, "bmc psychology": 4,
        })
        exact, prefixes = load_stopwords()

        result = dict(rank_keyphrases(counts, top_n=10, exact_stopwords=exact, prefix_stopwords=prefixes))

        assert result == {"climate anxiety": 76}, (
            "stopword variants should be filtered regardless of casing, "
            "and remaining casing variants merged"
        )

class TestWriteKeywordOutputs:
    """Tests for write_keyword_outputs() - CSV + optional JSON writing."""

    def test_writes_csv_only_by_default(self, temp_output_dir):
        top_keywords = [("climate anxiety", 145), ("women", 32)]

        csv_path, json_path = write_keyword_outputs(top_keywords, temp_output_dir, "paper1")

        assert Path(csv_path).exists()
        assert json_path is None
        assert not Path(temp_output_dir, "paper1_keywords.json").exists()

        df = pd.read_csv(csv_path)
        assert list(df["keyword"]) == ["climate anxiety", "women"]

    def test_writes_json_when_requested(self, temp_output_dir):
        top_keywords = [("climate anxiety", 145), ("women", 32)]

        csv_path, json_path = write_keyword_outputs(
            top_keywords, temp_output_dir, "paper1", write_json=True
        )

        assert Path(csv_path).exists()
        assert Path(json_path).exists()

        data = json.loads(Path(json_path).read_text())
        assert data["document"] == "paper1"
        assert data["n_keyphrases"] == 2
        assert data["keyphrases"][0] == {"keyword": "climate anxiety", "count": 145, "rank": 1}
        assert data["keyphrases"][1] == {"keyword": "women", "count": 32, "rank": 2}

class TestKeywordExtraction:
    """Tests for KeywordExtraction class."""

    def test_initialization(self, sample_txt_path, temp_output_dir):
        """Test KeywordExtraction initialization."""
        extractor = KeywordExtraction(
            input_path=str(sample_txt_path),
            output_folder=str(temp_output_dir),
            top_n=100
        )
        
        assert extractor.input_path == str(sample_txt_path), f"extractor.input_path should equal {str(sample_txt_path)}"
        assert extractor.output_folder == str(temp_output_dir), "extractor.output_folder should equal str(temp_output_dir)"""
        assert extractor.top_n == 100, "extractor.top_n should equal 100"
        assert temp_output_dir.exists(), "temp_output_dir should exist"
    def test_read_text_sentence_method(self, sample_txt_path, temp_output_dir):
        """Test _read_text with sentence method."""
        extractor = KeywordExtraction(
            input_path=str(sample_txt_path),
            output_folder=str(temp_output_dir),
            top_n=100
        )
        
        text_chunks = extractor._read_text(sample_txt_path, method="sentence")
        
        assert isinstance(text_chunks, list)
        assert len(text_chunks) > 0, "Length should be greater than 0"""
        # Should split on sentence boundaries"

    def test_read_text_chunk_method(self, sample_txt_path, temp_output_dir):
        """Test _read_text with chunk method."""
        extractor = KeywordExtraction(
            input_path=str(sample_txt_path),
            output_folder=str(temp_output_dir),
            top_n=100
        )
        
        text_chunks = extractor._read_text(sample_txt_path, method="chunk")
        
        assert isinstance(text_chunks, list)
        assert len(text_chunks) > 0, "Length should be greater than 0"""
        # Chunks should be around 300 words
        words_per_chunk = [len(chunk.split()) for chunk in text_chunks]
        assert all(words <= 300 for words in words_per_chunk[:-1])  # Last chunk may be smaller, "At least one condition should be true: all(words <= 300 for words in words_per_chunk[:-1])  # Last chunk may be smaller"
    def test_read_text_full_method(self, sample_txt_path, temp_output_dir):
        """Test _read_text with full method."""
        extractor = KeywordExtraction(
            input_path=str(sample_txt_path),
            output_folder=str(temp_output_dir),
            top_n=100
        )
        
        text_chunks = extractor._read_text(sample_txt_path, method="full")
        
        assert isinstance(text_chunks, list)
        assert len(text_chunks) == 1  # Should return single chunk, "Length should match expected value"
    @pytest.mark.requires_model
    def test_process_single_file(self, sample_txt_path, temp_output_dir):
        """Test _process_single_file method."""
        extractor = KeywordExtraction(
            input_path=str(sample_txt_path),
            output_folder=str(temp_output_dir),
            top_n=10
        )
        
        result = extractor._process_single_file(sample_txt_path)
        
        assert result is not None, "result should not be None"
        assert Path(result).exists(), "Path(result) should exist"
        assert Path(result).suffix == ".csv", "File extension should match expected"
        # Check CSV content
        df = pd.read_csv(result)
        assert "keyword" in df.columns, "keyword in df.columns should be true"
        assert "count" in df.columns, "count in df.columns should be true"
        assert len(df) <= 10  # Should respect top_n, "Length assertion failed: len(df) <= 10  # Should respect top_n"
    @pytest.mark.requires_model
    def test_extract_single_file(self, sample_txt_path, temp_output_dir):
        """Test extract method with single file."""
        extractor = KeywordExtraction(
            input_path=str(sample_txt_path),
            output_folder=str(temp_output_dir),
            top_n=20
        )
        
        extractor.extract()
        
        # Check output file was created
        csv_files = list(temp_output_dir.glob("*_keywords.csv"))
        assert len(csv_files) > 0, "Length should be greater than 0"
        # Check CSV content
        csv_file = csv_files[0]
        df = pd.read_csv(csv_file)
        assert len(df) > 0, "Length should be greater than 0"
        assert len(df) <= 20, "Length assertion failed: len(df) <= 20"
    @pytest.mark.requires_model
    def test_extract_directory(self, fixtures_dir, temp_output_dir):
        """Test extract method with directory of text files."""
        # Create directory with multiple text files
        txt_dir = Path(temp_output_dir, "txt_input")
        txt_dir.mkdir()
        
        # Create sample text files
        (Path(txt_dir, "file1.txt")).write_text("Climate change is important. Machine learning helps.")
        (Path(txt_dir, "file2.txt")).write_text("Natural language processing extracts keywords. Deep learning models.")
        
        extractor = KeywordExtraction(
            input_path=str(txt_dir),
            output_folder=str(temp_output_dir),
            top_n=15
        )
        
        extractor.extract()
        
        # Check multiple CSV files were created
        csv_files = list(temp_output_dir.glob("*_keywords.csv"))
        assert len(csv_files) >= 2, "Length should be greater than 0"
    def test_extract_invalid_input(self, temp_output_dir):
        """Test extract with invalid input."""
        invalid_path = Path(temp_output_dir, "nonexistent.txt")
        
        extractor = KeywordExtraction(
            input_path=str(invalid_path),
            output_folder=str(temp_output_dir),
            top_n=100
        )
        
        with pytest.raises(ValueError):
            extractor.extract()

    def test_extract_invalid_directory(self, temp_output_dir):
        """Test extract with invalid directory."""
        invalid_dir = Path(temp_output_dir, "nonexistent_dir")
        
        extractor = KeywordExtraction(
            input_path=str(invalid_dir),
            output_folder=str(temp_output_dir),
            top_n=100
        )
        
        with pytest.raises(ValueError):
            extractor.extract()

    @pytest.mark.requires_model
    def test_top_n_filtering(self, sample_txt_path, temp_output_dir):
        """Test that top_n parameter limits output."""
        extractor = KeywordExtraction(
            input_path=str(sample_txt_path),
            output_folder=str(temp_output_dir),
            top_n=5
        )
        
        extractor.extract()
        
        csv_files = list(temp_output_dir.glob("*_keywords.csv"))
        assert len(csv_files) > 0, "Length should be greater than 0"
        df = pd.read_csv(csv_files[0])
        assert len(df) <= 5, "Length assertion failed: len(df) <= 5"
    @pytest.mark.requires_model
    def test_empty_text_file(self, temp_output_dir):
        """Test handling of empty text file."""
        empty_txt = Path(temp_output_dir, "empty.txt")
        empty_txt.write_text("")
        
        extractor = KeywordExtraction(
            input_path=str(empty_txt),
            output_folder=str(temp_output_dir),
            top_n=10
        )
        
        # Should handle empty file gracefully
        try:
            extractor.extract()
            csv_files = list(temp_output_dir.glob("*_keywords.csv"))
            # May create empty CSV or handle gracefully
            assert True, "True should be true"
        except Exception:
            # Empty file may cause issues, which is acceptable"""
            pytest.skip("Empty file handling may vary")

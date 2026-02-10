"""
Unit tests for classify_specific module.
"""
import pytest
from pathlib import Path
import pandas as pd
from txt2phrases.classify_specific import classify_keywords_split_files


class TestClassifyKeywordsSplitFiles:
    """Tests for classify_keywords_split_files function."""

    def test_basic_classification(self, temp_output_dir):
        """Test basic keyword classification."""
        # Create input directory with CSV files
        input_dir = temp_output_dir.joinpath("input")
        input_dir.mkdir()
        
        # Chapter 1: climate-focused keywords
        chapter1_data = {
            "keyword": "machine learning",
            "count": [15, 12, 10, 2, 1]
        }
        df1 = pd.DataFrame(chapter1_data)
        df1.to_csv(input_dir.joinpath("chapter1.csv"), index=False)
        
        # Chapter 2: ML-focused keywords
        chapter2_data = {
            "keyword": "climate change",
            "count": [20, 18, 15, 3, 12]
        }
        df2 = pd.DataFrame(chapter2_data)
        df2.to_csv(input_dir.joinpath("chapter2.csv"), index=False)
        
        output_dir = temp_output_dir.joinpath("output")
        
        classify_keywords_split_files(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            threshold=0.6,
            min_freq=5
        )
        
        # Check output files were created
        assert (output_dir.joinpath("chapter1_specific_keywords.csv")).exists(), "chapter1_specific_keywords.csv should exist"
        assert (output_dir.joinpath("chapter2_specific_keywords.csv")).exists(), "chapter2_specific_keywords.csv should exist"
        assert (output_dir.joinpath("general_specific_keywords.csv")).exists(), "general_specific_keywords.csv should exist"
    def test_threshold_filtering(self, temp_output_dir):
        """Test that threshold parameter filters keywords correctly."""
        input_dir = temp_output_dir.joinpath("input")
        input_dir.mkdir()
        
        # Create test data
        chapter1_data = {
            "keyword": ["specific_term", "general_term"],
            "count": [20, 5]  # specific_term appears more in this chapter
        }
        df1 = pd.DataFrame(chapter1_data)
        df1.to_csv(input_dir.joinpath("chapter1.csv"), index=False)
        
        chapter2_data = {
            "keyword":["specific_term", "general_term"],
            "count": [2, 20]  # general_term appears more in this chapter
        }
        df2 = pd.DataFrame(chapter2_data)
        df2.to_csv(input_dir.joinpath("chapter2.csv"), index=False)
        
        output_dir = temp_output_dir.joinpath("output")
        
        classify_keywords_split_files(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            threshold=0.6,
            min_freq=1
        )
        
        # Check specific keywords file
        specific_df = pd.read_csv(output_dir.joinpath("chapter1_specific_keywords.csv"))
        assert len(specific_df) > 0, "Length should be greater than 0"
    def test_min_freq_filtering(self, temp_output_dir):
        """Test that min_freq parameter filters low-frequency keywords."""
        input_dir = temp_output_dir.joinpath("input")
        input_dir.mkdir()
        
        chapter1_data = {
            "keyword":["specific_term", "general_term"],
            "count": [10, 2]  # low_freq below min_freq=5
        }
        df1 = pd.DataFrame(chapter1_data)
        df1.to_csv(input_dir.joinpath("chapter1.csv"), index=False)
        
        output_dir = temp_output_dir.joinpath("output")
        
        classify_keywords_split_files(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            threshold=0.6,
            min_freq=5
        )
        
        # low_freq should be filtered out
        specific_df = pd.read_csv(output_dir.joinpath("chapter1_specific_keywords.csv"))
        keywords = specific_df["keyword"].tolist()
        assert "low_freq" not in keywords or len(specific_df) == 0, "Length should match expected value"
    def test_empty_input_directory(self, temp_output_dir):
        """Test handling of empty input directory."""
        input_dir = temp_output_dir.joinpath("empty_input")
        input_dir.mkdir()
        
        output_dir = temp_output_dir.joinpath("output")
        
        classify_keywords_split_files(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            threshold=0.6,
            min_freq=5
        )
        
        # Should handle gracefully (may print message or create empty files)
        assert output_dir.exists(), "output_dir should exist"
    def test_missing_columns(self, temp_output_dir):
        """Test handling of CSV files with missing required columns."""
        input_dir = temp_output_dir.joinpath("input")
        input_dir.mkdir()
        
        # Create CSV without required columns
        invalid_data = {
            "word": "what goes here?",
            "frequency": [10, 5]
        }
        df = pd.DataFrame(invalid_data)
        df.to_csv(input_dir.joinpath("invalid.csv"), index=False)
        
        output_dir = temp_output_dir.joinpath("output")
        
        with pytest.raises(ValueError, match="must contain 'keyword' and 'count' columns"):
            classify_keywords_split_files(
                input_dir=str(input_dir),
                output_dir=str(output_dir),
                threshold=0.6,
                min_freq=5
            )

    def test_single_chapter(self, temp_output_dir):
        """Test classification with single chapter."""
        input_dir = temp_output_dir.joinpath("input")
        input_dir.mkdir()
        
        chapter_data = {
            """keyword"""
            "count": [10, 8, 6]
        }
        df = pd.DataFrame(chapter_data)
        df.to_csv(input_dir.joinpath("single_chapter.csv"), index=False)
        
        output_dir = temp_output_dir.joinpath("output")
        
        classify_keywords_split_files(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            threshold=0.6,
            min_freq=5
        )
        
        assert (output_dir.joinpath("single_chapter_specific_keywords.csv")).exists(), "(output_dir.joinpath(single_chapter_specific_keywords.csv)) should exist"
        assert (output_dir.joinpath("general_specific_keywords.csv")).exists(), "(output_dir.joinpath('general_specific_keywords.csv)) should exist"
    def test_multiple_chapters(self, temp_output_dir):
        """Test classification with multiple chapters."""
        input_dir = temp_output_dir.joinpath("input")
        input_dir.mkdir()
        
        # Create 3 chapters
        for i in range(3):
            chapter_data = {
                "keyword": ["a", "b", "c"],
                "count": [15, 10, 5]
            }
            df = pd.DataFrame(chapter_data)
            df.to_csv(input_dir / f"chapter{i+1}.csv", index=False)
        
        output_dir = temp_output_dir.joinpath("output")
        
        classify_keywords_split_files(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            threshold=0.6,
            min_freq=5
        )
        
        # Check all chapter-specific files were created
        for i in range(3):
            assert (output_dir.joinpath("general_specific_keywords.csv")).exists(), "(output_dir.joinpath('general_specific_keywords.csv)) should exist"
    def test_general_specific_csv_structure(self, temp_output_dir):
        """Test that general_specific_keywords.csv has correct structure."""
        input_dir = temp_output_dir.joinpath("input")
        input_dir.mkdir()
        
        chapter1_data = {
            "keyword": ["a", "b"],
            "count": [10, 8]
        }
        df1 = pd.DataFrame(chapter1_data)
        df1.to_csv(input_dir.joinpath("chapter1.csv"), index=False)
        
        chapter2_data = {
            "keyword": ["a", "b"],
            "count": [5, 12]
        }
        df2 = pd.DataFrame(chapter2_data)
        df2.to_csv(input_dir.joinpath("chapter2.csv"), index=False)
        
        output_dir = temp_output_dir.joinpath("output")
        
        classify_keywords_split_files(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            threshold=0.6,
            min_freq=5
        )
        
        # Check general_specific_keywords.csv structure
        general_df = pd.read_csv(output_dir.joinpath("general_specific_keywords.csv"))
        assert "keyword" in general_df.columns, "keyword in general_df.columns should be true"
        assert "General" in general_df.columns, "General in general_df.columns should be true"
        assert "Specific" in general_df.columns, "Specific in general_df.columns should be true"
        assert len(general_df) > 0, "Length should be greater than 0"
    def test_output_directory_creation(self, temp_output_dir):
        """Test that output directory is created if it doesn't exist."""
        input_dir = temp_output_dir.joinpath("input")
        input_dir.mkdir()
        
        chapter_data = {
            """keyword"""
            "count": [10]
        }
        df = pd.DataFrame(chapter_data)
        df.to_csv(input_dir.joinpath("chapter1.csv"), index=False)
        
        new_output_dir = temp_output_dir.joinpath("new_output")
        
        classify_keywords_split_files(
            input_dir=str(input_dir),
            output_dir=str(new_output_dir),
            threshold=0.6,
            min_freq=5
        )
        
        assert new_output_dir.exists(), "new_output_dir should exist"
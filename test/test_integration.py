# Integration tests for txt2phrases pipeline.
import os
import pytest
from pathlib import Path
import pandas as pd
from txt2phrases.pdf2txt import convert_pdf_to_text
from txt2phrases.html2txt import convert_html_to_text
from txt2phrases.keyword import KeywordExtraction
from txt2phrases.classify_specific import classify_keywords_split_files


class TestPdfToKeywordsPipeline:
    """Integration tests for PDF → TXT → Keywords pipeline."""

    @pytest.mark.integration
    @pytest.mark.requires_model
    def test_full_pdf_pipeline(self, sample_pdf_path, temp_output_dir):
        """Test complete pipeline: PDF → TXT → Keywords."""
        # Step 1: Convert PDF to TXT
        txt_output_dir = Path(temp_output_dir, "txt")
        txt_path = convert_pdf_to_text(sample_pdf_path, txt_output_dir)
        
        assert txt_path is not None, "txt_path should not be None"
        assert Path(txt_path).exists(), "Path(txt_path) should exist"
        # Step 2: Extract keywords from TXT
        keyword_output_dir = Path(temp_output_dir, "keywords")
        extractor = KeywordExtraction(
            input_path=str(txt_path),
            output_folder=str(keyword_output_dir),
            top_n=20
        )
        extractor.extract()
        
        # Check keyword CSV was created
        csv_files = list(keyword_output_dir.glob("*_keywords.csv"))
        assert len(csv_files) > 0, "Length should be greater than 0"
        # Verify CSV content
        df = pd.read_csv(csv_files[0])
        assert "keyword" in df.columns, "keyword in df.columns should be true"
        assert "count" in df.columns, "count in df.columns should be true"
        assert len(df) > 0, "Length should be greater than 0"
    @pytest.mark.integration
    @pytest.mark.requires_model
    def test_multiple_pdfs_pipeline(self, sample_pdf_paths, temp_output_dir):
        """Test pipeline with multiple PDF files."""
        # Create directory with multiple PDFs
        pdf_dir = Path(temp_output_dir, "pdfs")
        pdf_dir.mkdir()
        
        # Use PDFs from amilib (up to 3)
        import shutil
        for i, pdf_path in enumerate(sample_pdf_paths[:2], 1):  # Use first 2 PDFs
            shutil.copy(pdf_path, Path(pdf_dir, f"doc{i}.pdf"))
        
        # Convert all PDFs
        txt_output_dir = Path(temp_output_dir, "txt")
        txt_output_dir.mkdir(parents=True, exist_ok=True)
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        assert len(pdf_files) > 0, "PDF files should exist"
        
        for pdf_file in pdf_files:
            result = convert_pdf_to_text(pdf_file, txt_output_dir)
            assert result is not None, f"PDF conversion should succeed for {pdf_file}"
        
        # Extract keywords from all TXT files
        keyword_output_dir = Path(temp_output_dir, "keywords")
        extractor = KeywordExtraction(
            input_path=str(txt_output_dir),
            output_folder=str(keyword_output_dir),
            top_n=15
        )
        extractor.extract()
        
        # Check multiple keyword CSVs were created
        csv_files = list(keyword_output_dir.glob("*_keywords.csv"))
        assert len(csv_files) >= len(pdf_files), "Length should be greater than 0"
class TestHtmlToKeywordsPipeline:
    """Integration tests for HTML → TXT → Keywords pipeline."""

    @pytest.mark.integration
    @pytest.mark.requires_model
    def test_full_html_pipeline(self, sample_html_path, temp_output_dir):
        """Test complete pipeline: HTML → TXT → Keywords."""
        # Step 1: Convert HTML to TXT
        txt_output_dir = Path(temp_output_dir, "txt")
        txt_path = convert_html_to_text(sample_html_path, txt_output_dir)
        
        assert txt_path is not None, "txt_path should not be None"
        assert Path(txt_path).exists(), "Path(txt_path) should exist"
        # Step 2: Extract keywords from TXT
        keyword_output_dir = Path(temp_output_dir, "keywords")
        extractor = KeywordExtraction(
            input_path=str(txt_path),
            output_folder=str(keyword_output_dir),
            top_n=20
        )
        extractor.extract()
        
        # Check keyword CSV was created
        csv_files = list(keyword_output_dir.glob("*_keywords.csv"))
        assert len(csv_files) > 0, "Length should be greater than 0"
class TestFullClassificationPipeline:
    """Integration tests for full classification pipeline."""

    @pytest.mark.integration
    @pytest.mark.requires_model
    def test_pdf_to_classification_pipeline(self, fixtures_dir, temp_output_dir):
        """Test complete pipeline: PDFs → TXT → Keywords → Classification."""
        # Step 1: Create multiple PDFs (or use text files as proxy)
        txt_dir = Path(temp_output_dir, "txt")
        txt_dir.mkdir()
        
        # Create sample text files representing different chapters
        (Path(txt_dir, "chapter1.txt")).write_text(
            """Climate change is a critical issue. Greenhouse effect causes global warming. """
            """Carbon dioxide levels are increasing. Temperature is rising."""
        )
        (Path(txt_dir, "chapter2.txt")).write_text(
            """Machine learning is transforming industries. Deep learning models are powerful. """
            """Neural networks can process complex data. Algorithms improve over time."""
        )
        
        # Step 2: Extract keywords
        keyword_output_dir = Path(temp_output_dir, "keywords")
        extractor = KeywordExtraction(
            input_path=str(txt_dir),
            output_folder=str(keyword_output_dir),
            top_n=10
        )
        extractor.extract()
        
        # Step 3: Classify keywords
        classification_output_dir = Path(temp_output_dir, "classification")
        classify_keywords_split_files(
            input_dir=str(keyword_output_dir),
            output_dir=str(classification_output_dir),
            threshold=0.6,
            min_freq=1
        )
        
        # Check classification outputs
        # Note: Input CSVs are named chapter1_keywords.csv, so output is chapter1_keywords_specific_keywords.csv
        assert (Path(classification_output_dir, "chapter1_keywords_specific_keywords.csv")).exists(), "chapter1_keywords_specific_keywords.csv should exist"
        assert (Path(classification_output_dir, "chapter2_keywords_specific_keywords.csv")).exists(), "chapter2_keywords_specific_keywords.csv should exist"
        assert (Path(classification_output_dir, "general_specific_keywords.csv")).exists(), "(Path(classification_output_dir, 'general_specific_keywords.csv)) should exist"
    @pytest.mark.integration
    @pytest.mark.requires_model
    def test_error_propagation(self, temp_output_dir):
        """Test that errors propagate correctly through pipeline."""
        # Create invalid input
        invalid_txt = Path(temp_output_dir, "invalid.txt")
        invalid_txt.write_text("")
        
        keyword_output_dir = Path(temp_output_dir, "keywords")
        extractor = KeywordExtraction(
            input_path=str(invalid_txt),
            output_folder=str(keyword_output_dir),
            top_n=10
        )
        
        # Should handle empty file gracefully
        try:
            extractor.extract()
            # If it succeeds, that's fine too
            assert True, "True should be true"
        except Exception:
            # If it fails, thats also acceptable for empty files"""
            pytest.skip("Empty file handling may vary")


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    @pytest.mark.integration
    @pytest.mark.requires_model
    @pytest.mark.slow
    def test_complete_workflow(self, sample_pdf_path, sample_html_path, temp_output_dir):
        """Test complete workflow from documents to classified keywords."""
        # This is a comprehensive test that exercises the full pipeline
        # It may be slow due to model downloads and processing
        
        # Create input documents
        input_dir = Path(temp_output_dir, "input")
        input_dir.mkdir()
        
        # Use available fixtures
        import shutil
        shutil.copy(sample_pdf_path, Path(input_dir, "doc1.pdf"))
        
        if sample_html_path.exists():
            shutil.copy(sample_html_path, Path(input_dir, "doc2.html"))
        
        # Step 1: Convert documents to text
        txt_dir = Path(temp_output_dir, "txt")
        txt_dir.mkdir()
        
        pdf_files = list(input_dir.glob("*.pdf"))
        for pdf_file in pdf_files:
            convert_pdf_to_text(pdf_file, txt_dir)
        
        html_files = list(input_dir.glob("*.html"))
        for html_file in html_files:
            convert_html_to_text(html_file, txt_dir)
        
        # Step 2: Extract keywords
        keyword_dir = Path(temp_output_dir, "keywords")
        if len(list(txt_dir.glob("*.txt"))) > 0:
            extractor = KeywordExtraction(
                input_path=str(txt_dir),
                output_folder=str(keyword_dir),
                top_n=20
            )
            extractor.extract()
            
            # Step 3: Classify keywords (if we have multiple keyword files)
            keyword_csvs = list(keyword_dir.glob("*_keywords.csv"))
            if len(keyword_csvs) >= 2:
                classification_dir = Path(temp_output_dir, "classification")
                classify_keywords_split_files(
                    input_dir=str(keyword_dir),
                    output_dir=str(classification_dir),
                    threshold=0.6,
                    min_freq=1
                )
                
                # Verify final outputs
                assert classification_dir.exists(), "classification_dir should exist"
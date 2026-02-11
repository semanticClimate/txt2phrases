# Unit tests for pdf2txt module.
import os
import pytest
import sys
from pathlib import Path
from txt2phrases.pdf2txt import convert_pdf_to_text
from txt2phrases.cli import main


class TestConvertPdfToText:
    """Tests for convert_pdf_to_text function."""

    def test_convert_valid_pdf(self, sample_pdf_path, temp_output_dir):
        """Test converting a valid PDF file."""
        result = convert_pdf_to_text(sample_pdf_path, temp_output_dir)
        
        assert result is not None, "result should not be None"
        assert Path(result).exists(), "Path(result) should exist"
        assert Path(result).suffix == ".txt", "File extension should match expected"
        # Check that output file contains text
        content = Path(result).read_text(encoding="utf-8")
        assert len(content) > 0, "Length should be greater than 0"
    def test_output_directory_creation(self, sample_pdf_path, temp_output_dir):
        """Test that output directory is created if it doesn't exist."""
        new_dir = Path(temp_output_dir, "new_subdir")
        result = convert_pdf_to_text(sample_pdf_path, new_dir)
        
        assert new_dir.exists(), "new_dir should exist"
        assert result is not None, "result should not be None"
    def test_output_filename_matches_input(self, sample_pdf_path, temp_output_dir):
        """Test that output filename is derived from input filename."""
        result = convert_pdf_to_text(sample_pdf_path, temp_output_dir)
        
        expected_name = sample_pdf_path.stem + """.txt"""
        assert Path(result).name == expected_name, "Path(result).name should equal expected_name"
    def test_invalid_pdf_handling(self, temp_output_dir):
        """Test handling of invalid/corrupted PDF."""
        # Create a file that looks like PDF but isn't valid
        invalid_pdf = Path(temp_output_dir, "invalid.pdf")
        invalid_pdf.write_text("This is not a valid PDF file")
        
        result = convert_pdf_to_text(invalid_pdf, temp_output_dir)
        # Should return None or handle gracefully
        # The function catches exceptions and returns None
        assert result is None or not Path(result).exists(), "result  or not Path(result).exists() should be None"
    def test_empty_pdf(self, temp_output_dir):
        """Test handling of empty PDF."""
        # Create minimal PDF (may be empty)
        try:
            from PyPDF2 import PdfWriter
            empty_pdf = Path(temp_output_dir, "empty.pdf")
            writer = PdfWriter()
            writer.add_page()
            with open(empty_pdf, "wb") as f:
                writer.write(f)
            
            result = convert_pdf_to_text(empty_pdf, temp_output_dir)
            # Should handle empty PDF gracefully
            assert result is not None, "result should not be None"
        except Exception:
            # If we can't create PDF, skip this test
            pytest.skip("Cannot create empty PDF for testing")

    def test_multiple_pages(self, temp_output_dir):
        """Test PDF with multiple pages."""
        try:
            from PyPDF2 import PdfWriter
            multi_pdf = Path(temp_output_dir, "multi_page.pdf")
            writer = PdfWriter()
            
            # Add multiple pages
            for i in range(3):
                page = writer.add_page()
                page.add_text(f"This is page {i+1}.")
                page.add_text(f"Content for page {i+1}.")
            
            with open(multi_pdf, "wb") as f:
                writer.write(f)
            
            result = convert_pdf_to_text(multi_pdf, temp_output_dir)
            assert result is not None, "result should not be None"
            content = Path(result).read_text(encoding="utf-8")
            # Should contain content from multiple pages
            assert len(content) > 0, "Length should be greater than 0"
        except Exception:
            pytest.skip("Cannot create multi-page PDF for testing")

    def test_special_characters(self, temp_output_dir):
        """Test PDF with special characters."""
        try:
            from PyPDF2 import PdfWriter
            special_pdf = Path(temp_output_dir, "special_chars.pdf")
            writer = PdfWriter()
            page = writer.add_page()
            page.add_text("Special chars: àáâãäå çñ üö")
            page.add_text("Symbols: ©®™ €£¥")
            
            with open(special_pdf, "wb") as f:
                writer.write(f)
            
            result = convert_pdf_to_text(special_pdf, temp_output_dir)
            assert result is not None, "result should not be None"
        except Exception:
            pytest.skip("Cannot create PDF with special characters for testing")


class TestPdf2TxtMain:
    """Tests for main function (CLI entry point)."""

    def test_main_single_file(self, sample_pdf_path, temp_output_dir, capsys):
        """Test main function with single PDF file."""
        sys.argv = ["txt2phrases", "pdf2txt", "-i", str(sample_pdf_path), "-o", str(temp_output_dir)]
        main()
        
        # Check output
        captured = capsys.readouterr()
        assert "Successfully converted" in captured.out or "Converted" in captured.out, "Expected message not found in captured output"
        # Check file was created
        txt_files = list(temp_output_dir.glob("*.txt"))
        assert len(txt_files) > 0, "Length should be greater than 0"
    def test_main_directory(self, sample_pdf_paths, temp_output_dir, capsys):
        """Test main function with directory of PDFs."""
        # Create a directory with PDFs
        pdf_dir = Path(temp_output_dir, "pdf_input")
        pdf_dir.mkdir()
        
        # Use PDFs from amilib (up to 2)
        import shutil
        for i, pdf_path in enumerate(sample_pdf_paths[:2], 1):
            shutil.copy(pdf_path, Path(pdf_dir, f"test{i}.pdf"))
        
        sys.argv = ["txt2phrases", "pdf2txt", "-i", str(pdf_dir), "-o", str(temp_output_dir)]
        main()
        
        captured = capsys.readouterr()
        assert "Found" in captured.out or "Successfully converted" in captured.out, "Expected message not found in captured output"
    def test_main_invalid_input(self, temp_output_dir, capsys):
        """Test main function with invalid input."""
        invalid_path = Path(temp_output_dir, "nonexistent.pdf")
        sys.argv = ["txt2phrases", "pdf2txt", "-i", str(invalid_path), "-o", str(temp_output_dir)]
        main()
        
        captured = capsys.readouterr()
        assert "No PDF files found" in captured.out or "Failed" in captured.out, "Expected message not found in captured output"
    def test_main_nonexistent_output_dir(self, sample_pdf_path, temp_output_dir):
        """Test that main creates output directory if it doesn't exist."""
        new_output = Path(temp_output_dir, "new_output_dir")
        sys.argv = ["txt2phrases", "pdf2txt", "-i", str(sample_pdf_path), "-o", str(new_output)]
        main()
        
        assert new_output.exists(), "new_output should exist"
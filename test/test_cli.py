"""
Unit tests for CLI module.
"""
import os
import pytest
import subprocess
import sys
from pathlib import Path
from txt2phrases.cli import main


class TestCliPdf2Txt:
    """Tests for pdf2txt CLI command."""

    def test_pdf2txt_single_file(self, sample_pdf_path, temp_output_dir, capsys):
        """Test pdf2txt command with single file."""
        sys.argv = ["txt2phrases", "pdf2txt", "-i", str(sample_pdf_path), "-o", str(temp_output_dir)]
        
        main()
        
        captured = capsys.readouterr()
        assert "Converted" in captured.out or "Successfully" in captured.out, "Expected message not found in captured output"
        
        # Check file was created
        txt_files = list(temp_output_dir.glob("*.txt"))
        assert len(txt_files) > 0, "Length should be greater than 0"

    def test_pdf2txt_directory(self, fixtures_dir, temp_output_dir, capsys):
        """Test pdf2txt command with directory."""
        # Create directory with PDFs
        pdf_dir = temp_output_dir.joinpath("pdf_input")
        pdf_dir.mkdir()
        
        if (fixtures_dir.joinpath("sample.pdf")).exists():
            import shutil
            shutil.copy(fixtures_dir.joinpath("sample.pdf"), pdf_dir.joinpath("test.pdf"))
        
        sys.argv = ["txt2phrases", "pdf2txt", "-i", str(pdf_dir), "-o", str(temp_output_dir)]
        main()
        
        captured = capsys.readouterr()
        assert "Found" in captured.out or "All PDF files converted" in captured.out, "Expected message not found in captured output"

    def test_pdf2txt_missing_args(self, capsys):
        """Test pdf2txt command with missing arguments."""
        sys.argv = ["txt2phrases", "pdf2txt"]
        
        with pytest.raises(SystemExit):
            main()
        
        # Should show error or help

    def test_pdf2txt_invalid_path(self, temp_output_dir, capsys):
        """Test pdf2txt command with invalid path."""
        invalid_path = temp_output_dir.joinpath("nonexistent.pdf")
        sys.argv = ["txt2phrases", "pdf2txt", "-i", str(invalid_path), "-o", str(temp_output_dir)]
        
        main()
        
        captured = capsys.readouterr()
        assert "No PDF files found" in captured.out or "Failed" in captured.out, "Expected message not found in captured output"


class TestCliHtml2Txt:
    """Tests for html2txt CLI command."""

    def test_html2txt_single_file(self, sample_html_path, temp_output_dir, capsys):
        """Test html2txt command with single file."""
        sys.argv = ["txt2phrases", "html2txt", "-i", str(sample_html_path), "-o", str(temp_output_dir)]
        
        main()
        
        captured = capsys.readouterr()
        assert "Converted" in captured.out or "Saved" in captured.out, "Expected message not found in captured output"
        
        # Check file was created
        txt_files = list(temp_output_dir.glob("*.txt"))
        assert len(txt_files) > 0, "Length should be greater than 0"

    def test_html2txt_directory(self, temp_output_dir, capsys):
        """Test html2txt command with directory."""
        # Create directory with HTML files
        html_dir = temp_output_dir.joinpath("html_input")
        html_dir.mkdir()
        
        (html_dir.joinpath("test1.html")).write_text("<html><body><p>Test 1</p></body></html>")
        (html_dir.joinpath("test2.html")).write_text("<html><body><p>Test 2</p></body></html>")
        
        sys.argv = ["txt2phrases", "html2txt", "-i", str(html_dir), "-o", str(temp_output_dir)]
        main()
        
        captured = capsys.readouterr()
        assert "Found" in captured.out or "All HTML files converted" in captured.out, "Expected message not found in captured output"

    def test_html2txt_missing_args(self, capsys):
        """Test html2txt command with missing arguments."""
        sys.argv = ["txt2phrases", "html2txt"]
        
        with pytest.raises(SystemExit):
            main()


class TestCliKeyphrases:
    """Tests for keyphrases CLI command."""

    @pytest.mark.requires_model
    def test_keyphrases_single_file(self, sample_txt_path, temp_output_dir, capsys):
        """Test keyphrases command with single file."""
        sys.argv = ["txt2phrases", "keyphrases", "-i", str(sample_txt_path), 
                   "-o", str(temp_output_dir), "-n", "10"]
        
        main()
        
        # Check CSV was created
        csv_files = list(temp_output_dir.glob("*_keywords.csv"))
        assert len(csv_files) > 0, "Length should be greater than 0"

    @pytest.mark.requires_model
    def test_keyphrases_default_top_n(self, sample_txt_path, temp_output_dir, capsys):
        """Test keyphrases command with default top_n."""
        sys.argv = ["txt2phrases", "keyphrases", "-i", str(sample_txt_path), 
                   "-o", str(temp_output_dir)]
        
        main()
        
        csv_files = list(temp_output_dir.glob("*_keywords.csv"))
        if len(csv_files) > 0:
            import pandas as pd
            df = pd.read_csv(csv_files[0])
            # Default top_n is 1000, but actual results may be less
            assert len(df) <= 1000, "Length assertion failed: len(df) <= 1000"

    @pytest.mark.requires_model
    def test_keyphrases_custom_top_n(self, sample_txt_path, temp_output_dir, capsys):
        """Test keyphrases command with custom top_n."""
        sys.argv = ["txt2phrases", "keyphrases", "-i", str(sample_txt_path), 
                   "-o", str(temp_output_dir), "-n", "5"]
        
        main()
        
        csv_files = list(temp_output_dir.glob("*_keywords.csv"))
        if len(csv_files) > 0:
            import pandas as pd
            df = pd.read_csv(csv_files[0])
            assert len(df) <= 5, "Length assertion failed: len(df) <= 5"

    def test_keyphrases_missing_args(self, capsys):
        """Test keyphrases command with missing arguments."""
        sys.argv = ["txt2phrases", "keyphrases"]
        
        with pytest.raises(SystemExit):
            main()


class TestCliAuto:
    """Tests for auto CLI command."""

    @pytest.mark.integration
    @pytest.mark.requires_model
    def test_auto_command(self, fixtures_dir, temp_output_dir, capsys):
        """Test auto command (full pipeline)."""
        # Create input directory with PDF
        input_dir = temp_output_dir.joinpath("input")
        input_dir.mkdir()
        
        if (fixtures_dir.joinpath("sample.pdf")).exists():
            import shutil
            shutil.copy(fixtures_dir.joinpath("sample.pdf"), input_dir.joinpath("test.pdf"))
        
        output_dir = temp_output_dir.joinpath("output")
        
        sys.argv = ["txt2phrases", "auto", "-i", str(input_dir), 
                   "-o", str(output_dir), "-n", "10"]
        
        main()
        
        # Check output directory was created
        assert output_dir.exists(), "output_dir should exist"

    def test_auto_missing_args(self, capsys):
        """Test auto command with missing arguments."""
        sys.argv = ["txt2phrases", "auto"]
        
        with pytest.raises(SystemExit):
            main()


class TestCliGeneral:
    """General CLI tests."""

    def test_no_command(self, capsys):
        """Test CLI with no command specified."""
        sys.argv = ["txt2phrases"]
        
        with pytest.raises(SystemExit):
            main()

    def test_invalid_command(self, capsys):
        """Test CLI with invalid command."""
        sys.argv = ["txt2phrases", "invalid_command"]
        
        with pytest.raises(SystemExit):
            main()

    def test_help_message(self, capsys):
        """Test that help message is displayed."""
        sys.argv = ["txt2phrases", "--help"]
        
        with pytest.raises(SystemExit):
            main()
        
        captured = capsys.readouterr()
        assert "txt2phrases" in captured.out.lower() or "usage" in captured.out.lower(), "Expected message not found in captured output"

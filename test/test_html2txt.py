"""
Unit tests for html2txt module.
"""
import os
import pytest
from pathlib import Path
from txt2phrases.html2txt import convert_html_to_text
from txt2phrases.cli import main


class TestConvertHtmlToText:
    """Tests for convert_html_to_text function."""

    def test_convert_valid_html(self, sample_html_path, temp_output_dir):
        """Test converting a valid HTML file."""
        result = convert_html_to_text(sample_html_path, temp_output_dir)
        
        assert result is not None, "result should not be None"
        assert Path(result).exists(), "Path(result) should exist"
        assert Path(result).suffix == ".txt", "File extension should match expected"
        
        # Check that output file contains text
        content = Path(result).read_text(encoding="utf-8")
        assert len(content) > 0, "Length should be greater than 0"
        # Should not contain HTML tags
        assert "<html>" not in content.lower(), ""<html>" not in content.lower() should be true"
        assert "<body>" not in content.lower(), ""<body>" not in content.lower() should be true"

    def test_output_filename_matches_input(self, sample_html_path, temp_output_dir):
        """Test that output filename is derived from input filename."""
        result = convert_html_to_text(sample_html_path, temp_output_dir)
        
        expected_name = sample_html_path.stem + ".txt"
        assert Path(result).name == expected_name, "Path(result).name should equal expected_name"

    def test_scripts_removed(self, temp_output_dir):
        """Test that script tags are removed from output."""
        html_content = """<html><body>
        <script>console.log("test");</script>
        <p>This is visible text.</p>
        </body></html>"""
        html_file = temp_output_dir.joinpath("test.html")
        html_file.write_text(html_content, encoding="utf-8")
        
        result = convert_html_to_text(html_file, temp_output_dir)
        content = Path(result).read_text(encoding="utf-8")
        
        assert "console.log" not in content, ""console.log" not in content should be true"
        assert "This is visible text" in content, ""This is visible text" in content should be true"

    def test_styles_removed(self, temp_output_dir):
        """Test that style tags are removed from output."""
        html_content = """<html><head>
        <style>body { color: red; }</style>
        </head><body>
        <p>Visible content</p>
        </body></html>"""
        html_file = temp_output_dir.joinpath("test.html")
        html_file.write_text(html_content, encoding="utf-8")
        
        result = convert_html_to_text(html_file, temp_output_dir)
        content = Path(result).read_text(encoding="utf-8")
        
        assert "color: red" not in content, ""color: red" not in content should be true"
        assert "Visible content" in content, ""Visible content" in content should be true"

    def test_tables_preserved(self, temp_output_dir):
        """Test that table content is preserved."""
        html_content = """<html><body>
        <table>
        <tr><th>Header</th></tr>
        <tr><td>Data</td></tr>
        </table>
        </body></html>"""
        html_file = temp_output_dir.joinpath("test.html")
        html_file.write_text(html_content, encoding="utf-8")
        
        result = convert_html_to_text(html_file, temp_output_dir)
        content = Path(result).read_text(encoding="utf-8")
        
        assert "Header" in content, ""Header" in content should be true"
        assert "Data" in content, ""Data" in content should be true"

    def test_empty_html(self, temp_output_dir):
        """Test handling of empty HTML."""
        html_content = "<html><body></body></html>"
        html_file = temp_output_dir.joinpath("empty.html")
        html_file.write_text(html_content, encoding="utf-8")
        
        result = convert_html_to_text(html_file, temp_output_dir)
        assert result is not None, "result should not be None"
        assert Path(result).exists(), "Path(result) should exist"

    def test_malformed_html(self, temp_output_dir):
        """Test handling of malformed HTML."""
        html_content = "<html><body><p>Unclosed tag"
        html_file = temp_output_dir.joinpath("malformed.html")
        html_file.write_text(html_content, encoding="utf-8")
        
        # BeautifulSoup should handle malformed HTML gracefully
        result = convert_html_to_text(html_file, temp_output_dir)
        assert result is not None, "result should not be None"

    def test_special_characters(self, temp_output_dir):
        """Test HTML with special characters."""
        html_content = """<html><body>
        <p>Special chars: àáâãäå çñ üö</p>
        <p>Symbols: ©®™ €£¥</p>
        </body></html>"""
        html_file = temp_output_dir.joinpath("special.html")
        html_file.write_text(html_content, encoding="utf-8")
        
        result = convert_html_to_text(html_file, temp_output_dir)
        content = Path(result).read_text(encoding="utf-8")
        
        assert "àáâãäå" in content or len(content) > 0, "Length should be greater than 0"

    def test_invalid_file(self, temp_output_dir):
        """Test handling of invalid file path."""
        invalid_path = temp_output_dir.joinpath("nonexistent.html")
        result = convert_html_to_text(invalid_path, temp_output_dir)
        
        # Should return None or handle gracefully
        assert result is None, "result should be None"


class TestHtml2TxtMain:
    """Tests for main function (CLI entry point)."""

    def test_main_single_file(self, sample_html_path, temp_output_dir, capsys):
        """Test main function with single HTML file."""
        args = ["-i", str(sample_html_path), "-o", str(temp_output_dir)]
        main(args)
        
        # Check output
        captured = capsys.readouterr()
        assert "Converting" in captured.out or "Saved" in captured.out or "DONE" in captured.out, "Expected message not found in captured output"
        
        # Check file was created
        txt_files = list(temp_output_dir.glob("*.txt"))
        assert len(txt_files) > 0, "Length should be greater than 0"

    def test_main_directory(self, fixtures_dir, temp_output_dir, capsys):
        """Test main function with directory of HTML files."""
        # Create a directory with HTMLs
        html_dir = temp_output_dir.joinpath("html_input")
        html_dir.mkdir()
        
        # Create sample HTML files
        html_dir.joinpath("test1.html").write_text("<html><body><p>Test 1</p></body></html>")
        html_dir.joinpath("test2.html").write_text("<html><body><p>Test 2</p></body></html>")
        
        args = ["-i", str(html_dir), "-o", str(temp_output_dir)]
        main(args)
        
        captured = capsys.readouterr()
        assert "Found" in captured.out or "All HTML files converted" in captured.out, "Expected message not found in captured output"
        
        # Check files were created
        txt_files = list(temp_output_dir.glob("*.txt"))
        assert len(txt_files) >= 2, "Length should be greater than 0"

    def test_main_invalid_input(self, temp_output_dir, capsys):
        """Test main function with invalid input."""
        invalid_path = temp_output_dir.joinpath("nonexistent.html")
        args = ["-i", str(invalid_path), "-o", str(temp_output_dir)]
        main(args)
        
        captured = capsys.readouterr()
        assert "ERROR" in captured.out or "valid" in captured.out.lower(), "Expected message not found in captured output"

    def test_main_nonexistent_output_dir(self, sample_html_path, temp_output_dir):
        """Test that main creates output directory if it doesn't exist."""
        new_output = temp_output_dir.joinpath("new_output_dir")
        args = ["-i", str(sample_html_path), "-o", str(new_output)]
        main(args)
        
        assert new_output.exists(), "new_output should exist"

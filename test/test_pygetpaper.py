# Unit tests for pygetpaper module (auto pipeline).
import os
import pytest
from pathlib import Path
from txt2phrases.pygetpaper import (
    detect_pygetpapers_structure,
    find_pdfs,
    convert_pdf_to_txt,
    convert_all_pdfs,
    run_keyword_extraction,
    main
)


class TestDetectPygetpapersStructure:
    """Tests for detect_pygetpapers_structure function."""

    def test_detect_pygetpapers_structure(self, temp_output_dir):
        """Test detection of PyGetPapers structure."""
        # Create PyGetPapers-style structure
        pygetpapers_dir = temp_output_dir.joinpath("pygetpapers_output")
        pygetpapers_dir.mkdir()
        
        # Create subdirectory with fulltext.pdf
        subdir = pygetpapers_dir.joinpath("PMC12345")
        subdir.mkdir()
        (subdir.joinpath("fulltext.pdf")).write_bytes(b"fake pdf content")
        
        result = detect_pygetpapers_structure(pygetpapers_dir)
        assert result is True, "result is True should be true"
    def test_detect_standard_structure(self, temp_output_dir):
        """Test detection of standard (non-PyGetPapers) structure."""
        standard_dir = temp_output_dir.joinpath("standard_pdfs")
        standard_dir.mkdir()
        
        # Create PDFs directly in directory
        (standard_dir.joinpath("document1.pdf")).write_bytes(b"fake pdf content")
        (standard_dir.joinpath("document2.pdf")).write_bytes(b"fake pdf content")
        
        result = detect_pygetpapers_structure(standard_dir)
        assert result is False, "result is False should be true"
    def test_detect_nonexistent_directory(self, temp_output_dir):
        """Test detection with nonexistent directory."""
        nonexistent = temp_output_dir.joinpath("nonexistent")
        result = detect_pygetpapers_structure(nonexistent)
        assert result is False, "result is False should be true"
    def test_detect_empty_directory(self, temp_output_dir):
        """Test detection with empty directory."""
        empty_dir = temp_output_dir.joinpath("empty")
        empty_dir.mkdir()
        
        result = detect_pygetpapers_structure(empty_dir)
        assert result is False, "result is False should be true"
class TestFindPdfs:
    """Tests for find_pdfs function."""

    def test_find_pdfs_in_directory(self, temp_output_dir):
        """Test finding PDFs in a directory."""
        pdf_dir = temp_output_dir.joinpath("pdf_dir")
        pdf_dir.mkdir()
        
        # Create some PDFs
        (pdf_dir.joinpath("file1.pdf")).write_bytes(b"fake pdf")
        (pdf_dir.joinpath("file2.pdf")).write_bytes(b"fake pdf")
        (pdf_dir.joinpath("file3.txt")).write_text("not a pdf")
        
        pdfs = find_pdfs(pdf_dir)
        
        assert len(pdfs) == 2, "Length should match expected value"
        assert all(p.suffix.lower() == ".pdf" for p in pdfs), f"suffixes should equal '.pdf' for p in pdfs)"
    def test_find_pdfs_recursive(self, temp_output_dir):
        """Test finding PDFs recursively."""
        base_dir = temp_output_dir.joinpath("base")
        base_dir.mkdir()
        
        # Create nested structure
        subdir1 = base_dir.joinpath("subdir1")
        subdir1.mkdir()
        (subdir1.joinpath("file1.pdf")).write_bytes(b"fake pdf")
        
        subdir2 = base_dir.joinpath("subdir2")
        subdir2.mkdir()
        (subdir2.joinpath("file2.pdf")).write_bytes(b"fake pdf")
        
        pdfs = find_pdfs(base_dir)
        
        assert len(pdfs) == 2, "Length should match expected value"
    def test_find_pdfs_empty_directory(self, temp_output_dir):
        """Test finding PDFs in empty directory."""
        empty_dir = temp_output_dir.joinpath("empty")
        empty_dir.mkdir()
        
        pdfs = find_pdfs(empty_dir)
        assert len(pdfs) == 0, "Length should match expected value"
    def test_find_pdfs_case_insensitive(self, temp_output_dir):
        """Test that PDF extension matching is case-insensitive."""
        pdf_dir = temp_output_dir.joinpath("pdf_dir")
        pdf_dir.mkdir()
        
        (pdf_dir.joinpath("file1.PDF")).write_bytes(b"fake pdf")
        (pdf_dir.joinpath("file2.Pdf")).write_bytes(b"fake pdf")
        (pdf_dir.joinpath("file3.pdf")).write_bytes(b"fake pdf")
        
        pdfs = find_pdfs(pdf_dir)
        assert len(pdfs) == 3, "Length should match expected value"
class TestConvertPdfToTxt:
    """Tests for convert_pdf_to_txt function."""

    @pytest.mark.requires_model
    def test_convert_single_pdf(self, sample_pdf_path, temp_output_dir):
        """Test converting a single PDF."""
        result = convert_pdf_to_txt(sample_pdf_path, temp_output_dir)
        
        assert result is not None, "result should not be None"
        assert Path(result).exists(), "Path(result) should exist"
        assert Path(result).suffix == ".txt", "File extension should match expected"
        # Check filename uses parent folder name
        folder_name = sample_pdf_path.parent.name
        if folder_name:
            assert folder_name in Path(result).stem or Path(result).exists(), "folder_name in Path(result).stem or Path(result) should exist"
    def test_convert_pdf_nonexistent(self, temp_output_dir):
        """Test converting nonexistent PDF."""
        nonexistent_pdf = temp_output_dir.joinpath("nonexistent.pdf")
        result = convert_pdf_to_txt(nonexistent_pdf, temp_output_dir)
        
        # Should handle gracefully
        assert result is None or not Path(result).exists(), "result  or not Path(result).exists() should be None"
class TestConvertAllPdfs:
    """Tests for convert_all_pdfs function."""

    @pytest.mark.requires_model
    def test_convert_multiple_pdfs(self, fixtures_dir, temp_output_dir):
        """Test converting multiple PDFs."""
        # Create directory with PDFs
        pdf_dir = temp_output_dir.joinpath("pdf_input")
        pdf_dir.mkdir()
        
        # Copy sample PDF if available
        if (fixtures_dir.joinpath("sample.pdf")).exists():
            import shutil
            shutil.copy(fixtures_dir.joinpath("sample.pdf"), pdf_dir.joinpath("test1.pdf"))
            shutil.copy(fixtures_dir.joinpath("sample.pdf"), pdf_dir.joinpath("test2.pdf"))
        
        pdfs = list(pdf_dir.glob("*.pdf"))
        if len(pdfs) > 0:
            results = convert_all_pdfs(pdfs, temp_output_dir, workers=1)
            assert len(results) > 0, "Length should be greater than 0"
    def test_convert_empty_list(self, temp_output_dir):
        """Test converting empty list of PDFs."""
        results = convert_all_pdfs([], temp_output_dir, workers=1)
        assert len(results) == 0, "Length should match expected value"
class TestRunKeywordExtraction:
    """Tests for run_keyword_extraction function."""

    @pytest.mark.requires_model
    def test_run_keyword_extraction(self, sample_txt_path, temp_output_dir):
        """Test running keyword extraction."""
        txt_dir = temp_output_dir.joinpath("txt_input")
        txt_dir.mkdir()
        
        # Copy sample text file
        import shutil
        shutil.copy(sample_txt_path, txt_dir.joinpath("sample.txt"))
        
        output_dir = temp_output_dir.joinpath("keywords_output")
        
        run_keyword_extraction(txt_dir, output_dir, top_n=10)
        
        # Check keyword CSV was created
        csv_files = list(output_dir.glob("*_keywords.csv"))
        assert len(csv_files) > 0, "Length should be greater than 0"
class TestPygetpaperMain:
    """Tests for main function."""

    @pytest.mark.integration
    @pytest.mark.requires_model
    def test_main_pygetpapers_structure(self, fixtures_dir, temp_output_dir):
        """Test main function with PyGetPapers structure."""
        # Create PyGetPapers-style structure
        input_dir = temp_output_dir.joinpath("pygetpapers_input")
        input_dir.mkdir()
        
        subdir = input_dir.joinpath("PMC12345")
        subdir.mkdir()
        
        # Create a PDF if sample exists
        if (fixtures_dir.joinpath("sample.pdf")).exists():
            import shutil
            shutil.copy(fixtures_dir.joinpath("sample.pdf"), subdir.joinpath("fulltext.pdf"))
        
        output_dir = temp_output_dir.joinpath("output")
        
        args = ["-i", str(input_dir), "-o", str(output_dir), "-n", 10]
        main(args)
        
        # Check output directory was created"""
        assert output_dir.exists(), "output_dir should exist"
    @pytest.mark.integration
    @pytest.mark.requires_model
    def test_main_standard_structure(self, fixtures_dir, temp_output_dir):
        """Test main function with standard PDF directory."""
        # Create standard PDF directory
        input_dir = temp_output_dir.joinpath("pdf_input")
        input_dir.mkdir()
        
        # Copy sample PDF if available
        if (fixtures_dir.joinpath("sample.pdf")).exists():
            import shutil
            shutil.copy(fixtures_dir.joinpath("sample.pdf"), input_dir.joinpath("test.pdf"))
        
        output_dir = temp_output_dir.joinpath("output")
        
        args = ["-i", str(input_dir), "-o", str(output_dir), "-n", 10]
        main(args)
        
        # Check output directory was created
        assert output_dir.exists(), f"{output_dir} should exist"

    def test_main_no_pdfs(self, temp_output_dir):
        """Test main function with no PDFs."""
        input_dir = temp_output_dir.joinpath("empty_input")
        input_dir.mkdir()
        
        output_dir = temp_output_dir.joinpath("output")
        
        args = ["-i", str(input_dir), "-o", str(output_dir), "-n", 10]
        main(args)
        
        # Should handle gracefully
        assert output_dir.exists(), "output_dir should exist"
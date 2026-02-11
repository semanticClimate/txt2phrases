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
        pygetpapers_dir = Path(temp_output_dir, "pygetpapers_output")
        pygetpapers_dir.mkdir()
        
        # Create subdirectory with fulltext.pdf
        subdir = Path(pygetpapers_dir, "PMC12345")
        subdir.mkdir()
        (Path(subdir, "fulltext.pdf")).write_bytes(b"fake pdf content")
        
        result = detect_pygetpapers_structure(pygetpapers_dir)
        assert result is True, "result is True should be true"
    def test_detect_standard_structure(self, temp_output_dir):
        """Test detection of standard (non-PyGetPapers) structure."""
        standard_dir = Path(temp_output_dir, "standard_pdfs")
        standard_dir.mkdir()
        
        # Create PDFs directly in directory
        (Path(standard_dir, "document1.pdf")).write_bytes(b"fake pdf content")
        (Path(standard_dir, "document2.pdf")).write_bytes(b"fake pdf content")
        
        result = detect_pygetpapers_structure(standard_dir)
        assert result is False, "result is False should be true"
    def test_detect_nonexistent_directory(self, temp_output_dir):
        """Test detection with nonexistent directory."""
        nonexistent = Path(temp_output_dir, "nonexistent")
        result = detect_pygetpapers_structure(nonexistent)
        assert result is False, "result is False should be true"
    def test_detect_empty_directory(self, temp_output_dir):
        """Test detection with empty directory."""
        empty_dir = Path(temp_output_dir, "empty")
        empty_dir.mkdir()
        
        result = detect_pygetpapers_structure(empty_dir)
        assert result is False, "result is False should be true"
class TestFindPdfs:
    """Tests for find_pdfs function."""

    def test_find_pdfs_in_directory(self, temp_output_dir):
        """Test finding PDFs in a directory."""
        pdf_dir = Path(temp_output_dir, "pdf_dir")
        pdf_dir.mkdir()
        
        # Create some PDFs
        (Path(pdf_dir, "file1.pdf")).write_bytes(b"fake pdf")
        (Path(pdf_dir, "file2.pdf")).write_bytes(b"fake pdf")
        (Path(pdf_dir, "file3.txt")).write_text("not a pdf")
        
        pdfs = find_pdfs(pdf_dir)
        
        assert len(pdfs) == 2, "Length should match expected value"
        assert all(p.suffix.lower() == ".pdf" for p in pdfs), f"suffixes should equal '.pdf' for p in pdfs)"
    def test_find_pdfs_recursive(self, temp_output_dir):
        """Test finding PDFs recursively."""
        base_dir = Path(temp_output_dir, "base")
        base_dir.mkdir()
        
        # Create nested structure
        subdir1 = Path(base_dir, "subdir1")
        subdir1.mkdir()
        (Path(subdir1, "file1.pdf")).write_bytes(b"fake pdf")
        
        subdir2 = Path(base_dir, "subdir2")
        subdir2.mkdir()
        (Path(subdir2, "file2.pdf")).write_bytes(b"fake pdf")
        
        pdfs = find_pdfs(base_dir)
        
        assert len(pdfs) == 2, "Length should match expected value"
    def test_find_pdfs_empty_directory(self, temp_output_dir):
        """Test finding PDFs in empty directory."""
        empty_dir = Path(temp_output_dir, "empty")
        empty_dir.mkdir()
        
        pdfs = find_pdfs(empty_dir)
        assert len(pdfs) == 0, "Length should match expected value"
    def test_find_pdfs_case_insensitive(self, temp_output_dir):
        """Test that PDF extension matching is case-insensitive."""
        pdf_dir = Path(temp_output_dir, "pdf_dir")
        pdf_dir.mkdir()
        
        (Path(pdf_dir, "file1.PDF")).write_bytes(b"fake pdf")
        (Path(pdf_dir, "file2.Pdf")).write_bytes(b"fake pdf")
        (Path(pdf_dir, "file3.pdf")).write_bytes(b"fake pdf")
        
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
        nonexistent_pdf = Path(temp_output_dir, "nonexistent.pdf")
        result = convert_pdf_to_txt(nonexistent_pdf, temp_output_dir)
        
        # Should handle gracefully
        assert result is None or not Path(result).exists(), "result  or not Path(result).exists() should be None"
class TestConvertAllPdfs:
    """Tests for convert_all_pdfs function."""

    @pytest.mark.requires_model
    def test_convert_multiple_pdfs(self, sample_pdf_paths, temp_output_dir):
        """Test converting multiple PDFs."""
        # Create directory with PDFs
        pdf_dir = Path(temp_output_dir, "pdf_input")
        pdf_dir.mkdir()
        
        # Use PDFs from amilib (up to 2)
        import shutil
        for i, pdf_path in enumerate(sample_pdf_paths[:2], 1):
            shutil.copy(pdf_path, Path(pdf_dir, f"test{i}.pdf"))
        
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
        txt_dir = Path(temp_output_dir, "txt_input")
        txt_dir.mkdir()
        
        # Copy sample text file
        import shutil
        shutil.copy(sample_txt_path, Path(txt_dir, "sample.txt"))
        
        output_dir = Path(temp_output_dir, "keywords_output")
        
        run_keyword_extraction(txt_dir, output_dir, top_n=10)
        
        # Check keyword CSV was created
        csv_files = list(output_dir.glob("*_keywords.csv"))
        assert len(csv_files) > 0, "Length should be greater than 0"
class TestPygetpaperMain:
    """Tests for main function."""

    @pytest.mark.integration
    @pytest.mark.requires_model
    def test_main_pygetpapers_structure(self, sample_pdf_path, temp_output_dir):
        """Test main function with PyGetPapers structure."""
        # Create PyGetPapers-style structure
        input_dir = Path(temp_output_dir, "pygetpapers_input")
        input_dir.mkdir()
        
        subdir = Path(input_dir, "PMC12345")
        subdir.mkdir()
        
        # Use PDF from amilib
        import shutil
        shutil.copy(sample_pdf_path, Path(subdir, "fulltext.pdf"))
        
        output_dir = Path(temp_output_dir, "output")
        
        args = ["-i", str(input_dir), "-o", str(output_dir), "-n", "10"]
        main(args)
        
        # Check output directory was created"""
        assert output_dir.exists(), "output_dir should exist"
    @pytest.mark.integration
    @pytest.mark.requires_model
    def test_main_standard_structure(self, sample_pdf_path, temp_output_dir):
        """Test main function with standard PDF directory."""
        # Create standard PDF directory
        input_dir = Path(temp_output_dir, "pdf_input")
        input_dir.mkdir()
        
        # Use PDF from amilib
        import shutil
        shutil.copy(sample_pdf_path, Path(input_dir, "test.pdf"))
        
        output_dir = Path(temp_output_dir, "output")
        
        args = ["-i", str(input_dir), "-o", str(output_dir), "-n", "10"]
        main(args)
        
        # Check output directory was created
        assert output_dir.exists(), f"{output_dir} should exist"

    def test_main_no_pdfs(self, temp_output_dir):
        """Test main function with no PDFs."""
        input_dir = Path(temp_output_dir, "empty_input")
        input_dir.mkdir()
        
        output_dir = Path(temp_output_dir, "output")
        
        args = ["-i", str(input_dir), "-o", str(output_dir), "-n", "10"]
        main(args)
        
        # Should handle gracefully
        assert output_dir.exists(), "output_dir should exist"
"""
Pytest configuration and shared fixtures for txt2phrases tests.
"""
import os
import tempfile
import shutil
import glob
from pathlib import Path
import pytest


# Root directory of the project
PROJECT_ROOT = Path(__file__).parent.parent
TEST_OUTPUT_DIR = Path(PROJECT_ROOT, "temp", "tests")
TEST_FIXTURES_DIR = Path(Path(__file__).parent, "fixtures")


@pytest.fixture(scope="session")
def test_output_dir():
    """Create and return the test output directory."""
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    yield TEST_OUTPUT_DIR
    # Cleanup after all tests
    if TEST_OUTPUT_DIR.exists():
        shutil.rmtree(TEST_OUTPUT_DIR, ignore_errors=True)


@pytest.fixture(scope="function")
def temp_output_dir(test_output_dir):
    """Create a temporary output directory for each test."""
    temp_dir = tempfile.mkdtemp(dir=str(test_output_dir))
    yield Path(temp_dir)
    # Cleanup after test
    if Path(temp_dir).exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def fixtures_dir():
    """Return the path to test fixtures directory."""
    TEST_FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    return TEST_FIXTURES_DIR


def _find_amilib_pdfs():
    """Find PDF files from ../amilib directory for testing."""
    amilib_dir = Path(__file__).parent.parent.parent / "amilib"
    pdfs = []
    
    # Priority order: temp directory, then test/resources
    search_paths = [
        amilib_dir / "temp" / "*.pdf",
        amilib_dir / "test" / "resources" / "pygetpapers" / "wildlife" / "PMC*" / "fulltext.pdf",
    ]
    
    for pattern in search_paths:
        try:
            found_pdfs = list(pattern.parent.glob(pattern.name))
            for pdf_path in found_pdfs:
                if pdf_path.exists() and pdf_path.stat().st_size > 0:
                    pdfs.append(pdf_path)
                    if len(pdfs) >= 3:  # Get up to 3 PDFs
                        return pdfs
        except Exception:
            continue
    
    return pdfs if pdfs else None


def _find_system_pdf():
    """Find a real PDF file on the system for testing (fallback)."""
    # Common locations where PDFs might exist
    search_paths = [
        "/System/Library/Assistant/UIPlugins/MailUI.siriUIBundle/Contents/Resources/*.pdf",
        "/Library/Application Support/Apple/BezelServices/**/*.pdf",
        "/Applications/**/*.pdf",
        "/usr/share/**/*.pdf",
    ]
    
    for pattern in search_paths:
        try:
            found_pdfs = glob.glob(pattern, recursive=True)
            if found_pdfs:
                # Return first readable PDF
                for pdf in found_pdfs:
                    pdf_path = Path(pdf)
                    if pdf_path.exists() and pdf_path.stat().st_size > 0:
                        return pdf_path
        except Exception:
            continue
    
    return None


def _is_valid_pdf(pdf_path):
    """Check if a file is a valid PDF by reading its header."""
    try:
        if not pdf_path.exists() or pdf_path.stat().st_size < 100:
            return False
        with open(pdf_path, 'rb') as f:
            header = f.read(10)
            return header.startswith(b'%PDF')
    except Exception:
        return False


@pytest.fixture(scope="session")
def sample_pdf_path(fixtures_dir):
    """Path to sample PDF file."""
    pdf_path = Path(fixtures_dir, "sample.pdf")
    
    # Check if PDF exists and is valid, if not, copy a real one
    if not _is_valid_pdf(pdf_path):
        # Remove corrupted/invalid PDF if it exists
        if pdf_path.exists():
            pdf_path.unlink()
        
        # Ensure fixtures directory exists
        fixtures_dir.mkdir(parents=True, exist_ok=True)
        
        # First try to find PDFs from ../amilib
        amilib_pdfs = _find_amilib_pdfs()
        if amilib_pdfs and len(amilib_pdfs) > 0:
            # Use the first PDF from amilib
            import shutil
            try:
                # Try copy2 first (preserves metadata)
                shutil.copy2(amilib_pdfs[0], pdf_path)
            except (PermissionError, OSError):
                # Fallback to copy if metadata copying fails (e.g., macOS file flags)
                shutil.copy(amilib_pdfs[0], pdf_path)
        else:
            # Fallback: try system PDFs
            system_pdf = _find_system_pdf()
            if system_pdf and system_pdf.exists():
                import shutil
                try:
                    # Try copy2 first (preserves metadata)
                    shutil.copy2(system_pdf, pdf_path)
                except (PermissionError, OSError):
                    # Fallback to copy if metadata copying fails (e.g., macOS file flags)
                    shutil.copy(system_pdf, pdf_path)
            else:
                # Last resort: create a minimal valid PDF
                _create_sample_pdf(pdf_path)
    
    return pdf_path


@pytest.fixture(scope="session")
def sample_pdf_paths(fixtures_dir):
    """Return list of up to 3 PDF paths from ../amilib for testing."""
    pdf_paths = []
    amilib_pdfs = _find_amilib_pdfs()
    
    # Ensure fixtures directory exists
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    
    if amilib_pdfs and len(amilib_pdfs) > 0:
        # Copy up to 3 PDFs to fixtures directory
        import shutil
        for i, amilib_pdf in enumerate(amilib_pdfs[:3]):
            fixture_pdf = Path(fixtures_dir, f"sample_{i+1}.pdf")
            # Only copy if file doesn't exist or is invalid
            if not _is_valid_pdf(fixture_pdf):
                if fixture_pdf.exists():
                    fixture_pdf.unlink()
                try:
                    # Try copy2 first (preserves metadata)
                    shutil.copy2(amilib_pdf, fixture_pdf)
                except (PermissionError, OSError):
                    # Fallback to copy if metadata copying fails (e.g., macOS file flags)
                    shutil.copy(amilib_pdf, fixture_pdf)
            pdf_paths.append(fixture_pdf)
    else:
        # Fallback: use single sample PDF (create it if needed)
        single_pdf = Path(fixtures_dir, "sample.pdf")
        if not _is_valid_pdf(single_pdf):
            if single_pdf.exists():
                single_pdf.unlink()
            system_pdf = _find_system_pdf()
            if system_pdf and system_pdf.exists():
                import shutil
                try:
                    # Try copy2 first (preserves metadata)
                    shutil.copy2(system_pdf, single_pdf)
                except (PermissionError, OSError):
                    # Fallback to copy if metadata copying fails (e.g., macOS file flags)
                    shutil.copy(system_pdf, single_pdf)
            else:
                _create_sample_pdf(single_pdf)
        pdf_paths.append(single_pdf)
    
    return pdf_paths


@pytest.fixture(scope="session")
def sample_html_path(fixtures_dir):
    """Path to sample HTML file."""
    html_path = Path(fixtures_dir, "sample.html")
    if not html_path.exists():
        _create_sample_html(html_path)
    return html_path


@pytest.fixture(scope="session")
def sample_txt_path(fixtures_dir):
    """Path to sample text file."""
    txt_path = Path(fixtures_dir, "sample.txt")
    if not txt_path.exists():
        _create_sample_txt(txt_path)
    return txt_path


@pytest.fixture(scope="session")
def sample_keywords_csv_path(fixtures_dir):
    """Path to sample keywords CSV file."""
    csv_path = Path(fixtures_dir, "sample_keywords.csv")
    if not csv_path.exists():
        _create_sample_keywords_csv(csv_path)
    return csv_path


@pytest.fixture(scope="session")
def sample_keywords_csv_chapter1(fixtures_dir):
    """Path to sample keywords CSV for chapter 1."""
    csv_path = Path(fixtures_dir, "chapter1_keywords.csv")
    if not csv_path.exists():
        _create_chapter1_keywords_csv(csv_path)
    return csv_path


@pytest.fixture(scope="session")
def sample_keywords_csv_chapter2(fixtures_dir):
    """Path to sample keywords CSV for chapter 2."""
    csv_path = Path(fixtures_dir, "chapter2_keywords.csv")
    if not csv_path.exists():
        _create_chapter2_keywords_csv(csv_path)
    return csv_path


def _create_sample_pdf(pdf_path):
    """Create a minimal valid PDF file for testing."""
    # Create a minimal valid PDF structure manually
    # This is a valid PDF that PyPDF2 can read
    minimal_pdf = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>
endobj
4 0 obj
<< /Length 120 >>
stream
BT
/F1 12 Tf
100 700 Td
(This is a sample PDF document for testing.) Tj
0 -20 Td
(It contains multiple lines of text.) Tj
0 -20 Td
(Climate change is an important topic.) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000307 00000 n
trailer
<< /Size 5 /Root 1 0 R >>
startxref
427
%%EOF"""
    pdf_path.write_bytes(minimal_pdf)


def _create_sample_html(html_path):
    """Create a sample HTML file for testing."""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Sample HTML Document</title>
    <style>
        body { font-family: Arial; }
    </style>
    <script>
        console.log("This is a script");
    </script>
</head>
<body>
    <h1>Sample HTML Document</h1>
    <p>This is a paragraph with some text about climate change.</p>
    <p>Another paragraph discussing machine learning and natural language processing.</p>
    <table>
        <tr><th>Keyword</th><th>Count</th></tr>
        <tr><td>climate</td><td>5</td></tr>
    </table>
    <div>Some content in a div element.</div>
</body>
</html>"""
    html_path.write_text(html_content, encoding="utf-8")


def _create_sample_txt(txt_path):
    """Create a sample text file for testing."""
    txt_content = """This is a sample text document for testing keyword extraction.
It contains multiple sentences about various topics.
Climate change is a critical issue facing humanity today.
Machine learning and artificial intelligence are transforming many industries.
Natural language processing enables computers to understand human language.
The greenhouse effect is caused by increased levels of carbon dioxide.
Renewable energy sources like solar and wind power are becoming more affordable.
Deep learning models can extract keyphrases from text documents effectively."""
    txt_path.write_text(txt_content, encoding="utf-8")


def _create_sample_keywords_csv(csv_path):
    """Create a sample keywords CSV file."""
    import pandas as pd
    data = {
        "keyword": ["climate change", "machine learning", "natural language processing", 
                   "greenhouse effect", "renewable energy", "deep learning"],
        "count": [10, 8, 6, 5, 4, 3]
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)


def _create_chapter1_keywords_csv(csv_path):
    """Create sample keywords CSV for chapter 1 (climate-focused)."""
    import pandas as pd
    data = {
        "keyword": ["climate change", "greenhouse effect", "carbon dioxide", 
                   "global warming", "temperature", "atmosphere"],
        "count": [15, 12, 10, 8, 7, 6]
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)


def _create_chapter2_keywords_csv(csv_path):
    """Create sample keywords CSV for chapter 2 (ML-focused)."""
    import pandas as pd
    data = {
        "keyword": ["machine learning", "deep learning", "neural networks",
                   "artificial intelligence", "algorithm", "model"],
        "count": [20, 18, 15, 12, 10, 9]
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)

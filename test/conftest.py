"""
Pytest configuration and shared fixtures for txt2phrases tests.
"""
import tempfile
import shutil
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


@pytest.fixture(scope="session")
def sample_pdf_path(fixtures_dir):
    """Path to minimal sample PDF file (one page, no images) for fast basic tests."""
    pdf_path = Path(fixtures_dir, "sample_minimal.pdf")
    assert pdf_path.exists(), f"Fixture file {pdf_path} must exist"
    return pdf_path


@pytest.fixture(scope="session")
def sample_pdf_paths(fixtures_dir):
    """Return list of PDF paths for testing, prioritizing minimal PDF for speed."""
    pdf_paths = []
    
    # Always include minimal PDF first for fast basic tests
    minimal_pdf = Path(fixtures_dir, "sample_minimal.pdf")
    if minimal_pdf.exists():
        pdf_paths.append(minimal_pdf)
    
    # Add numbered PDFs if they exist (for integration tests)
    for i in range(2, 4):  # Start from 2 since sample_1.pdf was removed
        pdf_path = Path(fixtures_dir, f"sample_{i}.pdf")
        if pdf_path.exists():
            pdf_paths.append(pdf_path)
            if len(pdf_paths) >= 3:  # Limit to 3 PDFs total
                break
    
    # Fallback to single sample.pdf if no numbered PDFs found
    if len(pdf_paths) == 1:  # Only minimal PDF exists
        pdf_path = Path(fixtures_dir, "sample.pdf")
        if pdf_path.exists():
            pdf_paths.append(pdf_path)
    
    assert len(pdf_paths) > 0, "At least one PDF fixture must exist"
    return pdf_paths


@pytest.fixture(scope="session")
def sample_html_path(fixtures_dir):
    """Path to sample HTML file."""
    html_path = Path(fixtures_dir, "sample.html")
    assert html_path.exists(), f"Fixture file {html_path} must exist"
    return html_path


@pytest.fixture(scope="session")
def sample_txt_path(fixtures_dir):
    """Path to sample text file."""
    txt_path = Path(fixtures_dir, "sample.txt")
    assert txt_path.exists(), f"Fixture file {txt_path} must exist"
    return txt_path


@pytest.fixture(scope="session")
def sample_keywords_csv_path(fixtures_dir):
    """Path to sample keywords CSV file."""
    csv_path = Path(fixtures_dir, "sample_keywords.csv")
    assert csv_path.exists(), f"Fixture file {csv_path} must exist"
    return csv_path

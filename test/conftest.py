"""
Pytest configuration and shared fixtures for txt2phrases tests.
"""
import os
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
    """Path to sample PDF file."""
    pdf_path = Path(fixtures_dir, "sample.pdf")
    if not pdf_path.exists():
        # Create a minimal valid PDF if it doesn't exist
        _create_sample_pdf(pdf_path)
    return pdf_path


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
    try:
        from PyPDF2 import PdfWriter
        writer = PdfWriter()
        page = writer.add_page()
        page.add_text("This is a sample PDF document for testing.")
        page.add_text("It contains multiple lines of text.")
        page.add_text("Climate change is an important topic.")
        with open(pdf_path, "wb") as f:
            writer.write(f)
    except Exception as e:
        # Fallback: create a simple text file with .pdf extension
        # This will fail PDF parsing tests but allows other tests to run
        pdf_path.write_text("Sample PDF content\nLine 2\nClimate change")


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

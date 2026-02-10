# Test Suite for txt2phrases

This directory contains the test suite for the `txt2phrases` package.

## Prerequisites

**Before running tests, ensure all dependencies are installed:**

```bash
pip install -r ../requirements.txt
```

Or install the package in development mode:

```bash
pip install -e ..
```

## Test Structure

- `test_pdf2txt.py` - Tests for PDF to text conversion
- `test_html2txt.py` - Tests for HTML to text conversion
- `test_keyword.py` - Tests for keyword extraction
- `test_classify_specific.py` - Tests for keyword classification
- `test_pygetpaper.py` - Tests for auto pipeline
- `test_cli.py` - Tests for command-line interface
- `test_integration.py` - Integration tests for full pipelines
- `conftest.py` - Shared fixtures and configuration
- `fixtures/` - Test data files (PDFs, HTML, TXT, CSV)

## Running Tests

### Run all tests:
```bash
pytest test/
```

### Run specific test file:
```bash
pytest test/test_pdf2txt.py
```

### Run tests by marker:
```bash
# Unit tests only
pytest test/ -m unit

# Integration tests only
pytest test/ -m integration

# Skip slow tests
pytest test/ -m "not slow"

# Skip tests requiring model downloads
pytest test/ -m "not requires_model"
```

### Run with coverage:
```bash
pytest test/ --cov=txt2phrases --cov-report=html
```

## Test Output

Test outputs are written to `<project_root>/temp/tests/` directory. This directory is automatically cleaned up after tests complete.

## Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.cli` - CLI tests
- `@pytest.mark.slow` - Slow tests (may take >5 seconds)
- `@pytest.mark.requires_model` - Tests that download/use transformer models

## Notes

- Tests use real transformer models (no mocks) - first run may download models
- Model downloads are cached by transformers library
- Some tests may be slow due to model inference
- Test fixtures are created automatically if they don't exist
- All file operations use temporary directories that are cleaned up

## CI/CD

In CI environments, you may want to skip slow tests:
```bash
pytest test/ -m "not slow" -v
```

For full test suite (including slow tests):
```bash
pytest test/ -v
```

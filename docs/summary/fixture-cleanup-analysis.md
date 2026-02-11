# Fixture Cleanup Analysis - conftest.py

**Date:** 2026-02-11 (system date)

## Overview

Analysis of `test/conftest.py` to identify one-time fixture creation methods that can be removed, assuming fixture files are committed to git.

---

## Methods That Can Be Removed (One-Time Creation)

### 1. **`_create_sample_html()` (lines 304-328)**
- **Status:** ✅ CAN BE REMOVED
- **Reason:** File `test/fixtures/sample.html` already exists
- **Fixture:** `sample_html_path` (lines 216-222)
- **Usage:** Used by `test_cli.py`, `test_html2txt.py`, `test_integration.py`
- **Action:** Remove function, simplify fixture to just return path if file exists

### 2. **`_create_sample_txt()` (lines 331-341)**
- **Status:** ✅ CAN BE REMOVED
- **Reason:** File `test/fixtures/sample.txt` already exists
- **Fixture:** `sample_txt_path` (lines 225-231)
- **Usage:** Used by `test_cli.py`, `test_keyword.py`, `test_pygetpaper.py`
- **Action:** Remove function, simplify fixture to just return path if file exists

### 3. **`_create_sample_keywords_csv()` (lines 344-353)**
- **Status:** ✅ CAN BE REMOVED
- **Reason:** Fixture `sample_keywords_csv_path` is **NOT USED** in any tests
- **Fixture:** `sample_keywords_csv_path` (lines 234-240)
- **Usage:** ❌ Not used anywhere
- **Action:** Remove both function and fixture entirely

### 4. **`_create_chapter1_keywords_csv()` (lines 356-365)**
- **Status:** ✅ CAN BE REMOVED
- **Reason:** Fixture `sample_keywords_csv_chapter1` is **NOT USED** in any tests
- **Fixture:** `sample_keywords_csv_chapter1` (lines 243-249)
- **Usage:** ❌ Not used anywhere
- **Action:** Remove both function and fixture entirely

### 5. **`_create_chapter2_keywords_csv()` (lines 368-377)**
- **Status:** ✅ CAN BE REMOVED
- **Reason:** Fixture `sample_keywords_csv_chapter2` is **NOT USED** in any tests
- **Fixture:** `sample_keywords_csv_chapter2` (lines 252-258)
- **Usage:** ❌ Not used anywhere
- **Action:** Remove both function and fixture entirely

---

## Methods That MUST Be Kept (Runtime Validation/Creation)

### 1. **`_create_sample_pdf()` (lines 261-301)**
- **Status:** ❌ KEEP (Fallback only)
- **Reason:** Used as fallback when no valid PDFs with extractable text are found
- **Usage:** Called by `sample_pdf_path` and `sample_pdf_paths` fixtures as last resort
- **Note:** PDFs need validation for extractable text, so this is a safety fallback

### 2. **`_find_amilib_pdfs()` (lines 45-69)**
- **Status:** ❌ KEEP
- **Reason:** Dynamically finds PDFs from `../amilib` with extractable text validation
- **Usage:** Used by `sample_pdf_path` and `sample_pdf_paths` fixtures
- **Note:** Runtime operation, validates PDFs have extractable text

### 3. **`_find_system_pdf()` (lines 72-95)**
- **Status:** ❌ KEEP
- **Reason:** Fallback to find system PDFs when amilib PDFs not available
- **Usage:** Used by `sample_pdf_path` and `sample_pdf_paths` fixtures
- **Note:** Runtime operation, validates PDFs have extractable text

### 4. **`_is_valid_pdf()` (lines 98-107)**
- **Status:** ❌ KEEP
- **Reason:** Validates PDF file structure (checks header)
- **Usage:** Used by PDF fixtures to validate existing PDFs
- **Note:** Runtime validation, not one-time creation

### 5. **`_has_extractable_text()` (lines 110-123)**
- **Status:** ❌ KEEP
- **Reason:** Validates PDFs have extractable text content
- **Usage:** Used by PDF fixtures and finder functions
- **Note:** Runtime validation, critical for test reliability

---

## Fixtures That Can Be Simplified

### 1. **`sample_html_path` (lines 216-222)**
- **Current:** Checks if file exists, creates if missing
- **Proposed:** Simplify to just return path (assume file is committed)
- **Change:**
  ```python
  @pytest.fixture(scope="session")
  def sample_html_path(fixtures_dir):
      """Path to sample HTML file."""
      html_path = Path(fixtures_dir, "sample.html")
      assert html_path.exists(), f"Fixture file {html_path} must exist"
      return html_path
  ```

### 2. **`sample_txt_path` (lines 225-231)**
- **Current:** Checks if file exists, creates if missing
- **Proposed:** Simplify to just return path (assume file is committed)
- **Change:**
  ```python
  @pytest.fixture(scope="session")
  def sample_txt_path(fixtures_dir):
      """Path to sample text file."""
      txt_path = Path(fixtures_dir, "sample.txt")
      assert txt_path.exists(), f"Fixture file {txt_path} must exist"
      return txt_path
  ```

---

## Fixtures That Can Be Removed Entirely

### 1. **`sample_keywords_csv_path` (lines 234-240)**
- **Status:** ✅ REMOVE
- **Reason:** Not used in any tests
- **Dependencies:** `_create_sample_keywords_csv()` (also remove)

### 2. **`sample_keywords_csv_chapter1` (lines 243-249)**
- **Status:** ✅ REMOVE
- **Reason:** Not used in any tests
- **Dependencies:** `_create_chapter1_keywords_csv()` (also remove)

### 3. **`sample_keywords_csv_chapter2` (lines 252-258)**
- **Status:** ✅ REMOVE
- **Reason:** Not used in any tests
- **Dependencies:** `_create_chapter2_keywords_csv()` (also remove)

---

## Summary

### Can Be Removed:
1. ✅ `_create_sample_html()` function (lines 304-328)
2. ✅ `_create_sample_txt()` function (lines 331-341)
3. ✅ `_create_sample_keywords_csv()` function (lines 344-353)
4. ✅ `_create_chapter1_keywords_csv()` function (lines 356-365)
5. ✅ `_create_chapter2_keywords_csv()` function (lines 368-377)
6. ✅ `sample_keywords_csv_path` fixture (lines 234-240)
7. ✅ `sample_keywords_csv_chapter1` fixture (lines 243-249)
8. ✅ `sample_keywords_csv_chapter2` fixture (lines 252-258)

### Must Be Kept:
1. ❌ `_create_sample_pdf()` - Fallback for PDF creation
2. ❌ `_find_amilib_pdfs()` - Runtime PDF discovery
3. ❌ `_find_system_pdf()` - Runtime PDF discovery
4. ❌ `_is_valid_pdf()` - Runtime PDF validation
5. ❌ `_has_extractable_text()` - Runtime PDF text validation

### Can Be Simplified:
1. 🔄 `sample_html_path` - Remove creation logic, add assertion
2. 🔄 `sample_txt_path` - Remove creation logic, add assertion

---

## Estimated Code Reduction

- **Lines removed:** ~135 lines (5 functions + 3 fixtures)
- **Lines simplified:** ~12 lines (2 fixtures)
- **Total reduction:** ~147 lines

---

## Prerequisites for Cleanup

1. ✅ Ensure `test/fixtures/sample.html` is committed to git
2. ✅ Ensure `test/fixtures/sample.txt` is committed to git
3. ✅ Verify no tests depend on CSV fixtures (confirmed - none found)
4. ✅ Run full test suite after cleanup to verify

---

## Notes

- PDF fixtures (`sample_pdf_path`, `sample_pdf_paths`) require runtime validation because PDFs need to have extractable text, which cannot be guaranteed by file existence alone.
- CSV fixtures were likely created for future use but are currently unused.
- HTML and TXT fixtures can be simplified because their content is static and doesn't require validation beyond file existence.

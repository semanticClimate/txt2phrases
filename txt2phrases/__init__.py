__version__ = "1.0.4"

from txt2phrases.pdf2txt import convert_pdf_to_text
from txt2phrases.html2txt import convert_html_to_text
from txt2phrases.classify_specific import classify_keywords_split_files

__all__ = [
    "convert_pdf_to_text",
    "convert_html_to_text",
    "KeywordExtraction",
    "classify_keywords_split_files",
]


def __getattr__(name):
    """
    Lazily import KeywordExtraction on first access, so `import txt2phrases`
    doesn't eagerly pull in transformers/torch and load the keyphrase model
    (slow, and unnecessary for callers who only need pdf2txt/html2txt/merge).
    """
    if name == "KeywordExtraction":
        from txt2phrases.keyword import KeywordExtraction
        return KeywordExtraction
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
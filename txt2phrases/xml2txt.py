# xml2txt.py
"""
Convert XML documents (e.g. JATS-format scientific full-text XML, such as
the fulltext.xml pygetpapers can download from Europe PMC via its -x flag)
to plain text.
"""
import logging
import os
from pathlib import Path
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# JATS (Journal Article Tag Suite) back-matter tags: references, notes,
# acknowledgements, footnotes, glossary, appendices - none of these are
# core article content, and references in particular tend to be a heavy
# source of journal-name/author-name noise for downstream keyword
# extraction (similar in spirit to the stopword filtering in keyphrases).
_BACK_MATTER_TAGS = ("back", "ref-list", "ref")


def find_xml_files(base_path):
    """
    Recursively find all .xml files under `base_path`.

    Unlike a flat glob, this walks into subfolders - needed because
    PyGetPapers-style output nests each paper's fulltext.xml inside its
    own PMC-numbered subfolder (base_path/PMC12345/fulltext.xml), rather
    than placing XML files directly in base_path itself.

    Returns
    -------
    list[Path]
        Sorted list of .xml file paths found.
    """
    base_path = Path(base_path)
    xml_files = []
    for root, _, files in os.walk(base_path):
        for f in files:
            if f.lower().endswith(".xml"):
                xml_files.append(Path(root) / f)
    return sorted(xml_files)


def _default_output_name(xml_path):
    """
    Decide the output .txt base name for a given XML file.

    PyGetPapers always names the file itself "fulltext.xml" regardless of
    the paper, with the actual paper identity carried by the parent
    folder name instead (e.g. PMC12345/fulltext.xml). Converting many such
    files into one output folder using the file's own name would collide
    (every one would want to be "fulltext.txt"), so for files named
    "fulltext*", the parent folder's name is used instead - mirroring the
    same convention pygetpaper.py already uses for PDF conversion.

    For any other filename, the file's own stem is used unchanged (this
    keeps single-file and flat-folder usage exactly as before).
    """
    xml_path = Path(xml_path)
    if xml_path.stem.lower().startswith("fulltext"):
        return xml_path.parent.name
    return xml_path.stem


def convert_xml_to_text(xml_path, output_folder, strip_references=True, output_name=None):
    """
    Convert a single XML file to plain text and save it.

    Parameters
    ----------
    xml_path : str | Path
    output_folder : str | Path
    strip_references : bool
        If True (default), JATS back-matter (<back>, and any stray
        <ref-list>/<ref> elements found outside it) is removed before
        extracting text - this drops the references/bibliography,
        acknowledgements, footnotes, and similar non-content sections.
        If False, the full document text is kept, references included.
    output_name : str | None
        Base name (without extension) for the output .txt file. If not
        given, defaults to the parent folder's name for PyGetPapers-style
        "fulltext.xml" files (to avoid every paper colliding on the same
        output name), or the input file's own stem otherwise.

    Returns
    -------
    str | None
        Path to the written .txt file, or None on failure.
    """
    try:
        os.makedirs(output_folder, exist_ok=True)

        with open(xml_path, "r", encoding="utf-8") as f:
            xml_content = f.read()

        soup = BeautifulSoup(xml_content, "xml")

        if strip_references:
            for tag_name in _BACK_MATTER_TAGS:
                for tag in soup.find_all(tag_name):
                    tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        base_name = output_name if output_name else _default_output_name(xml_path)
        txt_path = os.path.join(output_folder, base_name + ".txt")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        return txt_path
    except Exception as e:
        logger.error(f"[ERROR] Failed to process {xml_path}: {e}")
        return None

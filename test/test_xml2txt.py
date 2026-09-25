# -*- coding: utf-8 -*-
"""
Unit tests for xml2txt module.
"""
import sys
from pathlib import Path

import pytest

from txt2phrases.xml2txt import convert_xml_to_text, find_xml_files
from txt2phrases.cli import main


SAMPLE_JATS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" article-type="research-article">
  <front>
    <article-meta>
      <title-group>
        <article-title>Widespread coral bleaching across subtropical Japan</article-title>
      </title-group>
      <abstract>
        <p>Marine heatwaves in 2024 drove record-breaking sea surface temperatures.</p>
      </abstract>
    </article-meta>
  </front>
  <body>
    <sec>
      <title>Introduction</title>
      <p>Coral bleaching is a major threat to reef ecosystems under climate change.</p>
    </sec>
  </body>
  <back>
    <ack>
      <p>We thank the field teams for their assistance.</p>
    </ack>
    <ref-list>
      <ref id="r1"><mixed-citation>Smith J, et al. Scientific Reports. 2023.</mixed-citation></ref>
    </ref-list>
  </back>
</article>
"""


@pytest.fixture
def sample_xml_path(tmp_path):
    xml_path = Path(tmp_path, "sample.xml")
    xml_path.write_text(SAMPLE_JATS_XML, encoding="utf-8")
    return xml_path


class TestConvertXmlToText:
    """Tests for convert_xml_to_text function."""

    def test_convert_valid_xml(self, sample_xml_path, temp_output_dir):
        result = convert_xml_to_text(sample_xml_path, temp_output_dir)

        assert result is not None
        assert Path(result).exists()
        assert Path(result).suffix == ".txt"
        content = Path(result).read_text(encoding="utf-8")
        assert len(content) > 0
        assert "coral bleaching" in content.lower()

    def test_output_filename_matches_input(self, sample_xml_path, temp_output_dir):
        result = convert_xml_to_text(sample_xml_path, temp_output_dir)

        expected_name = sample_xml_path.stem + ".txt"
        assert Path(result).name == expected_name

    def test_references_stripped_by_default(self, sample_xml_path, temp_output_dir):
        result = convert_xml_to_text(sample_xml_path, temp_output_dir)
        content = Path(result).read_text(encoding="utf-8")

        assert "Smith J" not in content, "reference citation should be stripped by default"
        assert "Scientific Reports" not in content, "reference journal name should be stripped"

    def test_acknowledgements_stripped_by_default(self, sample_xml_path, temp_output_dir):
        result = convert_xml_to_text(sample_xml_path, temp_output_dir)
        content = Path(result).read_text(encoding="utf-8")

        assert "thank the field teams" not in content, "ack section (inside <back>) should be stripped"

    def test_body_content_always_kept(self, sample_xml_path, temp_output_dir):
        result = convert_xml_to_text(sample_xml_path, temp_output_dir)
        content = Path(result).read_text(encoding="utf-8")

        assert "Introduction" in content
        assert "reef ecosystems" in content
        assert "Marine heatwaves" in content, "abstract should be kept"

    def test_keep_references_opt_out(self, sample_xml_path, temp_output_dir):
        result = convert_xml_to_text(sample_xml_path, temp_output_dir, strip_references=False)
        content = Path(result).read_text(encoding="utf-8")

        assert "Smith J" in content
        assert "thank the field teams" in content

    def test_invalid_file_handling(self, temp_output_dir):
        result = convert_xml_to_text("nonexistent_file.xml", temp_output_dir)

        assert result is None, "should return None rather than raising for a missing file"

    def test_malformed_xml_does_not_crash(self, tmp_path, temp_output_dir):
        bad_xml = Path(tmp_path, "bad.xml")
        bad_xml.write_text("<article><body><p>Unclosed tag", encoding="utf-8")

        result = convert_xml_to_text(bad_xml, temp_output_dir)

        # BeautifulSoup's XML parser (lxml) recovers from many malformed
        # inputs rather than raising, so this should still succeed rather
        # than crash the pipeline.
        assert result is not None
        assert Path(result).exists()

    def test_fulltext_xml_renamed_to_parent_folder(self, tmp_path, temp_output_dir):
        """
        PyGetPapers always names the file itself 'fulltext.xml', with the
        real identity carried by the parent PMC-numbered folder. Converting
        it directly should use that parent folder's name, not 'fulltext'.
        """
        paper_dir = Path(tmp_path, "PMC13229102")
        paper_dir.mkdir()
        xml_path = Path(paper_dir, "fulltext.xml")
        xml_path.write_text(SAMPLE_JATS_XML, encoding="utf-8")

        result = convert_xml_to_text(xml_path, temp_output_dir)

        assert Path(result).name == "PMC13229102.txt"

    def test_non_fulltext_filename_unaffected(self, sample_xml_path, temp_output_dir):
        """A normally-named XML file should keep its own name, unaffected."""
        result = convert_xml_to_text(sample_xml_path, temp_output_dir)

        assert Path(result).name == sample_xml_path.stem + ".txt"

    def test_explicit_output_name_override(self, sample_xml_path, temp_output_dir):
        result = convert_xml_to_text(sample_xml_path, temp_output_dir, output_name="custom_name")

        assert Path(result).name == "custom_name.txt"


class TestFindXmlFiles:
    """Tests for find_xml_files() - recursive XML discovery."""

    def test_finds_flat_xml_files(self, tmp_path):
        Path(tmp_path, "a.xml").write_text(SAMPLE_JATS_XML, encoding="utf-8")
        Path(tmp_path, "b.xml").write_text(SAMPLE_JATS_XML, encoding="utf-8")

        found = find_xml_files(tmp_path)

        assert len(found) == 2

    def test_finds_nested_pygetpapers_style_xml_files(self, tmp_path):
        for folder in ("PMC11111111", "PMC22222222", "PMC33333333"):
            paper_dir = Path(tmp_path, folder)
            paper_dir.mkdir()
            Path(paper_dir, "fulltext.xml").write_text(SAMPLE_JATS_XML, encoding="utf-8")

        found = find_xml_files(tmp_path)

        assert len(found) == 3
        assert all(f.name == "fulltext.xml" for f in found)

    def test_empty_directory_returns_empty_list(self, tmp_path):
        found = find_xml_files(tmp_path)
        assert found == []


class TestCliXml2Txt:
    """Tests for the xml2txt CLI command."""

    def test_xml2txt_single_file(self, sample_xml_path, temp_output_dir):
        sys.argv = ["txt2phrases", "xml2txt", "-i", str(sample_xml_path), "-o", str(temp_output_dir)]
        main()

        expected = Path(temp_output_dir, sample_xml_path.stem + ".txt")
        assert expected.exists()
        content = expected.read_text(encoding="utf-8")
        assert "coral bleaching" in content.lower()
        assert "Smith J" not in content, "references should be stripped by default via CLI too"

    def test_xml2txt_directory(self, tmp_path, temp_output_dir):
        input_dir = Path(tmp_path, "xml_files")
        input_dir.mkdir()
        Path(input_dir, "paper1.xml").write_text(SAMPLE_JATS_XML, encoding="utf-8")
        Path(input_dir, "paper2.xml").write_text(SAMPLE_JATS_XML, encoding="utf-8")

        sys.argv = ["txt2phrases", "xml2txt", "-i", str(input_dir), "-o", str(temp_output_dir)]
        main()

        assert Path(temp_output_dir, "paper1.txt").exists()
        assert Path(temp_output_dir, "paper2.txt").exists()

    def test_xml2txt_pygetpapers_style_nested_directory(self, tmp_path, temp_output_dir):
        """
        Reproduces real PyGetPapers output: papers_xml/PMC.../fulltext.xml,
        one subfolder per paper, every file literally named 'fulltext.xml'.
        A flat glob would find none of these; xml2txt needs to walk in and
        rename each output after its parent folder to avoid collisions.
        """
        input_dir = Path(tmp_path, "papers_xml")
        for folder in ("PMC11111111", "PMC22222222", "PMC33333333"):
            paper_dir = Path(input_dir, folder)
            paper_dir.mkdir(parents=True)
            Path(paper_dir, "fulltext.xml").write_text(SAMPLE_JATS_XML, encoding="utf-8")

        sys.argv = ["txt2phrases", "xml2txt", "-i", str(input_dir), "-o", str(temp_output_dir)]
        main()

        assert Path(temp_output_dir, "PMC11111111.txt").exists()
        assert Path(temp_output_dir, "PMC22222222.txt").exists()
        assert Path(temp_output_dir, "PMC33333333.txt").exists()
        assert not Path(temp_output_dir, "fulltext.txt").exists(), (
            "outputs should be renamed per-paper, not collide on the generic 'fulltext' name"
        )

    def test_xml2txt_keep_references_flag(self, sample_xml_path, temp_output_dir):
        sys.argv = [
            "txt2phrases", "xml2txt",
            "-i", str(sample_xml_path), "-o", str(temp_output_dir),
            "--keep-references",
        ]
        main()

        expected = Path(temp_output_dir, sample_xml_path.stem + ".txt")
        content = expected.read_text(encoding="utf-8")
        assert "Smith J" in content

    def test_xml2txt_missing_args(self):
        sys.argv = ["txt2phrases", "xml2txt"]

        with pytest.raises(SystemExit):
            main()

    def test_xml2txt_invalid_path(self, temp_output_dir, capsys):
        sys.argv = ["txt2phrases", "xml2txt", "-i", "does_not_exist.xml", "-o", str(temp_output_dir)]
        main()

        captured = capsys.readouterr()
        assert "No XML files found" in captured.out

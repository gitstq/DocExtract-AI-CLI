"""Tests for document extractor module."""

import os
import tempfile
import pytest
from docextract.extractor import DocumentExtractor


class TestDocumentExtractor:
    """Test cases for DocumentExtractor."""

    def setup_method(self):
        self.extractor = DocumentExtractor()

    def test_extract_txt(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Hello, World!\nThis is a test.")
            path = f.name
        try:
            result = self.extractor.extract(path)
            assert result["format"] == "txt"
            assert "Hello, World!" in result["text"]
            assert result["metadata"]["word_count"] == 6
        finally:
            os.unlink(path)

    def test_extract_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"name": "test", "value": 123}')
            path = f.name
        try:
            result = self.extractor.extract(path)
            assert result["format"] == "json"
            assert '"name": "test"' in result["text"]
        finally:
            os.unlink(path)

    def test_extract_csv(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("name,age\nJohn,30\nJane,25")
            path = f.name
        try:
            result = self.extractor.extract(path)
            assert result["format"] == "csv"
            assert "John" in result["text"]
        finally:
            os.unlink(path)

    def test_extract_html(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<html><body><h1>Title</h1><p>Content here</p></body></html>")
            path = f.name
        try:
            result = self.extractor.extract(path)
            assert result["format"] == "html"
            assert "Title" in result["text"]
            assert "<html>" not in result["text"]
        finally:
            os.unlink(path)

    def test_extract_md(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Heading\n\nSome markdown content.")
            path = f.name
        try:
            result = self.extractor.extract(path)
            assert result["format"] == "md"
            assert "Heading" in result["text"]
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            self.extractor.extract("/nonexistent/file.txt")

    def test_unsupported_format(self):
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            f.write(b"test")
            path = f.name
        try:
            with pytest.raises(ValueError):
                self.extractor.extract(path)
        finally:
            os.unlink(path)

    def test_metadata_extraction(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Contact: test@example.com\nPrice: $100\nDate: 2024-01-15\nURL: https://example.com")
            path = f.name
        try:
            result = self.extractor.extract(path)
            meta = result["metadata"]
            assert meta["has_emails"] == True
            assert meta["has_currency"] == True
            assert meta["has_dates"] == True
            assert meta["has_urls"] == True
        finally:
            os.unlink(path)

    def test_list_supported_formats(self):
        formats = DocumentExtractor.list_supported_formats()
        assert ".txt" in formats
        assert ".pdf" in formats
        assert ".docx" in formats
        assert ".html" in formats

    def test_truncation(self):
        extractor = DocumentExtractor(max_chars=10)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("This is a very long text that should be truncated.")
            path = f.name
        try:
            result = extractor.extract(path)
            assert result["truncated"] == True
            assert len(result["text"]) <= 10
        finally:
            os.unlink(path)

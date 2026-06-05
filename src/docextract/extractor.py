"""
Document Text Extraction Module
Extracts text from various document formats using zero-dependency Python.
"""

import base64
import io
import json
import os
import re
import struct
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DocumentExtractor:
    """Extracts text content from various document formats."""

    SUPPORTED_FORMATS = {
        ".txt": "text",
        ".md": "text",
        ".json": "json",
        ".csv": "csv",
        ".html": "html",
        ".htm": "html",
        ".xml": "xml",
        ".pdf": "pdf",
        ".docx": "docx",
        ".pptx": "pptx",
        ".xlsx": "xlsx",
    }

    def __init__(self, max_chars: int = 50000):
        self.max_chars = max_chars

    def extract(self, file_path: str) -> Dict[str, any]:
        """Extract text and metadata from a document."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {ext}")

        format_type = self.SUPPORTED_FORMATS[ext]
        extractor_map = {
            "text": self._extract_text,
            "json": self._extract_json,
            "csv": self._extract_csv,
            "html": self._extract_html,
            "xml": self._extract_xml,
            "pdf": self._extract_pdf,
            "docx": self._extract_docx,
            "pptx": self._extract_pptx,
            "xlsx": self._extract_xlsx,
        }

        extractor = extractor_map.get(format_type)
        if not extractor:
            raise ValueError(f"No extractor available for: {ext}")

        text = extractor(file_path)
        metadata = self._extract_metadata(path, text)

        return {
            "file_path": str(path.absolute()),
            "file_name": path.name,
            "file_size": path.stat().st_size,
            "format": ext.lstrip("."),
            "text": text[:self.max_chars],
            "char_count": len(text),
            "truncated": len(text) > self.max_chars,
            "metadata": metadata,
        }

    def _extract_text(self, file_path: str) -> str:
        """Extract text from plain text files."""
        encodings = ["utf-8", "utf-16", "gbk", "latin-1", "cp1252"]
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
        # Fallback: read as binary and decode with replacement
        with open(file_path, "rb") as f:
            return f.read().decode("utf-8", errors="replace")

    def _extract_json(self, file_path: str) -> str:
        """Extract and pretty-print JSON content."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _extract_csv(self, file_path: str) -> str:
        """Extract CSV content as formatted text."""
        text = self._extract_text(file_path)
        lines = text.strip().split("\n")
        if len(lines) <= 1:
            return text
        # Parse and format
        result = ["CSV Data:"]
        delimiter = "," if text.count(",") > text.count("\t") else "\t"
        for i, line in enumerate(lines[:100]):  # Limit rows
            cells = line.split(delimiter)
            result.append(f"  Row {i}: {' | '.join(c.strip() for c in cells)}")
        if len(lines) > 100:
            result.append(f"  ... ({len(lines) - 100} more rows)")
        return "\n".join(result)

    def _extract_html(self, file_path: str) -> str:
        """Extract text from HTML by stripping tags."""
        text = self._extract_text(file_path)
        # Remove script and style content
        text = re.sub(r"<script[^>]*>[\s\S]*?</script>", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"<style[^>]*>[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
        # Remove tags
        text = re.sub(r"<[^>]+>", " ", text)
        # Decode entities
        text = self._decode_html_entities(text)
        # Clean whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _extract_xml(self, file_path: str) -> str:
        """Extract text from XML by stripping tags."""
        text = self._extract_text(file_path)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF using zero-dependency approach."""
        try:
            return self._extract_pdf_text(file_path)
        except Exception as e:
            return f"[PDF extraction failed: {str(e)}]"

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF by parsing PDF structure."""
        with open(file_path, "rb") as f:
            content = f.read()

        # Check PDF header
        if not content.startswith(b"%PDF"):
            raise ValueError("Not a valid PDF file")

        text_parts = []
        # Find all text streams
        stream_pattern = re.compile(b"stream\r?\n(.*?)(?:\r?\n)?endstream", re.DOTALL)
        xref_pattern = re.compile(br"xref\s*\n.*?\n?trailer", re.DOTALL)

        # Try to extract text from content streams
        # Look for BT...ET blocks (Begin/End Text)
        bt_pattern = re.compile(br"BT\s*(.*?)\s*ET", re.DOTALL)

        for match in bt_pattern.finditer(content):
            stream = match.group(1)
            try:
                text = self._parse_pdf_text_stream(stream)
                if text.strip():
                    text_parts.append(text)
            except Exception:
                continue

        # Fallback: extract strings from entire file
        if not text_parts:
            string_pattern = re.compile(br"\(([^\)]{1,500})\)")
            for match in string_pattern.finditer(content):
                try:
                    s = match.group(1).decode("latin-1", errors="ignore")
                    # Filter out binary garbage
                    if len(s) > 2 and any(c.isalnum() for c in s):
                        text_parts.append(s)
                except Exception:
                    continue

        result = " ".join(text_parts)
        result = re.sub(r"\s+", " ", result).strip()
        return result

    def _parse_pdf_text_stream(self, stream: bytes) -> str:
        """Parse PDF text stream to extract readable text."""
        text = ""
        i = 0
        while i < len(stream):
            # Look for string literals
            if stream[i:i+1] == b"(":
                j = i + 1
                depth = 1
                while j < len(stream) and depth > 0:
                    if stream[j:j+1] == b"\\":
                        j += 2
                    elif stream[j:j+1] == b"(":
                        depth += 1
                        j += 1
                    elif stream[j:j+1] == b")":
                        depth -= 1
                        j += 1
                    else:
                        j += 1
                try:
                    s = stream[i+1:j-1].decode("utf-8", errors="ignore")
                    s = s.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")
                    s = s.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")
                    text += s + " "
                except Exception:
                    pass
                i = j
            else:
                i += 1
        return text

    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX (ZIP-based XML)."""
        try:
            with zipfile.ZipFile(file_path, "r") as zf:
                # Read document.xml
                if "word/document.xml" in zf.namelist():
                    xml_content = zf.read("word/document.xml").decode("utf-8")
                    return self._extract_xml_text(xml_content)
                return "[Empty DOCX document]"
        except zipfile.BadZipFile:
            raise ValueError("Invalid DOCX file")

    def _extract_pptx(self, file_path: str) -> str:
        """Extract text from PPTX (ZIP-based XML)."""
        try:
            with zipfile.ZipFile(file_path, "r") as zf:
                text_parts = []
                slide_num = 1
                while True:
                    slide_path = f"ppt/slides/slide{slide_num}.xml"
                    if slide_path not in zf.namelist():
                        break
                    xml_content = zf.read(slide_path).decode("utf-8")
                    slide_text = self._extract_xml_text(xml_content)
                    if slide_text.strip():
                        text_parts.append(f"--- Slide {slide_num} ---")
                        text_parts.append(slide_text)
                    slide_num += 1
                return "\n\n".join(text_parts) if text_parts else "[Empty PPTX presentation]"
        except zipfile.BadZipFile:
            raise ValueError("Invalid PPTX file")

    def _extract_xlsx(self, file_path: str) -> str:
        """Extract text from XLSX (ZIP-based XML)."""
        try:
            with zipfile.ZipFile(file_path, "r") as zf:
                text_parts = []
                # Read shared strings
                shared_strings = {}
                if "xl/sharedStrings.xml" in zf.namelist():
                    ss_xml = zf.read("xl/sharedStrings.xml").decode("utf-8")
                    si_pattern = re.compile(r"<si>(.*?)</si>", re.DOTALL)
                    t_pattern = re.compile(r"<t[^>]*>([^<]*)</t>")
                    for i, si_match in enumerate(si_pattern.finditer(ss_xml)):
                        texts = t_pattern.findall(si_match.group(1))
                        shared_strings[i] = "".join(texts)

                # Read sheet data
                sheet_num = 1
                while True:
                    sheet_path = f"xl/worksheets/sheet{sheet_num}.xml"
                    if sheet_path not in zf.namelist():
                        break
                    xml_content = zf.read(sheet_path).decode("utf-8")
                    text_parts.append(f"--- Sheet {sheet_num} ---")

                    # Extract cell values
                    row_pattern = re.compile(r"<row[^>]*>(.*?)</row>", re.DOTALL)
                    cell_pattern = re.compile(r"<c[^>]*t=\"s\"[^>]*><v>(\d+)</v></c>")
                    cell_inline_pattern = re.compile(r"<c[^>]*>(?:<is>)?<t[^>]*>([^<]*)</t>(?:</is>)?</c>")

                    for row_match in row_pattern.finditer(xml_content):
                        row_text = []
                        row_xml = row_match.group(1)
                        # Shared string cells
                        for cell_match in cell_pattern.finditer(row_xml):
                            idx = int(cell_match.group(1))
                            if idx in shared_strings:
                                row_text.append(shared_strings[idx])
                        # Inline string cells
                        for cell_match in cell_inline_pattern.finditer(row_xml):
                            row_text.append(cell_match.group(1))
                        if row_text:
                            text_parts.append(" | ".join(row_text))
                    sheet_num += 1

                return "\n".join(text_parts) if text_parts else "[Empty XLSX workbook]"
        except zipfile.BadZipFile:
            raise ValueError("Invalid XLSX file")

    def _extract_xml_text(self, xml_content: str) -> str:
        """Extract text from XML content."""
        # Extract text from w:t tags (WordprocessingML)
        text_pattern = re.compile(r"<w:t[^>]*>([^<]*)</w:t>")
        texts = text_pattern.findall(xml_content)
        result = " ".join(texts)
        result = re.sub(r"\s+", " ", result).strip()
        return result

    def _decode_html_entities(self, text: str) -> str:
        """Decode common HTML entities."""
        entities = {
            "&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"',
            "&apos;": "'", "&nbsp;": " ", "&ndash;": "–", "&mdash;": "—",
            "&copy;": "©", "&reg;": "®", "&trade;": "™",
        }
        for entity, char in entities.items():
            text = text.replace(entity, char)
        # Numeric entities
        text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
        text = re.sub(r"&#x([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16)), text)
        return text

    def _extract_metadata(self, path: Path, text: str) -> Dict[str, any]:
        """Extract basic metadata from document."""
        metadata = {
            "word_count": len(text.split()),
            "line_count": text.count("\n") + 1,
            "has_numbers": bool(re.search(r"\d", text)),
            "has_dates": bool(re.search(r"\d{1,4}[/-]\d{1,2}[/-]\d{1,4}", text)),
            "has_emails": bool(re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)),
            "has_urls": bool(re.search(r"https?://[^\s]+", text)),
            "has_currency": bool(re.search(r"[\$\€\£\¥]\s*[\d,]+", text)),
        }
        return metadata

    @classmethod
    def list_supported_formats(cls) -> List[str]:
        """Return list of supported file extensions."""
        return list(cls.SUPPORTED_FORMATS.keys())

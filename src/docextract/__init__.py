"""
DocExtract-AI-CLI
Lightweight Terminal AI Intelligent Document Structured Extraction Engine
轻量级终端AI智能文档结构化提取引擎

Zero-dependency core for document text extraction and AI-powered structured data extraction.
"""

__version__ = "1.0.0"
__author__ = "gitstq"
__license__ = "MIT"

from .extractor import DocumentExtractor
from .schema import Schema, SchemaField
from .pipeline import ExtractionPipeline
from .providers import AIProvider, OpenAIProvider, OllamaProvider
from .tui import TUIApp

__all__ = [
    "DocumentExtractor",
    "Schema",
    "SchemaField",
    "ExtractionPipeline",
    "AIProvider",
    "OpenAIProvider",
    "OllamaProvider",
    "TUIApp",
]

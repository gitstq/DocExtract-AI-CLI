"""
Extraction Pipeline Module
Orchestrates document extraction, AI processing, and result validation.
"""

import json
import os
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable

from .extractor import DocumentExtractor
from .providers import AIProvider, ProviderRegistry
from .schema import Schema


class ExtractionResult:
    """Represents the result of a document extraction."""

    def __init__(
        self,
        file_path: str,
        schema_name: str,
        data: Dict[str, Any],
        validation_errors: List[str],
        processing_time: float,
        char_count: int,
        model_used: str,
        provider_used: str,
        timestamp: str = None,
    ):
        self.file_path = file_path
        self.schema_name = schema_name
        self.data = data
        self.validation_errors = validation_errors
        self.processing_time = processing_time
        self.char_count = char_count
        self.model_used = model_used
        self.provider_used = provider_used
        self.timestamp = timestamp or datetime.now().isoformat()
        self.is_valid = len(validation_errors) == 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "file_path": self.file_path,
            "schema_name": self.schema_name,
            "data": self.data,
            "validation_errors": self.validation_errors,
            "is_valid": self.is_valid,
            "processing_time_seconds": round(self.processing_time, 2),
            "char_count": self.char_count,
            "model_used": self.model_used,
            "provider_used": self.provider_used,
            "timestamp": self.timestamp,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert result to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def to_csv_row(self) -> str:
        """Convert result to CSV row (flat structure)."""
        flat = self._flatten_dict(self.data)
        return ",".join(f"{k}={v}" for k, v in flat.items())

    def _flatten_dict(self, d: Dict, parent_key: str = "") -> Dict[str, str]:
        """Flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key).items())
            elif isinstance(v, list):
                items.append((new_key, json.dumps(v, ensure_ascii=False)))
            else:
                items.append((new_key, str(v) if v is not None else ""))
        return dict(items)


class ExtractionPipeline:
    """Pipeline for extracting structured data from documents."""

    def __init__(
        self,
        provider: AIProvider,
        schema: Schema,
        model: str = "default",
        db_path: Optional[str] = None,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ):
        self.provider = provider
        self.schema = schema
        self.model = model
        self.db_path = db_path or os.path.expanduser("~/.docextract/history.db")
        self.progress_callback = progress_callback
        self.extractor = DocumentExtractor()
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database for extraction history."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS extractions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                schema_name TEXT NOT NULL,
                data TEXT NOT NULL,
                validation_errors TEXT,
                is_valid INTEGER NOT NULL,
                processing_time REAL,
                char_count INTEGER,
                model_used TEXT,
                provider_used TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_schema ON extractions(schema_name)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON extractions(timestamp)
        """)
        conn.commit()
        conn.close()

    def process_file(self, file_path: str) -> ExtractionResult:
        """Process a single document file."""
        start_time = time.time()

        # Step 1: Extract text from document
        doc_info = self.extractor.extract(file_path)
        text = doc_info["text"]

        # Step 2: Generate AI prompt from schema
        schema_prompt = self.schema.generate_prompt()

        # Step 3: AI extraction
        raw_data = self.provider.extract(text, schema_prompt, self.model)

        # Step 4: Validate against schema
        is_valid, errors = self.schema.validate(raw_data)

        # Step 5: Build result
        processing_time = time.time() - start_time
        result = ExtractionResult(
            file_path=file_path,
            schema_name=self.schema.name,
            data=raw_data,
            validation_errors=errors,
            processing_time=processing_time,
            char_count=doc_info["char_count"],
            model_used=self.model,
            provider_used=self.provider.__class__.__name__.replace("Provider", "").lower(),
        )

        # Step 6: Save to history
        self._save_to_history(result, doc_info["file_name"])

        return result

    def process_batch(
        self,
        file_paths: List[str],
        output_dir: Optional[str] = None,
        output_format: str = "json",
    ) -> List[ExtractionResult]:
        """Process multiple documents in batch."""
        results = []
        total = len(file_paths)

        for i, file_path in enumerate(file_paths):
            if self.progress_callback:
                self.progress_callback(file_path, i + 1, total)

            try:
                result = self.process_file(file_path)
                results.append(result)

                if output_dir:
                    self._save_result(result, output_dir, output_format)
            except Exception as e:
                error_result = ExtractionResult(
                    file_path=file_path,
                    schema_name=self.schema.name,
                    data={},
                    validation_errors=[str(e)],
                    processing_time=0,
                    char_count=0,
                    model_used=self.model,
                    provider_used="error",
                )
                results.append(error_result)

        return results

    def process_directory(
        self,
        directory: str,
        extensions: Optional[List[str]] = None,
        recursive: bool = False,
        output_dir: Optional[str] = None,
        output_format: str = "json",
    ) -> List[ExtractionResult]:
        """Process all documents in a directory."""
        extensions = extensions or DocumentExtractor.list_supported_formats()
        dir_path = Path(directory)

        if recursive:
            files = [
                str(f) for f in dir_path.rglob("*")
                if f.suffix.lower() in extensions and f.is_file()
            ]
        else:
            files = [
                str(f) for f in dir_path.iterdir()
                if f.suffix.lower() in extensions and f.is_file()
            ]

        files.sort()
        return self.process_batch(files, output_dir, output_format)

    def _save_to_history(self, result: ExtractionResult, file_name: str):
        """Save extraction result to history database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO extractions (
                file_path, file_name, schema_name, data, validation_errors,
                is_valid, processing_time, char_count, model_used, provider_used, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.file_path,
            file_name,
            result.schema_name,
            json.dumps(result.data, ensure_ascii=False),
            json.dumps(result.validation_errors, ensure_ascii=False),
            1 if result.is_valid else 0,
            result.processing_time,
            result.char_count,
            result.model_used,
            result.provider_used,
            result.timestamp,
        ))
        conn.commit()
        conn.close()

    def _save_result(self, result: ExtractionResult, output_dir: str, format: str):
        """Save result to output directory."""
        os.makedirs(output_dir, exist_ok=True)
        base_name = Path(result.file_path).stem

        if format == "json":
            output_path = os.path.join(output_dir, f"{base_name}.json")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result.to_json())
        elif format == "csv":
            output_path = os.path.join(output_dir, f"{base_name}.csv")
            flat_data = result._flatten_dict(result.data)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(",".join(f'"{k}"' for k in flat_data.keys()) + "\n")
                f.write(",".join(f'"{str(v).replace(chr(34), chr(34)+chr(34))}"' for v in flat_data.values()) + "\n")

    def get_history(
        self,
        schema_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Get extraction history from database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        if schema_name:
            cursor = conn.execute(
                "SELECT * FROM extractions WHERE schema_name = ? ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                (schema_name, limit, offset),
            )
        else:
            cursor = conn.execute(
                "SELECT * FROM extractions ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                (limit, offset),
            )

        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()

        for row in rows:
            row["data"] = json.loads(row["data"])
            row["validation_errors"] = json.loads(row["validation_errors"])
            row["is_valid"] = bool(row["is_valid"])
        return rows

    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT
                COUNT(*) as total_extractions,
                SUM(CASE WHEN is_valid = 1 THEN 1 ELSE 0 END) as valid_extractions,
                AVG(processing_time) as avg_processing_time,
                SUM(char_count) as total_chars_processed
            FROM extractions
        """)
        row = cursor.fetchone()
        conn.close()

        total = row[0] or 0
        valid = row[1] or 0
        return {
            "total_extractions": total,
            "valid_extractions": valid,
            "success_rate": round(valid / total * 100, 1) if total > 0 else 0,
            "avg_processing_time": round(row[2] or 0, 2),
            "total_chars_processed": row[3] or 0,
        }

    def export_results(
        self,
        output_path: str,
        schema_name: Optional[str] = None,
        format: str = "json",
    ):
        """Export all results to a file."""
        history = self.get_history(schema_name=schema_name, limit=10000)

        if format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        elif format == "csv":
            if not history:
                return
            # Flatten all data
            all_keys = set()
            for item in history:
                flat = self._flatten_nested(item["data"])
                all_keys.update(flat.keys())
            all_keys = sorted(all_keys)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(",".join(f'"{k}"' for k in ["file_path", "timestamp", "is_valid"] + all_keys) + "\n")
                for item in history:
                    flat = self._flatten_nested(item["data"])
                    row = [item["file_path"], item["timestamp"], str(item["is_valid"])]
                    for key in all_keys:
                        val = flat.get(key, "")
                        escaped = str(val).replace('"', '""')
                        row.append(f'"{escaped}"')
                    f.write(",".join(row) + "\n")

    def _flatten_nested(self, d: Dict, parent_key: str = "") -> Dict[str, str]:
        """Flatten nested dictionary for CSV export."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_nested(v, new_key).items())
            elif isinstance(v, list):
                items.append((new_key, json.dumps(v, ensure_ascii=False)))
            else:
                items.append((new_key, str(v) if v is not None else ""))
        return dict(items)

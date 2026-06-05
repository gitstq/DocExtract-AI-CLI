"""
Terminal UI Module
Provides an interactive terminal interface for document extraction.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional

from .extractor import DocumentExtractor
from .providers import ProviderRegistry
from .schema import Schema, SchemaTemplates
from .pipeline import ExtractionPipeline


class TUIApp:
    """Terminal User Interface for DocExtract."""

    def __init__(self):
        self.width = self._get_terminal_width()
        self.current_provider = None
        self.current_schema = None
        self.current_model = "default"

    def _get_terminal_width(self) -> int:
        """Get terminal width."""
        try:
            return os.get_terminal_size().columns
        except OSError:
            return 80

    def _print_header(self, title: str):
        """Print a formatted header."""
        print()
        print("=" * self.width)
        print(f"  {title}")
        print("=" * self.width)

    def _print_success(self, message: str):
        """Print success message."""
        print(f"  ✓ {message}")

    def _print_error(self, message: str):
        """Print error message."""
        print(f"  ✗ {message}")

    def _print_info(self, message: str):
        """Print info message."""
        print(f"  ℹ {message}")

    def _input(self, prompt: str) -> str:
        """Get user input."""
        return input(f"  > {prompt}: ").strip()

    def run(self):
        """Run the interactive TUI."""
        self._print_header("🦞 DocExtract-AI-CLI v1.0.0")
        print("  AI-Powered Document Structured Extraction Engine")
        print("  轻量级终端AI智能文档结构化提取引擎")
        print()

        while True:
            self._show_menu()
            choice = self._input("Select option")

            if choice == "1":
                self._setup_provider()
            elif choice == "2":
                self._select_schema()
            elif choice == "3":
                self._extract_single()
            elif choice == "4":
                self._extract_batch()
            elif choice == "5":
                self._view_history()
            elif choice == "6":
                self._view_stats()
            elif choice == "7":
                self._test_provider()
            elif choice == "0":
                print("\n  Goodbye! 👋\n")
                break
            else:
                self._print_error("Invalid option. Please try again.")

    def _show_menu(self):
        """Show main menu."""
        provider_status = f"✓ {self.current_provider.__class__.__name__.replace('Provider', '')}" if self.current_provider else "✗ Not configured"
        schema_status = f"✓ {self.current_schema.name}" if self.current_schema else "✗ Not selected"

        print()
        print("  ── Main Menu ──")
        print(f"  Provider: {provider_status} | Schema: {schema_status}")
        print()
        print("  [1] Configure AI Provider")
        print("  [2] Select Extraction Schema")
        print("  [3] Extract Single Document")
        print("  [4] Extract Batch (Directory)")
        print("  [5] View Extraction History")
        print("  [6] View Statistics")
        print("  [7] Test Provider Connection")
        print("  [0] Exit")
        print()

    def _setup_provider(self):
        """Configure AI provider."""
        self._print_header("Configure AI Provider")
        print()
        print("  Available providers:")
        for i, name in enumerate(ProviderRegistry.list_providers(), 1):
            print(f"    [{i}] {name.capitalize()}")
        print()

        choice = self._input("Select provider (number or name)")
        providers = ProviderRegistry.list_providers()

        provider_name = None
        if choice.isdigit() and 1 <= int(choice) <= len(providers):
            provider_name = providers[int(choice) - 1]
        elif choice.lower() in providers:
            provider_name = choice.lower()
        else:
            self._print_error("Invalid provider selection")
            return

        # Get provider-specific configuration
        kwargs = {}
        if provider_name == "openai":
            api_key = self._input("Enter OpenAI API Key")
            base_url = self._input("Base URL (optional, press Enter for default)")
            kwargs["api_key"] = api_key
            if base_url:
                kwargs["base_url"] = base_url
            self.current_model = self._input("Model (default: gpt-4o-mini)") or "gpt-4o-mini"
        elif provider_name == "ollama":
            base_url = self._input("Ollama URL (default: http://localhost:11434)")
            if base_url:
                kwargs["base_url"] = base_url
            self.current_model = self._input("Model (default: llama3.2)") or "llama3.2"
        elif provider_name == "gemini":
            api_key = self._input("Enter Gemini API Key")
            kwargs["api_key"] = api_key
            self.current_model = self._input("Model (default: gemini-1.5-flash)") or "gemini-1.5-flash"

        try:
            self.current_provider = ProviderRegistry.create(provider_name, **kwargs)
            self._print_success(f"Provider '{provider_name}' configured successfully")
        except Exception as e:
            self._print_error(f"Failed to configure provider: {str(e)}")

    def _select_schema(self):
        """Select extraction schema."""
        self._print_header("Select Extraction Schema")
        print()
        print("  [1] Invoice - Extract invoice details")
        print("  [2] Resume/CV - Extract resume information")
        print("  [3] Receipt - Extract purchase receipt data")
        print("  [4] Business Card - Extract contact information")
        print("  [5] Contract - Extract legal contract terms")
        print("  [6] Custom - Load from JSON file")
        print()

        choice = self._input("Select schema")
        templates = {
            "1": SchemaTemplates.invoice,
            "2": SchemaTemplates.resume,
            "3": SchemaTemplates.receipt,
            "4": SchemaTemplates.business_card,
            "5": SchemaTemplates.contract,
        }

        if choice in templates:
            self.current_schema = templates[choice]()
            self._print_success(f"Schema '{self.current_schema.name}' selected")
        elif choice == "6":
            file_path = self._input("Path to schema JSON file")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.current_schema = Schema.from_json(f.read())
                self._print_success(f"Custom schema '{self.current_schema.name}' loaded")
            except Exception as e:
                self._print_error(f"Failed to load schema: {str(e)}")
        else:
            self._print_error("Invalid selection")

    def _extract_single(self):
        """Extract from a single document."""
        if not self._check_ready():
            return

        self._print_header("Extract Single Document")
        file_path = self._input("Enter document path")

        if not os.path.exists(file_path):
            self._print_error("File not found")
            return

        try:
            print(f"\n  📄 Processing: {file_path}")
            print(f"  📋 Schema: {self.current_schema.name}")
            print(f"  🤖 Model: {self.current_model}")
            print("  ⏳ Extracting...")

            pipeline = ExtractionPipeline(
                provider=self.current_provider,
                schema=self.current_schema,
                model=self.current_model,
            )
            result = pipeline.process_file(file_path)

            print()
            self._print_success(f"Extraction complete in {result.processing_time:.2f}s")

            if result.is_valid:
                self._print_success("Validation passed ✓")
            else:
                self._print_error(f"Validation failed: {', '.join(result.validation_errors)}")

            print()
            print("  ── Extracted Data ──")
            print(json.dumps(result.data, indent=4, ensure_ascii=False))

            # Ask to save
            save = self._input("Save result to file? (y/n)")
            if save.lower() == "y":
                output_path = self._input("Output file path")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(result.to_json())
                self._print_success(f"Result saved to {output_path}")

        except Exception as e:
            self._print_error(f"Extraction failed: {str(e)}")

    def _extract_batch(self):
        """Extract from multiple documents in a directory."""
        if not self._check_ready():
            return

        self._print_header("Extract Batch (Directory)")
        directory = self._input("Enter directory path")

        if not os.path.isdir(directory):
            self._print_error("Directory not found")
            return

        recursive = self._input("Include subdirectories? (y/n)").lower() == "y"
        output_dir = self._input("Output directory (optional)")
        output_format = self._input("Output format (json/csv, default: json)") or "json"

        try:
            print(f"\n  📁 Processing directory: {directory}")
            print(f"  📋 Schema: {self.current_schema.name}")
            print(f"  🤖 Model: {self.current_model}")
            print("  ⏳ Scanning files...")

            pipeline = ExtractionPipeline(
                provider=self.current_provider,
                schema=self.current_schema,
                model=self.current_model,
            )

            def progress(file_path: str, current: int, total: int):
                print(f"  [{current}/{total}] Processing: {os.path.basename(file_path)}")

            results = pipeline.process_directory(
                directory=directory,
                recursive=recursive,
                output_dir=output_dir or None,
                output_format=output_format,
            )

            valid_count = sum(1 for r in results if r.is_valid)
            print()
            self._print_success(f"Batch complete: {valid_count}/{len(results)} successful")

            if output_dir:
                self._print_success(f"Results saved to: {output_dir}")

        except Exception as e:
            self._print_error(f"Batch extraction failed: {str(e)}")

    def _view_history(self):
        """View extraction history."""
        self._print_header("Extraction History")

        try:
            pipeline = ExtractionPipeline(
                provider=self.current_provider or ProviderRegistry.create("ollama"),
                schema=self.current_schema or SchemaTemplates.invoice(),
            )
            history = pipeline.get_history(limit=20)

            if not history:
                self._print_info("No extraction history found")
                return

            print()
            print(f"  {'Time':<20} {'File':<30} {'Schema':<15} {'Status':<10} {'Duration':<10}")
            print("  " + "-" * 90)
            for item in history:
                time_str = item["timestamp"][:19].replace("T", " ")
                file_name = os.path.basename(item["file_path"])[:28]
                schema = item["schema_name"][:13]
                status = "✓ Valid" if item["is_valid"] else "✗ Invalid"
                duration = f"{item['processing_time']:.1f}s" if item["processing_time"] else "N/A"
                print(f"  {time_str:<20} {file_name:<30} {schema:<15} {status:<10} {duration:<10}")

        except Exception as e:
            self._print_error(f"Failed to load history: {str(e)}")

    def _view_stats(self):
        """View pipeline statistics."""
        self._print_header("Pipeline Statistics")

        try:
            pipeline = ExtractionPipeline(
                provider=self.current_provider or ProviderRegistry.create("ollama"),
                schema=self.current_schema or SchemaTemplates.invoice(),
            )
            stats = pipeline.get_stats()

            print()
            print(f"  Total Extractions:    {stats['total_extractions']}")
            print(f"  Valid Extractions:    {stats['valid_extractions']}")
            print(f"  Success Rate:         {stats['success_rate']}%")
            print(f"  Avg Processing Time:  {stats['avg_processing_time']}s")
            print(f"  Total Chars Processed: {stats['total_chars_processed']:,}")

        except Exception as e:
            self._print_error(f"Failed to load stats: {str(e)}")

    def _test_provider(self):
        """Test provider connection."""
        if not self.current_provider:
            self._print_error("No provider configured")
            return

        self._print_header("Test Provider Connection")
        print("  Testing connection...")

        success, message = self.current_provider.test_connection()
        if success:
            self._print_success(message)
        else:
            self._print_error(message)

    def _check_ready(self) -> bool:
        """Check if provider and schema are configured."""
        if not self.current_provider:
            self._print_error("Please configure an AI provider first (Menu option 1)")
            return False
        if not self.current_schema:
            self._print_error("Please select an extraction schema first (Menu option 2)")
            return False
        return True

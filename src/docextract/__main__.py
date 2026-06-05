"""
DocExtract-AI-CLI Entry Point
Command-line interface for document structured extraction.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

from . import __version__
from .extractor import DocumentExtractor
from .providers import ProviderRegistry
from .schema import Schema, SchemaTemplates
from .pipeline import ExtractionPipeline
from .tui import TUIApp


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="docextract",
        description="🦞 DocExtract-AI-CLI - AI-Powered Document Structured Extraction Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive TUI mode
  docextract

  # Extract invoice from PDF
  docextract extract invoice.pdf --provider openai --api-key $OPENAI_KEY --schema invoice

  # Extract resume with Ollama (local AI)
  docextract extract resume.pdf --provider ollama --schema resume --model llama3.2

  # Batch extract all PDFs in directory
  docextract batch ./invoices/ --provider openai --api-key $OPENAI_KEY --schema invoice --output ./results/

  # List supported file formats
  docextract formats

  # Test provider connection
  docextract test --provider openai --api-key $OPENAI_KEY
        """,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract data from a single document")
    extract_parser.add_argument("file", help="Path to document file")
    extract_parser.add_argument("--provider", required=True, choices=ProviderRegistry.list_providers(),
                                help="AI provider to use")
    extract_parser.add_argument("--api-key", help="API key for the provider")
    extract_parser.add_argument("--base-url", help="Custom base URL for the provider")
    extract_parser.add_argument("--model", default="default", help="Model to use")
    extract_parser.add_argument("--schema", required=True,
                                choices=["invoice", "resume", "receipt", "business_card", "contract"],
                                help="Extraction schema")
    extract_parser.add_argument("--schema-file", help="Path to custom schema JSON file")
    extract_parser.add_argument("--output", "-o", help="Output file path")
    extract_parser.add_argument("--format", choices=["json", "csv"], default="json", help="Output format")

    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Batch extract from directory")
    batch_parser.add_argument("directory", help="Directory containing documents")
    batch_parser.add_argument("--provider", required=True, choices=ProviderRegistry.list_providers(),
                              help="AI provider to use")
    batch_parser.add_argument("--api-key", help="API key for the provider")
    batch_parser.add_argument("--base-url", help="Custom base URL for the provider")
    batch_parser.add_argument("--model", default="default", help="Model to use")
    batch_parser.add_argument("--schema", required=True,
                              choices=["invoice", "resume", "receipt", "business_card", "contract"],
                              help="Extraction schema")
    batch_parser.add_argument("--schema-file", help="Path to custom schema JSON file")
    batch_parser.add_argument("--output", "-o", required=True, help="Output directory")
    batch_parser.add_argument("--format", choices=["json", "csv"], default="json", help="Output format")
    batch_parser.add_argument("--recursive", "-r", action="store_true", help="Include subdirectories")
    batch_parser.add_argument("--extensions", help="Comma-separated file extensions (default: all supported)")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test provider connection")
    test_parser.add_argument("--provider", required=True, choices=ProviderRegistry.list_providers(),
                             help="AI provider to test")
    test_parser.add_argument("--api-key", help="API key for the provider")
    test_parser.add_argument("--base-url", help="Custom base URL for the provider")

    # Formats command
    subparsers.add_parser("formats", help="List supported file formats")

    # History command
    history_parser = subparsers.add_parser("history", help="View extraction history")
    history_parser.add_argument("--limit", type=int, default=20, help="Number of records to show")
    history_parser.add_argument("--schema", help="Filter by schema name")
    history_parser.add_argument("--export", help="Export to file")

    # Stats command
    subparsers.add_parser("stats", help="View pipeline statistics")

    # Schema command
    schema_parser = subparsers.add_parser("schema", help="Schema management")
    schema_parser.add_argument("--list", action="store_true", help="List built-in schemas")
    schema_parser.add_argument("--show", choices=["invoice", "resume", "receipt", "business_card", "contract"],
                               help="Show schema details")
    schema_parser.add_argument("--export", help="Export schema to file")

    return parser


def get_schema(schema_name: str, schema_file: Optional[str] = None) -> Schema:
    """Get schema by name or from file."""
    if schema_file:
        with open(schema_file, "r", encoding="utf-8") as f:
            return Schema.from_json(f.read())

    templates = {
        "invoice": SchemaTemplates.invoice,
        "resume": SchemaTemplates.resume,
        "receipt": SchemaTemplates.receipt,
        "business_card": SchemaTemplates.business_card,
        "contract": SchemaTemplates.contract,
    }
    return templates[schema_name]()


def create_provider(args) -> any:
    """Create AI provider from arguments."""
    kwargs = {}
    if args.api_key:
        kwargs["api_key"] = args.api_key
    if hasattr(args, "base_url") and args.base_url:
        kwargs["base_url"] = args.base_url
    return ProviderRegistry.create(args.provider, **kwargs)


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # No command - launch TUI
    if not args.command:
        app = TUIApp()
        app.run()
        return

    # Handle commands
    if args.command == "extract":
        provider = create_provider(args)
        schema = get_schema(args.schema, getattr(args, "schema_file", None))
        model = args.model if args.model != "default" else "gpt-4o-mini"

        pipeline = ExtractionPipeline(provider=provider, schema=schema, model=model)
        result = pipeline.process_file(args.file)

        output = result.to_json() if args.format == "json" else result.to_csv_row()

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"✓ Result saved to {args.output}")
        else:
            print(output)

    elif args.command == "batch":
        provider = create_provider(args)
        schema = get_schema(args.schema, getattr(args, "schema_file", None))
        model = args.model if args.model != "default" else "gpt-4o-mini"

        extensions = None
        if hasattr(args, "extensions") and args.extensions:
            extensions = [f".{ext.strip().lstrip('.')}" for ext in args.extensions.split(",")]

        pipeline = ExtractionPipeline(provider=provider, schema=schema, model=model)

        def progress(file_path: str, current: int, total: int):
            print(f"[{current}/{total}] {os.path.basename(file_path)}")

        pipeline.progress_callback = progress
        results = pipeline.process_directory(
            directory=args.directory,
            extensions=extensions,
            recursive=args.recursive,
            output_dir=args.output,
            output_format=args.format,
        )

        valid = sum(1 for r in results if r.is_valid)
        print(f"\n✓ Batch complete: {valid}/{len(results)} successful")
        print(f"  Results saved to: {args.output}")

    elif args.command == "test":
        provider = create_provider(args)
        success, message = provider.test_connection()
        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")
            sys.exit(1)

    elif args.command == "formats":
        print("Supported file formats:")
        for fmt in DocumentExtractor.list_supported_formats():
            print(f"  {fmt}")

    elif args.command == "history":
        # Use default provider for history access
        pipeline = ExtractionPipeline(
            provider=ProviderRegistry.create("ollama"),
            schema=SchemaTemplates.invoice(),
        )
        history = pipeline.get_history(
            schema_name=getattr(args, "schema", None),
            limit=args.limit,
        )

        if args.export:
            pipeline.export_results(args.export, getattr(args, "schema", None))
            print(f"✓ History exported to {args.export}")
        else:
            print(f"{'Time':<20} {'File':<30} {'Schema':<15} {'Status':<10}")
            print("-" * 80)
            for item in history:
                time_str = item["timestamp"][:19].replace("T", " ")
                file_name = os.path.basename(item["file_path"])[:28]
                schema = item["schema_name"][:13]
                status = "✓" if item["is_valid"] else "✗"
                print(f"{time_str:<20} {file_name:<30} {schema:<15} {status:<10}")

    elif args.command == "stats":
        pipeline = ExtractionPipeline(
            provider=ProviderRegistry.create("ollama"),
            schema=SchemaTemplates.invoice(),
        )
        stats = pipeline.get_stats()
        print(f"Total Extractions:     {stats['total_extractions']}")
        print(f"Valid Extractions:     {stats['valid_extractions']}")
        print(f"Success Rate:          {stats['success_rate']}%")
        print(f"Avg Processing Time:   {stats['avg_processing_time']}s")
        print(f"Total Chars Processed: {stats['total_chars_processed']:,}")

    elif args.command == "schema":
        if args.list:
            print("Built-in schemas:")
            for name in ["invoice", "resume", "receipt", "business_card", "contract"]:
                print(f"  {name}")
        elif args.show:
            schema = get_schema(args.show)
            print(schema.to_json())
            if args.export:
                with open(args.export, "w", encoding="utf-8") as f:
                    f.write(schema.to_json())
                print(f"✓ Schema exported to {args.export}")


if __name__ == "__main__":
    main()

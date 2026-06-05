.PHONY: help install install-dev test test-cov lint format clean build dist check upload docs

PYTHON := python3
PIP := $(PYTHON) -m pip

help:
	@echo "DocExtract-AI-CLI - Available commands:"
	@echo ""
	@echo "  install      - Install package"
	@echo "  install-dev  - Install with development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linters (flake8, mypy)"
	@echo "  format       - Format code with black"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build distribution packages"
	@echo "  dist         - Create source and wheel distributions"
	@echo "  check        - Run all checks (lint + test)"
	@echo "  run          - Run interactive TUI"
	@echo ""

install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[dev]"

test:
	$(PYTHON) -m pytest tests/ -v

test-cov:
	$(PYTHON) -m pytest tests/ -v --cov=docextract --cov-report=html --cov-report=term

lint:
	$(PYTHON) -m flake8 src/docextract tests
	$(PYTHON) -m mypy src/docextract

format:
	$(PYTHON) -m black src/docextract tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

build: clean
	$(PYTHON) -m build

dist: build

check: lint test

run:
	$(PYTHON) -m docextract

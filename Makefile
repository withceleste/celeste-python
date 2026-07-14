.PHONY: help sync lint lint-fix format typecheck test integration-test integration-retest security ci clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make sync       - Update and sync all dependencies with all extras"
	@echo "  make lint       - Run Ruff linting"
	@echo "  make format     - Apply Ruff formatting"
	@echo "  make typecheck  - Run mypy type checking"
	@echo "  make test       - Run all tests (core + packages) with coverage"
	@echo "  make integration-test    - Run all integration tests"
	@echo "  make integration-retest  - Rerun only last-failed integration tests"
	@echo "  make security   - Run Bandit security scan"
	@echo "  make ci       - Run full CI/CD pipeline"
	@echo "  make clean      - Clean cache directories"

# Complete dependency sync - update lock, sync everything
sync:
	@echo "🔄 Updating dependencies..."
	@uv sync --all-packages --all-extras --upgrade
	@echo "✅ All dependencies synced and updated"

# Linting
lint:
	uv run ruff check src/celeste tests/

# Linting with auto-fix
lint-fix:
	uv run ruff check --fix src/celeste tests/

# Formatting
format:
	uv run ruff format src/celeste tests/

# Type checking (fail fast on any error)
typecheck:
	@uv run mypy -p celeste && uv run mypy tests/

# Testing
test:
	uv run pytest tests/unit_tests --cov=celeste --cov-report=term-missing -v

# Integration testing (requires API keys and/or ADC credentials)
# Runs tests from tests/integration_tests/
integration-test:
	uv run pytest tests/integration_tests/ -v --dist=worksteal -n auto

# Rerun only last-failed integration tests (without xdist — --lf is incompatible with -n)
integration-retest:
	uv run pytest tests/integration_tests/ -v --lf

# Security scanning (config reads from pyproject.toml)
security:
	uv run bandit -c pyproject.toml -r src/ -f screen

# Full CI/CD pipeline - what GitHub Actions will run
ci:
	@echo "🔍 Running Full CI/CD Pipeline..."
	@echo "================================="
	@echo "1️⃣  Ruff Linting (with auto-fix)..."
	@$(MAKE) lint-fix || (echo "❌ Linting failed" && exit 1)
	@echo "✅ Linting passed"
	@echo ""
	@echo "2️⃣  Ruff Formatting..."
	@$(MAKE) format || (echo "❌ Formatting failed" && exit 1)
	@echo "✅ Formatting applied"
	@echo ""
	@echo "3️⃣  MyPy Type Checking (parallel)..."
	@$(MAKE) typecheck || (echo "❌ Type checking failed" && exit 1)
	@echo "✅ Type checking passed"
	@echo ""
	@echo "4️⃣  Bandit Security Scan..."
	@$(MAKE) security || (echo "❌ Security scan failed" && exit 1)
	@echo "✅ Security scan passed"
	@echo ""
	@echo "5️⃣  Running Tests with Coverage..."
	@$(MAKE) test || (echo "❌ Tests failed" && exit 1)
	@echo ""
	@echo "================================="
	@echo "🎉 All CI/CD checks passed! Ready to commit."

# Clean cache directories and artifacts
clean:
	@echo "🧹 Cleaning cache directories and artifacts..."
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov/
	rm -rf __pycache__ build/ dist/ *.egg-info .eggs/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "✅ Clean complete"

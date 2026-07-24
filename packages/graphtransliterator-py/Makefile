# Define the browser command for opening docs (fallback to open on macOS / xdg-open on Linux)
BROWSER := $(shell which open 2>/dev/null || which xdg-open 2>/dev/null || echo "echo Cannot open")

.DEFAULT_GOAL := help

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install the poetry environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment and installing dependencies"
	poetry install
	poetry run pre-commit install
	@echo "✅ Setup complete! Run 'poetry shell' to activate your environment."

.PHONY: check
check: ## Run all strict Python code quality and validation checks
	@echo "🚀 Checking Poetry lock file consistency..."
	poetry check --lock

	@echo "\n🚀 Running pre-commit hooks across all files..."
	poetry run pre-commit run --all-files

	@echo "\n🚀 Scanning for obsolete or untracked package dependencies..."
	poetry run deptry src --exclude .venv

fix: ## Automatically fix lint errors and format code
	@echo "🚀 Automatically fixing lint rules with Ruff..."
	poetry run ruff check --fix .

	@echo "\n🚀 Formatting code with Ruff..."
	poetry run ruff format .


.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	poetry run pytest --cov --cov-config=pyproject.toml --cov-report=xml

.PHONY: coverage
coverage: ## Check code coverage quickly and open HTML report
	@echo "🚀 Running tests with coverage"
	poetry run pytest --cov --cov-config=pyproject.toml --cov-report=term-missing --cov-report=html
	$(BROWSER) htmlcov/index.html

.PHONY: build
build: clean-build ## Build wheel file using poetry
	@echo "🚀 Creating wheel file"
	poetry build

.PHONY: clean-build
clean-build: ## Clean build artifacts
	rm -rf dist

.PHONY: clean-docs
clean-docs: ## Clean documentation build artifacts
	rm -rf docs/_build

.PHONY: clean
clean: clean-build clean-docs ## Clean build, docs, and test artifacts locally
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -f coverage.xml
	rm -rf htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete

	@echo "✨ Inner directory is clean!"

.PHONY: publish
publish: ## Publish a release to PyPI
	@echo "🚀 Publishing: Dry run."
	poetry config pypi-token.pypi $(PYPI_TOKEN)
	poetry publish --dry-run
	@echo "🚀 Publishing."
	poetry publish

.PHONY: build-and-publish
build-and-publish: build publish ## Build and publish

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	poetry run sphinx-build -b html docs docs/_build/html

.PHONY: docs
docs:
	rm -rf docs/_build
	# 1. Automatically regenerate TypeScript Markdown docs using the isolated sandbox
	npx --prefix $$(mktemp -d) --package=typescript@5.7.3 --package=typedoc --package=typedoc-plugin-markdown \
		typedoc \
		--plugin typedoc-plugin-markdown \
		--entryPoints ../graphtransliterator-ts/src/index.ts \
		--out docs/typescript_api \
		--readme none \
		--skipErrorChecking true
	# 2. Build the Sphinx documentation
	poetry run sphinx-build -b html docs docs/_build/html
	$(BROWSER) docs/_build/html/index.html

.PHONY: servedocs
servedocs: docs ## Compile the docs and watch for changes live
	poetry run watchmedo shell-command -p '*.py;*.rst;*.ipynb;*.md' -c 'poetry run sphinx-build -b html docs docs/_build/html' -R -D .

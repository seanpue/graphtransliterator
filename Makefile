# Define the browser command for opening docs (fallback to open on macOS / xdg-open on Linux)
BROWSER := $(shell which open 2>/dev/null || check which xdg-open 2>/dev/null || echo "echo Cannot open")

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
check: ## Run code quality tools
	@echo "🚀 Checking Poetry lock file consistency: Running poetry check"
	poetry check --lock
	@echo "🚀 Linting code: Running pre-commit"
	poetry run pre-commit run -a
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	poetry run deptry .

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
	poetry run $(MAKE) -C docs html

.PHONY: docs
docs: ## Build and serve the documentation
	poetry run $(MAKE) -C docs clean
	poetry run $(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

.PHONY: servedocs
servedocs: docs ## Compile the docs watching for changes
	poetry run watchmedo shell-command -p '*.py;*.rst;*ipynb;*md' -c '$(MAKE) -C docs html' -R -D .

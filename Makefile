.PHONY: install
install: ## Install environments for all subpackages
	$(MAKE) -C packages/graphtransliterator-py install
	pnpm install

.PHONY: check
check: check-py check-ts ## Run linting on all subpackages

.PHONY: check-py
check-py: ## Run Python-only checks
	$(MAKE) -C packages/graphtransliterator-py check

.PHONY: check-ts
check-ts: ## Run TS-only checks
	pnpm --filter graphtransliterator lint
	pnpm --filter graphtransliterator test:types

.PHONY: build
build: build-py build-ts ## Build assets for all subpackages

.PHONY: build-py
build-py: ## Build Python distribution packages
	cd packages/graphtransliterator-py && poetry build

.PHONY: build-ts
build-ts: ## Build TypeScript bundle and declaration files
	pnpm --filter graphtransliterator build

.PHONY: test
test: ## Run test suites for all languages
	$(MAKE) -C packages/graphtransliterator-py test
	pnpm --filter graphtransliterator test

.PHONY: clean
clean: ## Delegate cleaning down to the subpackage directory
	$(MAKE) -C packages/graphtransliterator-py clean
	rm -rf packages/graphtransliterator-ts/dist
	@echo "🧹 Cleaning project artifacts..."
	rm -rf .tox/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf *.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} +

.PHONY: fix
fix: fix-py fix-ts ## Automatically fix format/lint errors across the entire monorepo

.PHONY: fix-py
fix-py: ## Automatically fix and format Python code
	cd packages/graphtransliterator-py && poetry run ruff check --fix . && poetry run ruff format .

.PHONY: fix-ts
fix-ts: ## Automatically fix and format TypeScript code
	pnpm --filter graphtransliterator lint:fix

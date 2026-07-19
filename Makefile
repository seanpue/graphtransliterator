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

.PHONY: test
test: ## Run test suites for all languages
	$(MAKE) -C packages/graphtransliterator-py test
	pnpm --filter graphtransliterator test

.PHONY: clean
clean: ## Delegate cleaning down to the subpackage directory
	$(MAKE) -C packages/graphtransliterator-py clean
	rm -rf packages/graphtransliterator-ts/dist

.PHONY: fix
fix: fix-py fix-ts ## Automatically fix format/lint errors across the entire monorepo

.PHONY: fix-py
fix-py: ## Automatically fix and format Python code
	cd packages/graphtransliterator-py && poetry run ruff check --fix . && poetry run ruff format .

.PHONY: fix-ts
fix-ts: ## Automatically fix and format TypeScript code
	pnpm --filter graphtransliterator lint:fix

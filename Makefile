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
	pnpm --filter graphtransliterator run lint

.PHONY: test
test: ## Run test suites for all languages
	$(MAKE) -C packages/graphtransliterator-py test
	pnpm --filter graphtransliterator test

.PHONY: clean
clean: ## Delegate cleaning down to the subpackage directory
	$(MAKE) -C packages/graphtransliterator-py clean
	rm -rf packages/graphtransliterator-ts/dist

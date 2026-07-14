.PHONY: install
install: ## Install environments for all subpackages
	$(MAKE) -C packages/graphtransliterator-py install
	pnpm install

.PHONY: check
check: ## Run linting on all subpackages
	$(MAKE) -C packages/graphtransliterator-py check
	# If you add a lint script to your TS package later, uncomment below:
	# pnpm --filter graphtransliterator-ts run lint

.PHONY: test
test: ## Run test suites for all languages
	$(MAKE) -C packages/graphtransliterator-py test
	pnpm --filter graphtransliterator-ts test

.PHONY: clean
clean: ## Delegate cleaning down to the subpackage directory
	$(MAKE) -C packages/graphtransliterator-py clean
	rm -rf packages/graphtransliterator-ts/dist
.PHONY: install
install: ## Install environments for all subpackages
	$(MAKE) -C packages/graphtransliterator-py install
	# $(MAKE) -C packages/graphtransliterator-ts install

.PHONY: check
check: ## Run linting on all subpackages
	$(MAKE) -C packages/graphtransliterator-py check
	# $(MAKE) -C packages/graphtransliterator-ts check

.PHONY: test
test: ## Run test suites for all languages
	$(MAKE) -C packages/graphtransliterator-py test
	# $(MAKE) -C packages/graphtransliterator-ts test

.PHONY: clean
clean: ## Delegate cleaning down to the subpackage directory
	$(MAKE) -C packages/graphtransliterator-py clean

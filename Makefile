.PHONY: clean-build
clean-build: ## Remove python build artifacts
	rm -rf packages/graphtransliterator-py/dist
	rm -rf packages/graphtransliterator-py/build

.PHONY: clean-docs
clean-docs: ## Remove documentation build artifacts
	rm -rf packages/graphtransliterator-py/docs/_build

.PHONY: clean
clean: clean-build clean-docs ## Remove all build, test, and lint cache artifacts
	rm -rf packages/graphtransliterator-py/.pytest_cache
	rm -rf packages/graphtransliterator-py/.mypy_cache
	rm -rf packages/graphtransliterator-py/.coverage
	rm -rf packages/graphtransliterator-py/htmlcov
	rm -f packages/graphtransliterator-py/coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	@echo "✨ Workspace is completely clean!"
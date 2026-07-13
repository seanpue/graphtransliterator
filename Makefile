.PHONY: clean

clean:
	@echo "Cleaning up build artifacts, caches, and docs..."
	rm -rf .tox/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -f coverage.xml
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf packages/graphtransliterator-py/docs/_build/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	@echo "✨ Everything is fresh and clean!"

# Graph Transliterator Workspace

This is a monorepo workspace containing both the Python and TypeScript implementations of the Graph Transliterator framework.

## Repository Structure

- packages/graphtransliterator-py/ - The Python implementation, test suites, and unified Sphinx documentation.
- packages/graphtransliterator-ts/ - The TypeScript/NPM implementation built with tsup and tested via vitest.
- paper/ - Source files for the academic publication regarding this framework.

## Development Setup

This workspace relies on Python Poetry for the Python ecosystem and pnpm for managing the TypeScript project and monorepo topology.

### 1. Python Environment Setup

Navigate to the Python package directory to lock down your local virtual environment:

cd packages/graphtransliterator-py
poetry install

### 2. JavaScript/TypeScript Environment Setup

Install the monorepo-wide JavaScript dependencies from the workspace root:

pnpm install

## Available Root Tasks

You can invoke package-specific tasks using our workflow tooling from the root directory:

### TypeScript Targets

- Build TS Assets: pnpm --filter graphtransliterator-ts build
- Run TS Test Suites: pnpm --filter graphtransliterator-ts test

### Python Targets

- Run Python Test Suites: cd packages/graphtransliterator-py && poetry run pytest
- Run Linting & Sanity Checks: cd packages/graphtransliterator-py && make check

### Documentation Pipeline

The documentation build process automatically sandboxes TypeDoc to parse the TypeScript codebase into Markdown before compiling the global HTML site with Sphinx:

cd packages/graphtransliterator-py && make docs

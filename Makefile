# Terminal colors
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)
BLUE   := $(shell tput -Txterm setaf 4)

# Project settings
PYTHON_VERSION := 3.12
VENV_NAME := .venv
PYTHON := $(VENV_NAME)/bin/python
PROJECT_NAME := genai-ecommerce

# Test settings
TEST_PATH := tests/
PYTEST_ARGS ?= -v
COVERAGE_THRESHOLD := 90

RUN_ARGS ?= --help

help: ## Show this help message
	@echo ''
	@echo '${YELLOW}Development Guide${RESET}'
	@echo ''
	@echo '${YELLOW}Installation Options:${RESET}'
	@echo '  Core:       ${GREEN}make install-core${RESET}     - Install core package'
	@echo '  Web:        ${GREEN}make install-web${RESET}      - Install web package'
	@echo '  ML:         ${GREEN}make install-ml${RESET}       - Install ML package'
	@echo '  All:        ${GREEN}make install-all${RESET}      - Install all packages'
	@echo '  Development:${GREEN}make install-dev${RESET}      - Development tools'
	@echo ''
	@echo '${YELLOW}Development Workflow:${RESET}'
	@echo '  1. Setup:     ${GREEN}make setup${RESET}         - Full development environment'
	@echo '  2. Source:    ${GREEN}source setup.sh${RESET}    - Activate environment'
	@echo '  3. Install:   ${GREEN}make install-all${RESET}   - Install packages'
	@echo ''
	@echo '${YELLOW}Available Targets:${RESET}'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  ${YELLOW}%-15s${GREEN}%s${RESET}\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ''

# Development environment targets
.PHONY: env
env: ## Create virtual environment using uv
	@echo "${BLUE}Creating virtual environment...${RESET}"
	uv venv --python $(PYTHON_VERSION)
	@echo "${GREEN}Virtual environment created. Activate it with:${RESET}"
	@echo "source $(VENV_NAME)/bin/activate"

.PHONY: install-core
install-core: ## Install core package
	@echo "${BLUE}Installing core package...${RESET}"
	cp pyproject.core.toml pyproject.toml
	uv pip install -e .
	rm pyproject.toml

.PHONY: install-web
install-web: ## Install web package
	@echo "${BLUE}Installing web package...${RESET}"
	cp pyproject.web.toml pyproject.toml
	uv pip install -e .
	rm pyproject.toml

.PHONY: install-ml
install-ml: ## Install ML package
	@echo "${BLUE}Installing ML package...${RESET}"
	cp pyproject.ml.toml pyproject.toml
	uv pip install -e .
	rm pyproject.toml

.PHONY: install-all
install-all: install-core install-web install-ml ## Install all packages
	cp pyproject.main.toml pyproject.toml
	uv pip install -e .
	@echo "${GREEN}All packages installed successfully${RESET}"

.PHONY: install-dev
install-dev: ## Install all packages with development dependencies
	@echo "${BLUE}Installing packages with development tools...${RESET}"
	cp pyproject.core.toml pyproject.toml
	uv pip install -e ".[dev]"
	rm pyproject.toml
	cp pyproject.web.toml pyproject.toml
	uv pip install -e ".[dev]"
	rm pyproject.toml
	cp pyproject.ml.toml pyproject.toml
	uv pip install -e ".[dev]"
	rm pyproject.toml
	cp pyproject.main.toml pyproject.toml
	uv pip install -e ".[dev]"

.PHONY: setup
setup:
	@echo "${BLUE}Creating complete development environment...${RESET}"
	@echo '#!/bin/bash' > setup.sh
	@echo 'uv venv --python $(PYTHON_VERSION)' >> setup.sh
	@echo 'source $(VENV_NAME)/bin/activate' >> setup.sh
	@echo 'cat > pyproject.toml << EOL' >> setup.sh
	@echo '[build-system]' >> setup.sh
	@echo 'requires = ["hatchling"]' >> setup.sh
	@echo 'build-backend = "hatchling.build"' >> setup.sh
	@echo '[project]' >> setup.sh
	@echo 'name = "genai-ecommerce"' >> setup.sh
	@echo 'version = "0.1.0"' >> setup.sh
	@echo 'description = "GenAI E-commerce project with ML-powered recommendations"' >> setup.sh
	@echo 'requires-python = ">=3.12,<3.13"' >> setup.sh
	@echo 'dependencies = [' >> setup.sh
	@echo '    "genai_ecommerce_core @ file://.",' >> setup.sh
	@echo '    "genai_ecommerce_web @ file://.",' >> setup.sh
	@echo '    "genai_ecommerce_ml @ file://.",' >> setup.sh
	@echo ']' >> setup.sh
	@echo '[tool.hatch.metadata]' >> setup.sh
	@echo 'allow-direct-references = true' >> setup.sh
	@echo '[tool.ruff]' >> setup.sh
	@echo 'line-length = 88' >> setup.sh
	@echo 'target-version = "py312"' >> setup.sh
	@echo '[tool.ruff.lint]' >> setup.sh
	@echo 'select = ["E", "W", "F", "I", "C", "B", "UP", "N", "ANN", "S", "A"]' >> setup.sh
	@echo '[tool.ruff.format]' >> setup.sh
	@echo 'quote-style = "double"' >> setup.sh
	@echo 'indent-style = "space"' >> setup.sh
	@echo 'skip-magic-trailing-comma = false' >> setup.sh
	@echo 'line-ending = "auto"' >> setup.sh
	@echo '[tool.mypy]' >> setup.sh
	@echo 'python_version = "3.12"' >> setup.sh
	@echo 'disallow_untyped_defs = true' >> setup.sh
	@echo 'disallow_incomplete_defs = true' >> setup.sh
	@echo 'check_untyped_defs = true' >> setup.sh
	@echo 'disallow_untyped_decorators = true' >> setup.sh
	@echo 'no_implicit_optional = true' >> setup.sh
	@echo 'warn_redundant_casts = true' >> setup.sh
	@echo 'warn_unused_ignores = true' >> setup.sh
	@echo 'warn_return_any = true' >> setup.sh
	@echo 'strict_optional = true' >> setup.sh
	@echo '[project.optional-dependencies]' >> setup.sh
	@echo 'dev = [' >> setup.sh
	@echo '    "pytest>=7.0.0",' >> setup.sh
	@echo '    "pytest-cov>=4.1.0",' >> setup.sh
	@echo '    "ruff>=0.2.0",' >> setup.sh
	@echo '    "mypy>=1.8.0",' >> setup.sh
	@echo '    "ipykernel>=6.0.0",' >> setup.sh
	@echo ']' >> setup.sh
	@echo 'EOL' >> setup.sh
	@echo 'make install-all' >> setup.sh
	@echo 'rm "$$0"' >> setup.sh
	@chmod +x setup.sh
	@echo "${GREEN}Environment setup script created. To complete setup, run:${RESET}"
	@echo "${YELLOW}source setup.sh${RESET}"

.PHONY: run-web
run-web: ## Run web application
	$(PYTHON) -m genai_ecommerce_web

.PHONY: ingest-data
ingest-data: ## Fetch and store data from AboutYou API
	@echo "Starting data ingestion..."
	$(PYTHON) src/genai_ecommerce_core/data_ingestion.py

.PHONY: update
update: ## Update all dependencies
	@echo "${BLUE}Updating dependencies...${RESET}"
	make install-dev

.PHONY: test
test: install-dev ## Run tests with coverage
	$(PYTHON) -m pytest $(TEST_PATH) $(PYTEST_ARGS) --cov=src --cov-report=term-missing

.PHONY: format
format: install-dev ## Format code with ruff
	@echo "${BLUE}Formatting code...${RESET}"
	$(PYTHON) -m ruff format .
	$(PYTHON) -m isort .

.PHONY: lint
lint: install-dev ## Run linters
	$(PYTHON) -m ruff check src/ tests/ examples/
	$(PYTHON) -m ruff format --check src/ tests/ examples/
	$(PYTHON) -m mypy src/ tests/ examples/

.PHONY: clean
clean: ## Clean build artifacts and cache
	rm -rf build/ dist/ *.egg-info .coverage .mypy_cache .pytest_cache .ruff_cache $(VENV_NAME)
	rm -rf setup.sh pyproject.toml
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: pre-commit
pre-commit: format lint test clean ## Run all checks before committing
	@echo "${GREEN}✓ All checks passed${RESET}"

.PHONY: structure
structure: ## Show project structure
	@echo "${YELLOW}Current Project Structure:${RESET}"
	@echo "${BLUE}"
	@if command -v tree > /dev/null; then \
		tree -a -I '.git|.venv|__pycache__|*.pyc|*.pyo|*.pyd|.pytest_cache|.ruff_cache|.coverage|htmlcov'; \
	else \
		find . -not -path '*/\.*' -not -path '*.pyc' -not -path '*/__pycache__/*' \
			-not -path './.venv/*' -not -path './build/*' -not -path './dist/*' \
			-not -path './*.egg-info/*' \
			| sort | \
			sed -e "s/[^-][^\/]*\// │   /g" -e "s/├── /│── /" -e "s/└── /└── /"; \
	fi
	@echo "${RESET}"

.DEFAULT_GOAL := help
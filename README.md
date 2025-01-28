# 🛍️ GenAI E-commerce

E-commerce exploratory platform with AI-powered recommendations using classic and modern embedding techniques.

## Features

- Product feed ingestion from AboutYou API
- Local caching of products and images
- Classic clustering-based recommendations
- Vector embeddings for similarity search
- Web interface for product browsing and recommendations

## Prerequisites

- Python 3.12
- UV package manager

## Quick Start

```bash
# Setup environment
make setup
source setup.sh

# Run web application
make run-web
```

Visit http://localhost:8000

## Project Structure

```

├── LICENSE
├── Makefile
├── README.md
├── ecommerce.db
├── pyproject.core.toml
├── pyproject.main.toml
├── pyproject.ml.toml
├── pyproject.toml
├── pyproject.web.toml
└── src
    ├── genai_ecommerce_core
    │   ├── __init__.py
    │   ├── client.py
    │   ├── data_ingestion.py
    │   ├── database.py
    │   └── models.py
    ├── genai_ecommerce_ml
    │   ├── __init__.py
    │   ├── base.py
    │   ├── clustering.py
    │   └── embeddings.py
    └── genai_ecommerce_web
        ├── __init__.py
        ├── __main__.py
        ├── app.py
        ├── dependencies.py
        ├── routers
        │   ├── __init__.py
        │   └── api.py
        ├── static
        │   └── .gitkeep
        └── templates
            ├── base.html
            ├── catalog.html
            └── product.html

```

## Development

```bash
# Format code
make format

# Run linters
make lint

# Run tests
make test

# Run all checks
make pre-commit
```
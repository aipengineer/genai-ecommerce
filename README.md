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
src/
├── genai_ecommerce_core/    # Core functionality
│   ├── client.py           # API client
│   ├── database.py         # SQLite models
│   └── models.py          # Pydantic models
├── genai_ecommerce_ml/     # ML components
│   ├── clustering.py      # Classic recommendations
│   └── embeddings.py      # Vector embeddings
└── genai_ecommerce_web/    # Web interface
    ├── app.py            # FastAPI application
    └── templates/        # Jinja2 templates
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
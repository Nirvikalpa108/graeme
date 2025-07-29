#!/bin/bash
set -e  # Exit immediately if a command fails

echo "🚀 Running data load step..."
python3 src/load_to_postgres.py

echo "🧠 Running embedding step..."
python3 src/embed_batch_to_pgvector.py

echo "🧪 Running tests..."
pytest -s tests/

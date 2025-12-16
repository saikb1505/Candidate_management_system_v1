#!/bin/bash
# Migration script for Railway deployment
# Run this to apply database migrations

set -e  # Exit on error

echo "Running database migrations..."

# Check if python3 or python is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "Error: Python not found"
    exit 1
fi

# Run migrations using the Python script
$PYTHON_CMD scripts/run_migrations.py

echo "Migration complete!"

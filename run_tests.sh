#!/bin/bash

# Exit on error
set -e

echo "Installing test dependencies..."
python -m pip install -r requirements-test.txt

echo "Running tests with coverage..."
python -m pytest --cov=src tests/ --cov-report=term-missing

echo "Generating coverage report..."
python -m coverage html

echo "Tests completed successfully!"

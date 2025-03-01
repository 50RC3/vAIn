# Stop on first error
$ErrorActionPreference = "Stop"

try {
    Write-Host "Installing test dependencies..."
    python -m pip install -r requirements-test.txt

    Write-Host "Running tests with coverage..."
    python -m pytest --cov=src tests/ --cov-report=term-missing

    Write-Host "Generating coverage report..."
    python -m coverage html

    Write-Host "Tests completed successfully!" -ForegroundColor Green
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

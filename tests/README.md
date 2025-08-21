# Carbon CLI Test Suite

This directory contains comprehensive unit tests for the Carbon CLI project.

## Test Structure

- `test_carbon_cli.py` - Main test file containing all unit tests
- `test_run.py` - Tests for the main CLI entry point
- `conftest.py` - Test fixtures and configuration
- `pytest.ini` - PyTest configuration

## Test Coverage

### TestConfig
Tests for configuration management functions:
- S3 client creation
- Configuration loading from S3
- Configuration saving to S3
- Error handling for missing configs

### TestAI
Tests for AI/OpenAI integration functions:
- Assistant creation and retrieval
- File upload functionality
- Thread management
- File saving operations
- Error handling

### TestMain
Tests for the main CLI interface:
- Command parsing and routing
- Environment variable validation
- Error handling for invalid commands
- All supported command combinations

### TestIntegration
Integration tests for complete workflows:
- End-to-end issue creation workflow
- Proper interaction between components

## Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_carbon_cli.py -v

# Run specific test class
python -m pytest tests/test_carbon_cli.py::TestConfig -v

# Run with coverage (if coverage package is installed)
python -m pytest --cov=src
```

## Test Dependencies

- pytest
- pytest-mock
- moto (for AWS S3 mocking)

## Mock Strategy

Tests use extensive mocking to isolate units under test:
- AWS S3 operations are mocked using unittest.mock
- OpenAI API calls are mocked
- File system operations are mocked
- Environment variables are patched for each test

This ensures tests run quickly and don't require external dependencies.
# Contra Eris Test Suite

This directory contains tests for the Contra Eris project.

## Structure

- `test_core.py`: Tests for core functionality
- `test_cli.py`: Tests for CLI commands
- `test_data/`: Sample data for testing

## Running Tests

### Run all tests

```bash
python -m unittest discover tests
```

### Run a specific test file

```bash
python -m unittest tests/test_core.py
```

### Run a specific test case

```bash
python -m unittest tests.test_core.TestCore.test_analyze_project
```

## Adding New Tests

1. Create a new test file with the naming convention `test_*.py`
2. Import the module you want to test
3. Create a class that inherits from `unittest.TestCase`
4. Add test methods with names starting with `test_`
5. Run the tests to verify they work

## Test Data

The `test_data` directory contains sample files used for testing. You can add more test files here as needed.

## Continuous Integration

These tests are designed to run in a CI/CD pipeline. Make sure to run the tests before submitting a pull request. 
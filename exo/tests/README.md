# exo Multi-Agent Framework Tests

This directory contains the test suite for the exo Multi-Agent Framework.

## Test Structure

The tests are organized by module, with each test file corresponding to a specific module in the exo framework:

- `test_service_registry.py`: Tests for the service registry module
- `test_onboarding.py`: Tests for the onboarding module
- `test_llm_manager.py`: Tests for the LLM manager module
- `test_base_agent.py`: Tests for the base agent module
- `test_web_server.py`: Tests for the web server module

## Running Tests

To run the tests, use pytest from the root directory of the project:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=exo

# Run a specific test file
pytest exo/tests/test_service_registry.py

# Run a specific test function
pytest exo/tests/test_service_registry.py::test_helper_functions
```

## Test Fixtures

Common test fixtures are defined in `conftest.py`. These fixtures provide mock objects that can be used across multiple test files:

- `mock_onboarding`: A mock onboarding instance
- `mock_llm_manager`: A mock LLM manager instance
- `mock_mcp_manager`: A mock MCP manager instance
- `mock_service_registry`: A mock service registry with common services

## Writing New Tests

When writing new tests, follow these guidelines:

1. Create a new test file for each module you want to test
2. Use the existing fixtures from `conftest.py` when possible
3. Mock external dependencies to isolate the code being tested
4. Test both success and error cases
5. Use descriptive test names that explain what is being tested
6. Add docstrings to test classes and functions

Example:

```python
def test_something():
    """Test that something works correctly."""
    # Arrange
    expected = "expected result"
    
    # Act
    actual = function_under_test()
    
    # Assert
    assert actual == expected
```

## Test Coverage

The goal is to maintain high test coverage for all modules. Use the coverage report to identify areas that need more tests:

```bash
pytest --cov=exo --cov-report=term-missing
```

## Continuous Integration

Tests are automatically run as part of the CI/CD pipeline. Make sure all tests pass before submitting a pull request.

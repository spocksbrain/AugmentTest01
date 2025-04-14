# exo Multi-Agent Framework Test Plan

This document outlines the comprehensive test plan for the exo Multi-Agent Framework. It covers unit tests, integration tests, and system tests to ensure the framework functions correctly.

## Test Categories

### 1. Unit Tests

Unit tests verify that individual components work correctly in isolation.

#### 1.1 Primary Interface Agent (PIA)

- **Test File**: `exo/tests/test_primary_agent.py`
- **Components Tested**:
  - Initialization
  - User input processing
  - Domain detection
  - Direct response generation
  - Domain agent delegation
  - MCP server handling (Brave Search, Filesystem)
  - Path extraction from queries
  - File operations (list, read, delete)

#### 1.2 Message Handling

- **Test File**: `exo/tests/test_message_handling.py`
- **Components Tested**:
  - Message validation
  - Message routing to PIA
  - Error handling
  - Response formatting

#### 1.3 System Prompts

- **Test File**: `exo/tests/test_system_prompts.py`
- **Components Tested**:
  - Prompt retrieval for different agent types
  - Prompt content validation
  - Prompt consistency

### 2. Integration Tests

Integration tests verify that components work correctly together.

#### 2.1 System Integration

- **Test File**: `exo/tests/test_system_integration.py`
- **Components Tested**:
  - System initialization
  - Service registration
  - Domain agent registration
  - Message flow through the system
  - Complex task delegation
  - Domain-specific task delegation
  - MCP server integration

#### 2.2 MCP Integration

- **Test File**: `exo/tests/test_mcp_integration.py`
- **Components Tested**:
  - MCP server manager initialization
  - Server initialization
  - Request sending
  - Service registration
  - PIA integration with MCP servers

### 3. System Tests

System tests verify that the entire system works correctly as a whole.

#### 3.1 End-to-End Tests

- **Manual Testing**: These tests involve running the system and interacting with it through the UI.
- **Components Tested**:
  - System startup
  - UI interaction
  - Message processing
  - Response generation
  - MCP server integration
  - Domain agent delegation

## Test Execution

### Running All Tests

To run all tests, use the provided test runner script:

```bash
./run_tests.py
```

### Running Specific Tests

To run specific tests, specify the test file or directory:

```bash
./run_tests.py exo/tests/test_primary_agent.py
```

### Generating Coverage Reports

To generate coverage reports, use the `--coverage` option:

```bash
./run_tests.py --coverage
```

This will generate an HTML coverage report in the `htmlcov` directory.

## Test Dependencies

The tests use the following dependencies:

- **pytest**: For test execution
- **pytest-cov**: For coverage reporting
- **unittest.mock**: For mocking dependencies

## Test Fixtures

Common test fixtures are defined in `exo/tests/conftest.py`:

- **mock_onboarding**: Mock onboarding service
- **mock_llm_manager**: Mock LLM manager
- **mock_mcp_manager**: Mock MCP manager
- **mock_primary_agent**: Mock primary interface agent
- **mock_cnc_agent**: Mock command and control agent
- **mock_system**: Mock system instance
- **mock_web_server**: Mock web server
- **mock_service_registry**: Mock service registry with all services registered

## Test Maintenance

When adding new features or modifying existing ones, follow these guidelines:

1. **Add or update tests** for the affected components
2. **Run the tests** to ensure they pass
3. **Check the coverage** to ensure the new code is adequately tested
4. **Update this test plan** if necessary

## Continuous Integration

The tests should be integrated into a CI/CD pipeline to ensure they are run automatically on every commit. This will help catch regressions early.

## Test Data

The tests use mock data and services to avoid dependencies on external systems. This ensures that the tests are reliable and can be run in any environment.

## Test Environment

The tests are designed to run in a development environment. They do not require any special configuration or external dependencies.

## Test Reporting

The test runner script generates a report of the test results. This report includes:

- Number of tests run
- Number of tests passed
- Number of tests failed
- Coverage report (if requested)

## Conclusion

This test plan provides a comprehensive approach to testing the exo Multi-Agent Framework. By following this plan, we can ensure that the framework functions correctly and reliably.

# codenose ignore
"""
CODENOSE TEST REFERENCE
=======================

This file shows correct and incorrect testing patterns.
Codenose points here when it detects test quality issues.

Run: python -c "from codenose import CodeNose; print(CodeNose.show_test_example())"
"""

# =============================================================================
# BAD PATTERNS - What NOT to do
# =============================================================================

def test_bad_no_assert():
    """
    BAD: test_no_assert

    This test runs code but never validates anything.
    If process_data() returns garbage or raises an exception
    that gets swallowed, this test still "passes".
    """
    result = process_data({"key": "value"})
    # ... nothing checked, test always passes


def test_bad_prints_instead_of_asserting():
    """
    BAD: test_prints_success

    Printing a message is not validation. The print happens
    regardless of whether the code actually worked correctly.
    """
    result = process_data({"key": "value"})
    print("it worked!")  # This always prints, even if result is wrong


def test_bad_assert_true():
    """
    BAD: test_assert_true_only

    'assert True' always passes. It doesn't validate
    anything about the actual behavior.
    """
    process_data({"key": "value"})
    assert True  # Always passes, tests nothing


def test_bad_bare_call():
    """
    BAD: test_no_assert (variant)

    Just calling a function without checking return value
    or side effects. Only catches if function raises.
    """
    transform_output(input_data)
    validate_input(user_input)
    # No assertions - did these actually work?


# =============================================================================
# GOOD PATTERNS - What to do
# =============================================================================

def test_good_return_value():
    """
    GOOD: Validates return value with meaningful assertions.

    Each assertion checks a specific property of the result.
    If something breaks, you know exactly what failed.
    """
    result = process_data({"key": "value"})

    assert result is not None, "Should return a result"
    assert isinstance(result, dict), "Should return a dict"
    assert result["status"] == "complete", "Status should be complete"
    assert len(result["items"]) > 0, "Should have at least one item"


def test_good_edge_cases():
    """
    GOOD: Tests edge cases and error conditions.

    Don't just test the happy path. Test what happens
    when things go wrong.
    """
    # Empty input
    result = process_data({})
    assert result["status"] == "empty", "Empty input should return empty status"

    # Invalid input should raise
    try:
        process_data(None)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "cannot be None" in str(e)


def test_good_side_effects():
    """
    GOOD: Verifies side effects actually happened.

    If your function writes to a file or database,
    verify that write actually occurred.
    """
    output_path = "/tmp/test_output.txt"

    write_report(data, output_path)

    # Verify the side effect
    assert os.path.exists(output_path), "Output file should exist"
    content = open(output_path).read()
    assert "Report" in content, "File should contain report"


# =============================================================================
# AGENT BEHAVIORAL TESTS - For AI agent testing
# =============================================================================

async def test_good_agent_behavioral():
    """
    GOOD: Agent behavioral test with built-in assertions.

    This pattern from AgentConfigTestTool shows how to test
    AI agent behavior with declarative assertions.
    """
    result = await agent_config_test(
        test_prompt="Analyze the file /tmp/test.py",
        system_prompt="You are a code analyzer",
        tools=["SafeCodeReaderTool"],

        # ASSERTIONS - what must be true for test to pass
        assert_tool_used="SafeCodeReaderTool",  # Agent must use this tool
        assert_no_errors=True,                   # No tool errors allowed
        assert_goal_accomplished=True,           # Agent must complete goal
        assert_min_tool_calls=1,                 # Must make at least 1 call
    )

    # Verify all assertions passed
    assert result["assertions"]["all_passed"], \
        f"Assertions failed: {result['assertions']['results']}"


# =============================================================================
# PYTEST FIXTURES PATTERN
# =============================================================================

import pytest

@pytest.fixture
def sample_data():
    """
    GOOD: Use fixtures for test data setup.

    Fixtures make tests cleaner and data reusable.
    """
    return {
        "id": 123,
        "name": "test",
        "items": [1, 2, 3]
    }


def test_good_with_fixture(sample_data):
    """
    GOOD: Uses fixture for clean test setup.
    """
    result = process_data(sample_data)

    assert result["id"] == sample_data["id"]
    assert result["processed"] is True


# =============================================================================
# INTEGRATION TEST PATTERN
# =============================================================================

@pytest.mark.integration
def test_integration_full_pipeline():
    """
    GOOD: Integration test that exercises multiple components.

    Mark integration tests so they can be run separately.
    These tests are slower but catch real integration issues.
    """
    # Setup
    input_data = load_test_data("fixtures/input.json")

    # Exercise full pipeline
    validated = validate_input(input_data)
    processed = process_data(validated)
    output = transform_output(processed)

    # Verify end-to-end
    assert output["status"] == "complete"
    assert len(output["results"]) == len(input_data["items"])
    assert all(r["valid"] for r in output["results"])


# =============================================================================
# SUMMARY
# =============================================================================

"""
KEY PRINCIPLES:

1. Every test MUST have at least one meaningful assertion
2. Assertions should check ACTUAL VALUES, not just "assert True"
3. Don't print messages as validation - use assert statements
4. Test edge cases and error conditions
5. For side effects, verify the effect happened
6. Use fixtures for clean test data
7. Mark integration tests for separate runs
8. For agents, use behavioral assertions

If codenose flagged your test file, check:
- Do all test_* functions have assertions?
- Are assertions checking actual values?
- Are you printing instead of asserting?
"""


# Dummy functions for example (not real implementations)
def process_data(data): pass
def validate_input(data): pass
def transform_output(data): pass
def write_report(data, path): pass
def load_test_data(path): pass
async def agent_config_test(**kwargs): pass
import os
input_data = {}
user_input = {}
data = {}

# codenose ignore
"""Default configuration values for CodeNose."""

DEFAULT_CANONICAL_FILENAMES = {
    "__init__.py",
    "utils.py",
    "core.py",
    "models.py",
    "mcp_server.py",
    "api.py",
    "cli.py",
    "main.py",
    "config.py",
    "constants.py",
    "types.py",
    "exceptions.py",
}

DEFAULT_EXEMPT_DIRS = {
    "util_deps",
    "tests",
    "test",
    "__pycache__",
    "migrations",
    "scripts",
    "hooks",
    "commands",
}

DEFAULT_TEST_PATTERNS = [
    r"^test_.*\.py$",
    r"^.*_test\.py$",
    r"^conftest\.py$",
]

DEFAULT_FACADE_FILES = {"mcp_server.py", "api.py", "cli.py"}

DEFAULT_MAX_FILE_LINES = 400
DEFAULT_MAX_FUNCTION_LINES = 33
DEFAULT_MIN_DUP_BLOCK_SIZE = 3
DEFAULT_MIN_LOG_LINES = 20

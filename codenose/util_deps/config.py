# codenose ignore
"""Default configuration values for CodeNose."""
import os
from pathlib import Path

# Architecture lock file location
ARCH_LOCK_FILE = Path(os.path.expanduser("~/.claude/.codenose_arch_lock"))


def is_arch_locked() -> bool:
    """Check if architecture lock mode is enabled."""
    return ARCH_LOCK_FILE.exists()


def set_arch_lock(enabled: bool) -> bool:
    """Enable or disable architecture lock mode. Returns new state."""
    if enabled:
        ARCH_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        ARCH_LOCK_FILE.touch()
    else:
        if ARCH_LOCK_FILE.exists():
            ARCH_LOCK_FILE.unlink()
    return is_arch_locked()


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

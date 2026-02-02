# codenose ignore
"""
CodeNose Utils - Re-exports from util_deps.

This module provides the public API surface for codenose utilities.
All implementation lives in util_deps/ subdirectory.
"""
from .util_deps.config import (
    DEFAULT_CANONICAL_FILENAMES,
    DEFAULT_EXEMPT_DIRS,
    DEFAULT_TEST_PATTERNS,
    DEFAULT_FACADE_FILES,
    DEFAULT_MAX_FILE_LINES,
    DEFAULT_MAX_FUNCTION_LINES,
    DEFAULT_MIN_DUP_BLOCK_SIZE,
    DEFAULT_MIN_LOG_LINES,
)

from .util_deps.detectors import (
    check_syntax_errors,
    check_file_length,
    check_modularization,
    check_duplication,
    check_logging,
    check_import_duplication,
    check_sys_path_usage,
    check_traceback_handling,
    check_architecture,
    check_facade_logic,
)

from .util_deps.scanners import (
    scan_file,
    scan_directory,
)

from .util_deps.formatters import (
    format_smell_table,
    format_codenose_output,
)

__all__ = [
    # Config
    "DEFAULT_CANONICAL_FILENAMES",
    "DEFAULT_EXEMPT_DIRS",
    "DEFAULT_TEST_PATTERNS",
    "DEFAULT_FACADE_FILES",
    "DEFAULT_MAX_FILE_LINES",
    "DEFAULT_MAX_FUNCTION_LINES",
    "DEFAULT_MIN_DUP_BLOCK_SIZE",
    "DEFAULT_MIN_LOG_LINES",
    # Detectors
    "check_syntax_errors",
    "check_file_length",
    "check_modularization",
    "check_duplication",
    "check_logging",
    "check_import_duplication",
    "check_sys_path_usage",
    "check_traceback_handling",
    "check_architecture",
    "check_facade_logic",
    # Scanners
    "scan_file",
    "scan_directory",
    # Formatters
    "format_smell_table",
    "format_codenose_output",
]

#!/usr/bin/env python3
# codenose ignore
"""
CodeNose v2 PreToolUse Hook - Architecture Lock Enforcement.

Blocks writes to non-canonical filenames when arch lock is enabled.
Runs BEFORE the write happens, so it can actually prevent it.
"""
import json
import sys
import re
from pathlib import Path

try:
    from codenose import CodeNose
    from codenose.utils import (
        DEFAULT_CANONICAL_FILENAMES,
        DEFAULT_EXEMPT_DIRS,
        DEFAULT_TEST_PATTERNS,
    )
except ImportError:
    sys.exit(0)


def check_architecture(file_path: str) -> str | None:
    """Check if file follows canonical architecture naming."""
    path = Path(file_path)
    filename = path.name
    parent_dir = path.parent.name
    path_parts = set(path.parts)

    if not filename.endswith('.py'):
        return None

    if parent_dir in DEFAULT_EXEMPT_DIRS or any(d in path_parts for d in DEFAULT_EXEMPT_DIRS):
        return None

    for pattern in DEFAULT_TEST_PATTERNS:
        if re.match(pattern, filename):
            return None

    if filename not in DEFAULT_CANONICAL_FILENAMES:
        return f"'{filename}' is not canonical. Use: utils.py, core.py, models.py, mcp_server.py, api.py, cli.py"

    return None


def main():
    try:
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "unknown")
        tool_input = input_data.get("tool_input", {})

        if tool_name not in ["Edit", "Write", "MultiEdit"]:
            sys.exit(0)

        file_path = tool_input.get("file_path", "")

        # Only enforce if arch lock is ON
        if not CodeNose.is_arch_locked():
            sys.exit(0)

        if not file_path.endswith('.py'):
            sys.exit(0)

        violation = check_architecture(file_path)

        if violation:
            nose = CodeNose()
            tag = nose.theme.output_tag
            error_msg = f"""
<{tag}>
[ARCH LOCK MODE - BLOCKED]
{nose.theme.get_emoji("arch")}=arch

{violation}

To disable lock: rm ~/.claude/.codenose_arch_lock
</{tag}>
"""
            print(error_msg, file=sys.stderr)
            sys.exit(2)  # Block the write

        sys.exit(0)

    except Exception:
        # On error, allow the operation
        sys.exit(0)


if __name__ == "__main__":
    main()

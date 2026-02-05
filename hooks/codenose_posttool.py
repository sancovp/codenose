#!/usr/bin/env python3
# codenose ignore
"""
CodeNose v2 PostToolUse Hook - Thin wrapper using codenose library.

Detects code smells after Edit/Write/MultiEdit operations.
All logic delegated to the codenose library.
"""
import json
import sys

try:
    from codenose import CodeNose
except ImportError:
    # Library not installed, exit silently
    sys.exit(0)


def main():
    try:
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "unknown")
        tool_input = input_data.get("tool_input", {})

        if tool_name not in ["Edit", "Write", "MultiEdit"]:
            sys.exit(0)

        file_path = tool_input.get("file_path", "")
        if not file_path.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c')):
            sys.exit(0)

        # Use the library
        nose = CodeNose()
        result = nose.scan_file(file_path)

        if not result.smells:
            sys.exit(0)

        # Check for critical smells
        has_critical = any(s.critical for s in result.smells)

        # Check arch lock for architecture violations
        if nose.is_arch_locked():
            arch_smells = [s for s in result.smells if s.type == "arch"]
            if arch_smells:
                for s in arch_smells:
                    s.critical = True
                has_critical = True

        # Check TDD mode - coverage warnings become CRITICAL
        if nose.is_tdd_mode():
            coverage_smells = [s for s in result.smells if s.type == "coverage"]
            if coverage_smells:
                for s in coverage_smells:
                    s.critical = True
                    s.msg = f"[TDD MODE] {s.msg}"
                has_critical = True

        # Format and output
        output = nose.format_output(result)
        if output:
            print(output, file=sys.stderr)

        # Exit codes: 0=ok, 2=critical
        sys.exit(2 if has_critical else 0)

    except Exception as e:
        print(f"CodeNose error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()

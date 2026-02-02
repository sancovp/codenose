# CodeNose 👃

Code smell detection for LLMs - sniffs out duplicate logic, architecture violations, and other blind spots.

## Installation

```bash
pip install codenose
```

## Usage

```python
from codenose import CodeNose

# Quick scan a file
result = CodeNose.quick_scan_file("/path/to/file.py")
print(f"Found {len(result.smells)} smells")

# Scan a directory
result = CodeNose.quick_scan_directory("/path/to/project")
print(f"Cleanliness: {result.cleanliness_score:.0%}")

# With custom configuration
nose = CodeNose(
    max_file_lines=500,
    max_function_lines=50,
    canonical_filenames={"utils.py", "core.py", "models.py"}
)
result = nose.scan_file("/path/to/file.py")
```

## Smell Types

| Type | Emoji | Description |
|------|-------|-------------|
| syntax | 🔴 | Syntax errors |
| syspath | 💀 | sys.path manipulation |
| traceback | ☠️ | Exception without traceback |
| arch | 🏗️ | Non-canonical filename |
| facade | 🧅 | Logic in facade layer |
| dup | 👯 | Duplicate code blocks |
| long | 📏 | File/function too long |
| log | 📝 | Missing logging |
| import | 📦 | Duplicate imports |

## Configuration

```python
nose = CodeNose(
    # Architecture settings
    canonical_filenames={"utils.py", "core.py", ...},
    exempt_dirs={"tests", "__pycache__", ...},
    facade_files={"api.py", "cli.py", "mcp_server.py"},

    # Thresholds
    max_file_lines=400,
    max_function_lines=33,
    min_dup_block_size=3,
)
```

## License

MIT

# codenose ignore
"""
Smell detector functions.

Each detector returns a list of Smell objects.
"""
import ast
import os
import py_compile
import re
import tempfile
import traceback
from collections import defaultdict
from pathlib import Path

from ..models import Smell
from .config import (
    DEFAULT_CANONICAL_FILENAMES,
    DEFAULT_EXEMPT_DIRS,
    DEFAULT_TEST_PATTERNS,
    DEFAULT_MAX_FILE_LINES,
    DEFAULT_MAX_FUNCTION_LINES,
    DEFAULT_MIN_DUP_BLOCK_SIZE,
    DEFAULT_MIN_LOG_LINES,
)


def check_syntax_errors(content: str, file_path: str) -> list[Smell]:
    """Check for Python syntax errors."""
    if not file_path.endswith('.py'):
        return []
    try:
        ast.parse(content)
        return []
    except SyntaxError as e:
        return [Smell(type="syntax", line=e.lineno or 0, msg=e.msg or "Syntax error", critical=True)]
    except Exception as e:
        return _fallback_syntax_check(content, e)


def _fallback_syntax_check(content: str, original_error: Exception) -> list[Smell]:
    """Fallback syntax check using py_compile."""
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            temp_file = f.name
        py_compile.compile(temp_file, doraise=True)
        return []
    except py_compile.PyCompileError as e:
        return [Smell(type="syntax", line=0, msg=str(e), critical=True)]
    except Exception:
        return [Smell(type="syntax", line=0, msg=f"Parse failed: {original_error}", critical=True)]
    finally:
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)


def check_file_length(content: str, file_path: str, max_lines: int = DEFAULT_MAX_FILE_LINES) -> list[Smell]:
    """Check if file is too long."""
    line_count = len(content.split('\n'))
    if line_count > max_lines:
        return [Smell(
            type="long", line=0,
            msg=f"File is {line_count} lines. Modularize with mixins or decompose utils.",
            critical=True
        )]
    elif line_count > int(max_lines * 0.75):
        return [Smell(type="long", line=0, msg=f"File is {line_count} lines - approaching limit", critical=False)]
    return []


def check_modularization(content: str, file_path: str, max_func_lines: int = DEFAULT_MAX_FUNCTION_LINES) -> list[Smell]:
    """Check if functions are too long."""
    smells = []
    lines = content.split('\n')
    current_func, func_start, indent = None, 0, 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('def '):
            if current_func and (i - func_start) > max_func_lines:
                smells.append(Smell(type="long", line=func_start + 1, msg=f"{current_func}() is {i - func_start} lines"))
            current_func = stripped.split('(')[0].replace('def ', '')
            func_start, indent = i, len(line) - len(line.lstrip())
        elif current_func and stripped and len(line) - len(line.lstrip()) <= indent:
            if (i - func_start) > max_func_lines:
                smells.append(Smell(type="long", line=func_start + 1, msg=f"{current_func}() is {i - func_start} lines"))
            current_func = None
    return smells


def check_duplication(content: str, file_path: str, min_block: int = DEFAULT_MIN_DUP_BLOCK_SIZE) -> list[Smell]:
    """Check for duplicate logic blocks."""
    lines = content.split('\n')
    blocks = _find_meaningful_blocks(lines, min_block)
    return _find_duplicates(blocks)


def _find_meaningful_blocks(lines: list[str], min_block: int) -> list[tuple[str, int]]:
    """Find meaningful code blocks for duplication check."""
    blocks = []
    for i in range(len(lines) - min_block + 1):
        block_lines = []
        for j in range(min_block):
            line = lines[i + j].strip()
            if _is_meaningful_line(line):
                block_lines.append(line)
        if len(block_lines) >= min_block:
            blocks.append(('\n'.join(block_lines), i + 1))
    return blocks


def _is_meaningful_line(line: str) -> bool:
    """Check if a line is meaningful for duplication detection."""
    return (line and not line.startswith('#') and not line.startswith('"""') and
            not line.startswith("'''") and len(line) > 10 and
            ('=' in line or 'if ' in line or 'for ' in line or 'while ' in line or 'def ' in line))


def _find_duplicates(blocks: list[tuple[str, int]]) -> list[Smell]:
    """Find duplicate blocks and return smells."""
    counts = defaultdict(list)
    for text, line in blocks:
        normalized = re.sub(r'\s+', ' ', text.strip())
        if len(normalized) > 30:
            counts[normalized].append(line)
    return [Smell(type="dup", lines=lns, count=len(lns)) for lns in counts.values() if len(lns) > 1]


def check_logging(content: str, file_path: str, min_lines: int = DEFAULT_MIN_LOG_LINES) -> list[Smell]:
    """Check if code uses proper logging."""
    if 'test' in file_path.lower() or len(content.split('\n')) < min_lines:
        return []
    has_funcs = 'def ' in content
    needs_log = 'except' in content or 'raise' in content or any(k in content for k in ['requests.', 'open(', 'subprocess.'])
    if has_funcs and (needs_log or len(content.split('\n')) > 50):
        if 'logging.' not in content and 'logger.' not in content:
            return [Smell(type="log", line=0, msg="No logging found")]
    return []


def check_import_duplication(content: str, file_path: str) -> list[Smell]:
    """Check for imports that appear both globally and locally."""
    lines = content.split('\n')
    global_imports, local_imports, in_func = set(), [], False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(('def ', 'class ')):
            in_func = True
        elif line and not line[0].isspace() and not stripped.startswith(('#', '"""', "'''")):
            in_func = False
        if stripped.startswith(('import ', 'from ')):
            module = _extract_module_name(stripped)
            if module:
                if in_func:
                    local_imports.append((module, i + 1))
                else:
                    global_imports.add(module)

    return [Smell(type="import", line=ln, msg=f"'{m}' duplicated globally and locally")
            for m, ln in local_imports if m in global_imports]


def _extract_module_name(line: str) -> str:
    """Extract module name from import statement."""
    if line.startswith('import '):
        return line.replace('import ', '').split(' as ')[0].split('.')[0].split(',')[0].strip()
    elif line.startswith('from '):
        return line.split(' ')[1].split('.')[0].strip()
    return ""


def check_sys_path_usage(content: str, file_path: str) -> list[Smell]:
    """Check for forbidden sys.path manipulation."""
    smells = []
    for i, line in enumerate(content.split('\n')):
        lower = line.strip().lower()
        if lower.startswith('#'):
            continue
        if 'sys.path' in lower:
            smells.append(Smell(type="syspath", line=i + 1, msg="sys.path manipulation", critical=True))
        if 'pythonpath' in lower and any(k in lower for k in ['subprocess', 'os.', 'bash']):
            smells.append(Smell(type="syspath", line=i + 1, msg="PYTHONPATH manipulation", critical=True))
    return smells


def check_traceback_handling(content: str, file_path: str) -> list[Smell]:
    """Check for exception handling without proper traceback logging."""
    smells, lines = [], content.split('\n')
    in_except, except_line, block = False, 0, []
    tb_kw = ['traceback', 'exc_info', 'logging.exception', 'logger.exception', 'print_exc', 'format_exc', 'raise']
    sub_kw = ['return', 'print(', 'logging.', 'logger.', '=', 'if ', 'for ']

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('except'):
            in_except, except_line, block = True, i + 1, []
        elif in_except:
            if not stripped or line[0].isspace():
                block.append(stripped)
            else:
                text = ' '.join(block).lower()
                if any(k in text for k in sub_kw) and 'pass' not in text and not any(k in text for k in tb_kw):
                    smells.append(Smell(type="traceback", line=except_line, msg="Exception without traceback", critical=True))
                in_except = False
    return smells


def check_architecture(file_path: str, canonical: set[str] = None, exempt: set[str] = None, patterns: list[str] = None) -> list[Smell]:
    """Check if file follows canonical architecture naming."""
    canonical = canonical or DEFAULT_CANONICAL_FILENAMES
    exempt = exempt or DEFAULT_EXEMPT_DIRS
    patterns = patterns or DEFAULT_TEST_PATTERNS

    path = Path(file_path)
    if not path.name.endswith('.py'):
        return []
    if path.parent.name in exempt or any(d in path.parts for d in exempt):
        return []
    if any(re.match(p, path.name) for p in patterns):
        return []
    if path.name not in canonical:
        return [Smell(type="arch", line=0, msg=f"'{path.name}' not canonical. Use: utils.py, core.py, models.py", filename=path.name)]
    return []


def check_facade_logic(content: str, file_path: str, facade_files: set[str] = None) -> list[Smell]:
    """Check if facade files contain logic instead of pure delegation."""
    facade_files = facade_files or {"mcp_server.py", "api.py", "cli.py"}
    if Path(file_path).name not in facade_files:
        return []

    smells = []
    logic_pat = [(r'\bif\s+.*:', 'conditional'), (r'\bfor\s+.*:', 'loop'), (r'\bwhile\s+.*:', 'loop'), (r'\btry\s*:', 'try/except')]
    skip_pat = [r'^\s*#', r'^\s*$', r'@\w+', r'def\s+', r'return\s+', r'from\s+', r'import\s+', r'class\s+', r'"""', r"'''"]

    for i, line in enumerate(content.split('\n')):
        if any(re.match(p, line.strip()) for p in skip_pat):
            continue
        for pat, name in logic_pat:
            if re.search(pat, line) and 'return' not in line:
                smells.append(Smell(type="facade", line=i + 1, msg=f"Logic in facade: {name}"))
                break
    return smells[:3] if len(smells) > 2 else []


# =============================================================================
# BUILTIN RULES REGISTRY
# =============================================================================

BUILTIN_RULES = {
    "syntax": check_syntax_errors,
    "long": check_file_length,
    "modularization": check_modularization,
    "dup": check_duplication,
    "log": check_logging,
    "import": check_import_duplication,
    "syspath": check_sys_path_usage,
    "traceback": check_traceback_handling,
    "arch": check_architecture,
    "facade": check_facade_logic,
}

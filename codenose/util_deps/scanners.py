# codenose ignore
"""File and directory scanning with configurable rules."""
from collections import defaultdict
from pathlib import Path
from typing import Optional

from ..models import ScanResult, DirectoryScanResult, FullConfig, RuleConfig
from .detectors import BUILTIN_RULES
from .loader import load_full_config, import_rule_function


def scan_file(file_path: str, config: Optional[FullConfig] = None) -> ScanResult:
    """Scan a single file using configured rules."""
    config = config or load_full_config()

    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception:
        return ScanResult(file_path=file_path, smells=[])

    # Check first 3 lines for ignore directive
    first_lines = '\n'.join(content.split('\n')[:3])
    if '# codenose ignore' in first_lines or '// codenose ignore' in first_lines:
        return ScanResult(file_path=file_path, smells=[])

    all_smells = []

    # Run enabled builtin rules
    for rule_name, rule_func in BUILTIN_RULES.items():
        rule_cfg = config.rules.builtin.get(rule_name, RuleConfig())
        if not rule_cfg.enabled:
            continue

        # Get rule-specific config
        rule_config = rule_cfg.config

        # Call the rule function
        try:
            smells = rule_func(content, file_path, **rule_config) if rule_config else rule_func(content, file_path)
        except TypeError:
            # Function doesn't accept extra kwargs
            smells = rule_func(content, file_path)

        # Apply severity override
        for smell in smells:
            smell.severity_override = rule_cfg.severity

        all_smells.extend(smells)

    # Run enabled custom rules
    for custom_rule in config.rules.custom:
        if not custom_rule.enabled:
            continue

        func = import_rule_function(custom_rule)
        if func is None:
            continue

        try:
            smells = func(content, file_path, custom_rule.config)
            for smell in smells:
                smell.type = custom_rule.type
                smell.severity_override = custom_rule.severity
            all_smells.extend(smells)
        except Exception as e:
            print(f"Warning: Custom rule '{custom_rule.name}' failed: {e}")

    return ScanResult(file_path=file_path, smells=all_smells)


def scan_directory(directory: str, max_files: int = 50, config: Optional[FullConfig] = None) -> DirectoryScanResult:
    """Scan a directory for code smells."""
    config = config or load_full_config()
    py_files = list(Path(directory).rglob("*.py"))[:max_files]

    result = DirectoryScanResult(
        directory=directory,
        total_files=len(py_files),
        by_severity={"critical": 0, "warning": 0, "info": 0},
    )

    if not py_files:
        return result

    by_type = defaultdict(int)
    for f in py_files:
        scan = scan_file(str(f), config)
        if scan.smells:
            result.files_with_smells += 1
            result.total_smells += len(scan.smells)
            for smell in scan.smells:
                by_type[smell.type] += 1
                result.by_severity[smell.severity.value] += 1

    result.by_type = dict(by_type)
    if result.total_files > 0:
        penalty = (result.by_severity["critical"] * 0.15 + result.by_severity["warning"] * 0.03 +
                   result.by_severity["info"] * 0.005) / result.total_files
        result.cleanliness_score = max(0.0, min(1.0, 1.0 - penalty))

    return result

# codenose ignore
"""Output formatting with theme support."""
from collections import defaultdict
from typing import Optional

from ..models import Smell, ScanResult, ThemeConfig


def format_smell_table(smells: list[Smell], theme: Optional[ThemeConfig] = None) -> str:
    """Format smells as a markdown table using theme."""
    if not smells:
        return ""

    theme = theme or ThemeConfig()

    by_type = defaultdict(list)
    for smell in smells:
        by_type[smell.type].append(smell)

    has_critical = any(s.critical or s.severity_override == "critical" for s in smells)
    legend = " | ".join(f"{theme.get_emoji(t)}={t}" for t in by_type)

    rows = ["| Smell | Location | Info |", "|-------|----------|------|"]
    for smell_type, type_smells in by_type.items():
        emoji = theme.get_emoji(smell_type)
        for smell in type_smells[:3]:
            loc = f"L{smell.line}" if smell.line else "file"
            msg = (smell.msg or "")[:40]
            rows.append(f"| {emoji} | {loc} | {msg} |")
        if len(type_smells) > 3:
            rows.append(f"| {emoji} | ... | +{len(type_smells) - 3} more |")

    critical_label = theme.severity_names.get("critical", "CRITICAL")
    critical_str = f"\U0001f6a8 {critical_label}" if has_critical else ""
    smell_word = theme.smell_word

    return f"{len(smells)} {smell_word}(s) {critical_str}\n{legend}\n\n" + "\n".join(rows)


def format_output(scan_result: ScanResult, theme: Optional[ThemeConfig] = None, arch_locked: bool = False, tdd_mode: bool = False) -> str:
    """Format a scan result as tagged output block using theme.

    When critical smells exist, uses system-reminder style for visibility.
    """
    if not scan_result.smells:
        return ""

    theme = theme or ThemeConfig()
    lock_str = "[ARCH LOCK: ON]" if arch_locked else ""
    tdd_str = "[TDD MODE: ON]" if tdd_mode else ""
    table = format_smell_table(scan_result.smells, theme)

    has_critical = any(s.critical or s.severity_override == "critical" for s in scan_result.smells)

    # Use system-reminder style when critical for agent attention
    if has_critical:
        flags = " ".join(filter(None, [lock_str, tdd_str]))
        return f"""<system-reminder>
⚠️ CODENOSE CRITICAL - ACTION REQUIRED {flags}

{table}

You MUST address these issues before proceeding. Do not ignore this warning.
</system-reminder>"""

    # Normal output for non-critical
    tag = theme.output_tag
    return f"<{tag}>\n{table} {lock_str}\n</{tag}>"

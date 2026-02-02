# codenose ignore
"""
CodeNose - Configurable code smell detection.

Usage:
    from codenose import CodeNose

    # Quick scan
    result = CodeNose.quick_scan("/path/to/code")

    # With config
    nose = CodeNose(config_dir=".codenose")
    result = nose.scan_file("myfile.py")

    # Initialize config files
    CodeNose.init_config()
"""
from .core import CodeNose
from .models import (
    Smell,
    SmellSeverity,
    ScanResult,
    DirectoryScanResult,
    ThemeConfig,
    RuleConfig,
    CustomRuleConfig,
    RulesConfig,
    FullConfig,
    SMELL_EMOJI,
    CRITICAL_SMELL_TYPES,
    WARNING_SMELL_TYPES,
    BUILTIN_SMELL_TYPES,
)

__version__ = "0.2.0"
__all__ = [
    "CodeNose",
    "Smell",
    "SmellSeverity",
    "ScanResult",
    "DirectoryScanResult",
    "ThemeConfig",
    "RuleConfig",
    "CustomRuleConfig",
    "RulesConfig",
    "FullConfig",
    "SMELL_EMOJI",
    "CRITICAL_SMELL_TYPES",
    "WARNING_SMELL_TYPES",
    "BUILTIN_SMELL_TYPES",
]

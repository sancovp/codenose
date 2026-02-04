# codenose ignore
"""
CodeNose Models - Pydantic models for code smell detection and configuration.
"""
from enum import Enum
from typing import Optional, Callable, Any
from pydantic import BaseModel, Field


# =============================================================================
# SMELL MODELS
# =============================================================================

class SmellSeverity(str, Enum):
    """Severity levels for code smells."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class Smell(BaseModel):
    """A single code smell detection result."""
    type: str  # String to allow custom types
    line: int = 0
    msg: str = ""
    critical: bool = False
    lines: Optional[list[int]] = None
    count: Optional[int] = None
    filename: Optional[str] = None
    severity_override: Optional[str] = None  # From rule config

    @property
    def severity(self) -> SmellSeverity:
        """Determine severity based on override, critical flag, or type."""
        if self.severity_override:
            return SmellSeverity(self.severity_override)
        if self.critical:
            return SmellSeverity.CRITICAL
        return SmellSeverity.INFO


class ScanResult(BaseModel):
    """Result of scanning a file for smells."""
    file_path: str
    smells: list[Smell] = Field(default_factory=list)

    @property
    def has_critical(self) -> bool:
        return any(s.severity == SmellSeverity.CRITICAL for s in self.smells)

    @property
    def smell_count(self) -> int:
        return len(self.smells)


class DirectoryScanResult(BaseModel):
    """Result of scanning a directory for smells."""
    directory: str
    total_files: int = 0
    files_with_smells: int = 0
    total_smells: int = 0
    by_severity: dict[str, int] = Field(default_factory=lambda: {"critical": 0, "warning": 0, "info": 0})
    by_type: dict[str, int] = Field(default_factory=dict)
    cleanliness_score: float = 1.0


# =============================================================================
# CONFIGURATION MODELS
# =============================================================================

class ThemeConfig(BaseModel):
    """Theming/branding configuration."""
    tool_name: str = "CodeNose"
    tool_emoji: str = "\U0001f443"  # 👃
    smell_word: str = "smell"
    output_tag: str = "codenose"
    severity_names: dict[str, str] = Field(default_factory=lambda: {
        "critical": "CRITICAL",
        "warning": "WARNING",
        "info": "INFO"
    })
    emoji_map: dict[str, str] = Field(default_factory=lambda: {
        "syntax": "\U0001f534",      # 🔴
        "syspath": "\U0001f480",     # 💀
        "traceback": "\u2620\ufe0f", # ☠️
        "arch": "\U0001f3d7\ufe0f",  # 🏗️
        "facade": "\U0001f9c5",      # 🧅
        "dup": "\U0001f46f",         # 👯
        "long": "\U0001f4cf",        # 📏
        "log": "\U0001f4dd",         # 📝
        "import": "\U0001f4e6",      # 📦
        "coverage": "\U0001f9ea",    # 🧪
        "test_no_assert": "\u274c",  # ❌
        "test_prints_success": "\U0001f5a8\ufe0f",  # 🖨️
        "test_assert_true_only": "\u2714\ufe0f",    # ✔️
    })

    def get_emoji(self, smell_type: str) -> str:
        """Get emoji for a smell type, with fallback."""
        return self.emoji_map.get(smell_type, self.tool_emoji)


class RuleConfig(BaseModel):
    """Configuration for a single rule."""
    enabled: bool = True
    severity: str = "info"
    config: dict[str, Any] = Field(default_factory=dict)


class CustomRuleConfig(BaseModel):
    """Configuration for an external custom rule."""
    name: str
    type: str  # The smell type this rule produces
    module: str  # Python module path
    function: str  # Function name in module
    enabled: bool = True
    severity: str = "warning"
    config: dict[str, Any] = Field(default_factory=dict)


class RulesConfig(BaseModel):
    """All rules configuration."""
    builtin: dict[str, RuleConfig] = Field(default_factory=dict)
    custom: list[CustomRuleConfig] = Field(default_factory=list)


class FullConfig(BaseModel):
    """Complete codenose configuration."""
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    rules: RulesConfig = Field(default_factory=RulesConfig)


# =============================================================================
# DEFAULTS (for backwards compatibility)
# =============================================================================

# Built-in smell types
BUILTIN_SMELL_TYPES = {"syntax", "syspath", "traceback", "arch", "facade", "dup", "long", "log", "import"}

# Critical smell types (default)
CRITICAL_SMELL_TYPES = {"syntax", "syspath", "traceback"}

# Warning smell types (default)
WARNING_SMELL_TYPES = {"arch", "facade"}

# Default emoji map (for backwards compat)
SMELL_EMOJI = ThemeConfig().emoji_map

# codenose ignore
"""
Config loader - loads theme, rules, and custom rules from JSON files.

Priority: ~/.config/codenose/ (user) > .codenose/ (project) > defaults
"""
import importlib
import json
import os
from pathlib import Path
from typing import Callable, Optional

from ..models import (
    ThemeConfig, RuleConfig, RulesConfig, CustomRuleConfig, FullConfig, Smell
)

# Type alias for rule functions
RuleFunc = Callable[[str, str, dict], list[Smell]]

USER_CONFIG_DIR = Path.home() / ".config" / "codenose"
PROJECT_CONFIG_NAME = ".codenose"


def find_config_dirs() -> list[Path]:
    """Find config directories in priority order (user > project)."""
    dirs = []

    # User config (base)
    if USER_CONFIG_DIR.exists():
        dirs.append(USER_CONFIG_DIR)

    # Project config (overrides)
    project_dir = Path.cwd() / PROJECT_CONFIG_NAME
    if project_dir.exists():
        dirs.append(project_dir)

    return dirs


def load_json_file(path: Path) -> dict:
    """Load a JSON file, return empty dict if not found."""
    if path.exists():
        return json.loads(path.read_text())
    return {}


def merge_dicts(base: dict, override: dict) -> dict:
    """Deep merge two dicts, override wins for conflicts."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def load_theme(config_dirs: list[Path] = None) -> ThemeConfig:
    """Load theme config with merging."""
    config_dirs = config_dirs or find_config_dirs()
    merged = {}

    for config_dir in config_dirs:
        theme_file = config_dir / "theme.json"
        if theme_file.exists():
            merged = merge_dicts(merged, load_json_file(theme_file))

    return ThemeConfig(**merged) if merged else ThemeConfig()


def load_rules(config_dirs: list[Path] = None) -> dict[str, RuleConfig]:
    """Load builtin rules config with merging."""
    config_dirs = config_dirs or find_config_dirs()
    merged = {}

    for config_dir in config_dirs:
        rules_file = config_dir / "rules.json"
        data = load_json_file(rules_file)
        if "rules" in data:
            merged = merge_dicts(merged, data["rules"])

    return {name: RuleConfig(**cfg) for name, cfg in merged.items()}


def load_custom_rules(config_dirs: list[Path] = None) -> list[CustomRuleConfig]:
    """Load custom rules from all config dirs (accumulative)."""
    config_dirs = config_dirs or find_config_dirs()
    all_rules = []

    for config_dir in config_dirs:
        rules_file = config_dir / "custom_rules.json"
        data = load_json_file(rules_file)
        if "rules" in data:
            for rule_data in data["rules"]:
                all_rules.append(CustomRuleConfig(**rule_data))

    return all_rules


def import_rule_function(rule: CustomRuleConfig) -> Optional[RuleFunc]:
    """Dynamically import a custom rule function."""
    try:
        module = importlib.import_module(rule.module)
        func = getattr(module, rule.function)
        return func
    except (ImportError, AttributeError) as e:
        # Log warning but don't crash
        print(f"Warning: Could not load custom rule '{rule.name}': {e}")
        return None


def load_full_config(config_dir: Optional[Path] = None) -> FullConfig:
    """Load complete configuration."""
    if config_dir:
        config_dirs = [config_dir]
    else:
        config_dirs = find_config_dirs()

    theme = load_theme(config_dirs)
    builtin_rules = load_rules(config_dirs)
    custom_rules = load_custom_rules(config_dirs)

    return FullConfig(
        theme=theme,
        rules=RulesConfig(builtin=builtin_rules, custom=custom_rules)
    )


def init_config_dir(path: Path = None, include_examples: bool = True) -> Path:
    """Initialize a config directory with default files."""
    path = path or USER_CONFIG_DIR
    path.mkdir(parents=True, exist_ok=True)

    # Write default theme
    theme_file = path / "theme.json"
    if not theme_file.exists():
        theme = ThemeConfig()
        theme_file.write_text(json.dumps(theme.model_dump(), indent=2))

    # Write default rules
    rules_file = path / "rules.json"
    if not rules_file.exists():
        default_rules = {
            "rules": {
                "syntax": {"enabled": True, "severity": "critical"},
                "syspath": {"enabled": True, "severity": "critical"},
                "traceback": {"enabled": True, "severity": "critical"},
                "arch": {"enabled": True, "severity": "warning"},
                "facade": {"enabled": True, "severity": "warning"},
                "dup": {"enabled": True, "severity": "info", "config": {"min_block_size": 3}},
                "long": {"enabled": True, "severity": "info", "config": {"max_file_lines": 400, "max_function_lines": 33}},
                "log": {"enabled": False, "severity": "info"},
                "import": {"enabled": True, "severity": "info"},
                "coverage": {"enabled": True, "severity": "info", "config": {"test_dirs": ["tests", "test"]}},
                "test_quality": {"enabled": True, "severity": "warning"}
            }
        }
        rules_file.write_text(json.dumps(default_rules, indent=2))

    # Write example custom rules
    custom_file = path / "custom_rules.json"
    if not custom_file.exists() and include_examples:
        example = {
            "rules": [
                {
                    "name": "example_no_prints",
                    "type": "no_print",
                    "module": "my_linting.rules",
                    "function": "check_no_prints",
                    "enabled": False,
                    "severity": "warning",
                    "config": {}
                }
            ]
        }
        custom_file.write_text(json.dumps(example, indent=2))

    return path

# codenose ignore
"""
CodeNose Core - Configurable code smell detection.

Usage:
    from codenose import CodeNose

    # With default config
    nose = CodeNose()
    result = nose.scan_file("/path/to/file.py")

    # With custom config directory
    nose = CodeNose(config_dir="/path/to/.codenose")

    # Initialize config files
    CodeNose.init_config()
"""
import os
from pathlib import Path
from typing import Optional

from .models import ScanResult, DirectoryScanResult, FullConfig, ThemeConfig
from .util_deps.loader import load_full_config, init_config_dir
from .util_deps.scanners import scan_file, scan_directory
from .util_deps.formatters import format_output, format_smell_table


ARCH_LOCK_FILE = Path.home() / ".claude" / ".codenose_arch_lock"


class CodeNose:
    """Configurable code smell detector."""

    def __init__(self, config_dir: Optional[str] = None):
        """Initialize with optional explicit config directory."""
        config_path = Path(config_dir) if config_dir else None
        self.config = load_full_config(config_path)
        self.theme = self.config.theme

    def scan(self, path: str, max_files: int = 50) -> ScanResult | DirectoryScanResult:
        """Scan a file or directory."""
        p = Path(path)
        if p.is_file():
            return self.scan_file(path)
        elif p.is_dir():
            return self.scan_directory(path, max_files)
        return ScanResult(file_path=path, smells=[])

    def scan_file(self, file_path: str) -> ScanResult:
        """Scan a single file."""
        return scan_file(file_path, self.config)

    def scan_directory(self, directory: str, max_files: int = 50) -> DirectoryScanResult:
        """Scan a directory."""
        return scan_directory(directory, max_files, self.config)

    def format_output(self, result: ScanResult) -> str:
        """Format scan result using theme."""
        return format_output(result, self.theme, arch_locked=self.is_arch_locked())

    def format_table(self, result: ScanResult) -> str:
        """Format smells as table using theme."""
        return format_smell_table(result.smells, self.theme)

    @staticmethod
    def is_arch_locked() -> bool:
        """Check if architecture lock is enabled."""
        return ARCH_LOCK_FILE.exists()

    @staticmethod
    def set_arch_lock(enabled: bool) -> None:
        """Enable or disable architecture lock."""
        if enabled:
            ARCH_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
            ARCH_LOCK_FILE.touch()
        elif ARCH_LOCK_FILE.exists():
            ARCH_LOCK_FILE.unlink()

    @classmethod
    def init_config(cls, path: Optional[str] = None) -> Path:
        """Initialize config directory with default files."""
        return init_config_dir(Path(path) if path else None)

    # Quick class methods for one-off usage
    @classmethod
    def quick_scan(cls, path: str) -> ScanResult | DirectoryScanResult:
        """Quick scan with default config."""
        return cls().scan(path)

    @classmethod
    def quick_scan_file(cls, file_path: str) -> ScanResult:
        """Quick file scan with default config."""
        return cls().scan_file(file_path)

    @classmethod
    def quick_scan_directory(cls, directory: str, max_files: int = 50) -> DirectoryScanResult:
        """Quick directory scan with default config."""
        return cls().scan_directory(directory, max_files)

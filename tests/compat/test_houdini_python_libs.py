"""Tests for Houdini Python library compatibility folders."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
from pathlib import Path

# =============================================================================
# GLOBALS
# =============================================================================

ROOT = Path(__file__).resolve().parents[2]
HOUDINI_ROOT = ROOT / "houdini"


# =============================================================================
# TESTS
# =============================================================================


def test_houdini_21_python311libs_folder_exists():
    """Test that Houdini 21 can discover Python 3.11 startup modules."""
    assert (HOUDINI_ROOT / "python3.11libs").is_dir()


def test_python311libs_matches_python39libs_startup_modules():
    """Test that Python 3.11 receives the same startup hooks as Python 3.9."""
    python39_files = sorted(
        path.relative_to(HOUDINI_ROOT / "python3.9libs")
        for path in (HOUDINI_ROOT / "python3.9libs").glob("*.py")
    )
    python311_files = sorted(
        path.relative_to(HOUDINI_ROOT / "python3.11libs")
        for path in (HOUDINI_ROOT / "python3.11libs").glob("*.py")
    )

    assert python311_files == python39_files

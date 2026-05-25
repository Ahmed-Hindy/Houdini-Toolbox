"""Tests for package metadata related to supported Houdini versions."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import ast
from pathlib import Path

# =============================================================================
# GLOBALS
# =============================================================================

ROOT = Path(__file__).resolve().parents[2]


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _read_assignment(name):
    """Read a top-level assignment from package.py without importing Rez code."""
    module = ast.parse((ROOT / "package.py").read_text(encoding="utf-8"))

    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)

    raise AssertionError(f"Could not find assignment: {name}")


# =============================================================================
# TESTS
# =============================================================================


def test_houdini_21_variant_is_declared():
    """Test that the Rez package advertises Houdini 21.0 support."""
    variants = _read_assignment("variants")

    assert ["houdini-21.0"] in variants


def test_qt_build_dependencies_allow_houdini_21_qt6():
    """Test that Qt6 build tooling can be resolved for Houdini 21."""
    build_requires = _read_assignment("build_requires")

    assert "PySide6" in build_requires


def test_icon_build_can_use_pyside6_resource_compiler():
    """Test that Qt resource generation can target Qt6 builds."""
    cmake_text = (ROOT / "icons" / "CMakeLists.txt").read_text(encoding="utf-8")

    assert "REZ_HOUDINI_VERSION" in cmake_text
    assert 'set(HT_QT_BINDING "PySide6")' in cmake_text
    assert 'set(HT_QT_BINDING "PySide2")' in cmake_text
    assert "pyside6-rcc" in cmake_text
    assert "pyside2-rcc" in cmake_text
    assert "pyrcc5" in cmake_text
    assert "pyrcc6" in cmake_text
    assert "pyside6-rcc pyside2-rcc" not in cmake_text

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


def test_houdini_21_variant_has_pyside2_requirement():
    """Test that the Rez package advertises Houdini 21.0 with its Qt binding."""
    variants = _read_assignment("variants")

    assert ["houdini-21.0", "PySide2"] in variants


def test_pyside_requirements_are_variant_specific():
    """Test that PySide requirements are not global build requirements."""
    build_requires = _read_assignment("build_requires")
    variants = _read_assignment("variants")

    assert "PySide2" not in build_requires
    assert "PySide6" not in build_requires
    assert all(any(req.startswith("PySide") for req in variant) for variant in variants)


def test_icon_build_supports_all_qt_resource_compilers():
    """Test that Qt resource generation can target supported bindings."""
    cmake_text = (ROOT / "icons" / "CMakeLists.txt").read_text(encoding="utf-8")

    assert "REZ_HOUDINI_VERSION" in cmake_text
    assert 'set(HT_QT_BINDING "PySide2")' in cmake_text
    assert "pyside6-rcc" in cmake_text
    assert "pyside2-rcc" in cmake_text
    assert "pyrcc5" in cmake_text
    assert "pyrcc6" in cmake_text
    assert "pyside6-rcc pyside2-rcc" not in cmake_text

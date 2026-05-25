"""Tests for the Qt compatibility layer."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import builtins
import importlib
import sys
import types
from pathlib import Path

# Third Party
import pytest

# =============================================================================
# GLOBALS
# =============================================================================

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = str(ROOT / "python")
QT_BINDINGS = ("PySide2", "PySide6", "PyQt5", "PyQt6")


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(autouse=True)
def python_path(monkeypatch):
    """Make the repository package importable."""
    monkeypatch.syspath_prepend(PYTHON_ROOT)


@pytest.fixture
def isolated_qt_imports(monkeypatch):
    """Block real Qt bindings so tests only see explicitly installed fakes."""
    for name in list(sys.modules):
        if name == "houdini_toolbox.ui.qt" or name.startswith(QT_BINDINGS):
            monkeypatch.delitem(sys.modules, name, raising=False)

    real_import = builtins.__import__

    def _import(name, globals=None, locals=None, fromlist=(), level=0):
        root_name = name.split(".", 1)[0]

        if root_name in QT_BINDINGS and root_name not in sys.modules:
            raise ImportError(root_name)

        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _import)


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _install_binding(monkeypatch, name):
    """Install a fake Qt binding package into sys.modules."""
    package = types.ModuleType(name)
    qt_core = types.ModuleType(f"{name}.QtCore")
    qt_gui = types.ModuleType(f"{name}.QtGui")
    qt_widgets = types.ModuleType(f"{name}.QtWidgets")

    if name.startswith("PySide"):
        qt_core.Signal = object()
        qt_core.Slot = object()
        qt_core.Property = object()

    else:
        qt_core.pyqtSignal = object()
        qt_core.pyqtSlot = object()
        qt_core.pyqtProperty = object()

    package.QtCore = qt_core
    package.QtGui = qt_gui
    package.QtWidgets = qt_widgets

    monkeypatch.setitem(sys.modules, name, package)
    monkeypatch.setitem(sys.modules, f"{name}.QtCore", qt_core)
    monkeypatch.setitem(sys.modules, f"{name}.QtGui", qt_gui)
    monkeypatch.setitem(sys.modules, f"{name}.QtWidgets", qt_widgets)

    return package


def _import_qt():
    """Import a fresh copy of the compatibility layer."""
    sys.modules.pop("houdini_toolbox.ui.qt", None)
    return importlib.import_module("houdini_toolbox.ui.qt")


# =============================================================================
# TESTS
# =============================================================================


def test_prefers_pyside2_for_houdini_21_0_631(monkeypatch, isolated_qt_imports):
    """Test that the default binding order matches Houdini 21.0.631."""
    binding = _install_binding(monkeypatch, "PySide2")
    _install_binding(monkeypatch, "PySide6")

    qt = _import_qt()

    assert qt.QT_BINDING == "PySide2"
    assert qt.QtCore is binding.QtCore
    assert qt.QtGui is binding.QtGui
    assert qt.QtWidgets is binding.QtWidgets
    assert qt.Signal is binding.QtCore.Signal
    assert qt.Slot is binding.QtCore.Slot
    assert qt.Property is binding.QtCore.Property


def test_falls_back_to_pyside6(monkeypatch, isolated_qt_imports):
    """Test compatibility with future Houdini Qt6/PySide6 builds."""
    binding = _install_binding(monkeypatch, "PySide6")

    qt = _import_qt()

    assert qt.QT_BINDING == "PySide6"
    assert qt.QtCore is binding.QtCore
    assert qt.QtGui is binding.QtGui
    assert qt.QtWidgets is binding.QtWidgets
    assert qt.Signal is binding.QtCore.Signal
    assert qt.Slot is binding.QtCore.Slot
    assert qt.Property is binding.QtCore.Property


def test_pyqt6_aliases_signal_slot_and_property(monkeypatch, isolated_qt_imports):
    """Test that PyQt6 names are normalized to the PySide-style API."""
    monkeypatch.setenv("HOUDINI_TOOLBOX_QT_BINDING", "PyQt6")
    binding = _install_binding(monkeypatch, "PyQt6")

    qt = _import_qt()

    assert qt.QT_BINDING == "PyQt6"
    assert qt.QtCore.Signal is binding.QtCore.pyqtSignal
    assert qt.QtCore.Slot is binding.QtCore.pyqtSlot
    assert qt.QtCore.Property is binding.QtCore.pyqtProperty
    assert qt.Signal is binding.QtCore.pyqtSignal
    assert qt.Slot is binding.QtCore.pyqtSlot
    assert qt.Property is binding.QtCore.pyqtProperty


def test_pyqt5_aliases_signal_slot_and_property(monkeypatch, isolated_qt_imports):
    """Test that PyQt5 can be selected explicitly."""
    monkeypatch.setenv("HOUDINI_TOOLBOX_QT_BINDING", "PyQt5")
    binding = _install_binding(monkeypatch, "PyQt5")

    qt = _import_qt()

    assert qt.QT_BINDING == "PyQt5"
    assert qt.QtCore.Signal is binding.QtCore.pyqtSignal
    assert qt.QtCore.Slot is binding.QtCore.pyqtSlot
    assert qt.QtCore.Property is binding.QtCore.pyqtProperty
    assert qt.Signal is binding.QtCore.pyqtSignal
    assert qt.Slot is binding.QtCore.pyqtSlot
    assert qt.Property is binding.QtCore.pyqtProperty


def test_environment_override_wins(monkeypatch, isolated_qt_imports):
    """Test that an explicit binding override takes precedence."""
    monkeypatch.setenv("HOUDINI_TOOLBOX_QT_BINDING", "PyQt5")
    _install_binding(monkeypatch, "PySide2")
    binding = _install_binding(monkeypatch, "PyQt5")

    qt = _import_qt()

    assert qt.QT_BINDING == "PyQt5"
    assert qt.QtCore is binding.QtCore


def test_invalid_environment_override_fails_fast(monkeypatch, isolated_qt_imports):
    """Test that unsupported binding names are reported directly."""
    monkeypatch.setenv("HOUDINI_TOOLBOX_QT_BINDING", "QtMagic")

    with pytest.raises(ImportError, match="Unsupported Qt binding"):
        _import_qt()


def test_missing_bindings_fail_with_actionable_error(isolated_qt_imports):
    """Test the error when no supported Qt binding can be imported."""
    with pytest.raises(ImportError, match="No supported Qt binding found"):
        _import_qt()


def test_ui_modules_use_compatibility_layer():
    """Test that UI modules do not import a concrete Qt binding directly."""
    ui_root = ROOT / "python" / "houdini_toolbox" / "ui"

    for path in ui_root.rglob("*.py"):
        if path.name == "qt.py":
            continue

        text = path.read_text(encoding="utf-8")

        assert "from PySide2 import" not in text
        assert "from PySide6 import" not in text
        assert "from PyQt5 import" not in text
        assert "from PyQt6 import" not in text

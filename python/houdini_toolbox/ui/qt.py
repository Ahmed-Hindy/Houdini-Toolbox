"""Qt binding compatibility helpers.

The toolbox normally runs inside Houdini, so the first choice should be the Qt
binding shipped with that Houdini build. Houdini 21.0.631 ships Python 3.11 with
Qt5/PySide2, so Qt5 bindings are the conservative defaults. Qt6 bindings are
kept as fallback options for standalone tooling and future builds.
"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import os
from typing import Any, Optional, Tuple

# =============================================================================
# GLOBALS
# =============================================================================

SUPPORTED_BINDINGS = ("PySide2", "PyQt5", "PySide6", "PyQt6")

QT_BINDING = ""
QtCore: Any = None
QtGui: Any = None
QtWidgets: Any = None
Signal: Any = None
Slot: Any = None
Property: Any = None


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _binding_order() -> Tuple[str, ...]:
    """Get the Qt binding resolution order.

    Returns:
        The binding names to try.

    Raises:
        ImportError: If an explicit environment override is not supported.

    """
    binding_override = os.environ.get("HOUDINI_TOOLBOX_QT_BINDING")

    if binding_override:
        if binding_override not in SUPPORTED_BINDINGS:
            raise ImportError(
                "Unsupported Qt binding "
                f"'{binding_override}'. Expected one of: "
                f"{', '.join(SUPPORTED_BINDINGS)}"
            )

        return (binding_override,)

    return SUPPORTED_BINDINGS


def _apply_pyqt_aliases(qt_core: Any) -> Tuple[Any, Any, Any]:
    """Normalize PyQt signal APIs to PySide-style names.

    Args:
        qt_core: The imported QtCore module.

    Returns:
        Signal, Slot, and Property callables.

    """
    signal = qt_core.pyqtSignal
    slot = qt_core.pyqtSlot
    prop = qt_core.pyqtProperty

    qt_core.Signal = signal
    qt_core.Slot = slot
    qt_core.Property = prop

    return signal, slot, prop


def _set_attr_if_missing(obj: Any, name: str, value: Any) -> None:
    """Set an attribute if it does not already exist."""
    if not hasattr(obj, name):
        setattr(obj, name, value)


def _copy_enum_members(target: Any, enum_type: Optional[Any], names: Tuple[str, ...]) -> None:
    """Copy Qt6 enum members onto their Qt5-style container when possible."""
    if enum_type is None:
        return

    for name in names:
        if hasattr(enum_type, name):
            _set_attr_if_missing(target, name, getattr(enum_type, name))


def _apply_qt6_enum_aliases(qt_core: Any, qt_gui: Any, qt_widgets: Any) -> None:
    """Add common Qt5-style enum aliases for Qt6 bindings.

    The existing UI code was written against PySide2 and uses names such as
    ``QtCore.Qt.DisplayRole``. PyQt6 in particular prefers scoped enum names
    like ``QtCore.Qt.ItemDataRole.DisplayRole``. Adding aliases here keeps the
    call sites readable and preserves the older Houdini behavior.
    """
    qt = qt_core.Qt

    _copy_enum_members(
        qt,
        getattr(qt, "ItemDataRole", None),
        (
            "DisplayRole",
            "DecorationRole",
            "ToolTipRole",
            "FontRole",
            "ForegroundRole",
            "UserRole",
            "CheckStateRole",
        ),
    )
    _copy_enum_members(
        qt,
        getattr(qt, "ItemFlag", None),
        (
            "ItemIsEnabled",
            "ItemIsSelectable",
            "ItemIsDragEnabled",
            "ItemIsUserCheckable",
        ),
    )
    _copy_enum_members(
        qt,
        getattr(qt, "Key", None),
        (
            "Key_C",
            "Key_Delete",
            "Key_E",
            "Key_I",
            "Key_Left",
            "Key_Right",
            "Key_U",
            "Key_Y",
        ),
    )
    _copy_enum_members(
        qt,
        getattr(qt, "ContextMenuPolicy", None),
        ("CustomContextMenu",),
    )
    _copy_enum_members(
        qt,
        getattr(qt, "KeyboardModifier", None),
        ("ControlModifier",),
    )
    _copy_enum_members(
        qt,
        getattr(qt, "AlignmentFlag", None),
        ("AlignVCenter",),
    )
    _copy_enum_members(
        qt,
        getattr(qt, "SortOrder", None),
        ("AscendingOrder",),
    )
    _copy_enum_members(
        qt,
        getattr(qt, "CaseSensitivity", None),
        ("CaseInsensitive",),
    )
    _copy_enum_members(
        qt,
        getattr(qt, "Orientation", None),
        ("Horizontal",),
    )
    _copy_enum_members(
        qt,
        getattr(qt, "DropAction", None),
        ("CopyAction",),
    )

    keyboard_modifier = getattr(qt, "KeyboardModifier", None)
    if keyboard_modifier is not None and hasattr(keyboard_modifier, "ControlModifier"):
        _set_attr_if_missing(qt, "CTRL", keyboard_modifier.ControlModifier)

    _copy_enum_members(
        qt_widgets.QAbstractItemView,
        getattr(qt_widgets.QAbstractItemView, "SelectionMode", None),
        ("SingleSelection", "ExtendedSelection", "MultiSelection"),
    )
    _copy_enum_members(
        qt_widgets.QAbstractItemView,
        getattr(qt_widgets.QAbstractItemView, "SelectionBehavior", None),
        ("SelectRows",),
    )
    _copy_enum_members(
        qt_widgets.QDialogButtonBox,
        getattr(qt_widgets.QDialogButtonBox, "StandardButton", None),
        ("Cancel", "Ok", "Reset"),
    )
    _copy_enum_members(
        qt_widgets.QDialogButtonBox,
        getattr(qt_widgets.QDialogButtonBox, "ButtonRole", None),
        ("AcceptRole", "ResetRole", "HelpRole"),
    )
    _copy_enum_members(
        qt_widgets.QSizePolicy,
        getattr(qt_widgets.QSizePolicy, "Policy", None),
        ("Expanding",),
    )
    _copy_enum_members(
        qt_gui.QKeySequence,
        getattr(qt_gui.QKeySequence, "StandardKey", None),
        ("Delete", "SelectAll"),
    )


def _import_binding(binding_name: str) -> Tuple[Any, Any, Any, Any, Any, Any]:
    """Import a supported Qt binding.

    Args:
        binding_name: The binding package name.

    Returns:
        Imported QtCore, QtGui, QtWidgets, Signal, Slot, and Property objects.

    """
    if binding_name == "PySide6":
        from PySide6 import QtCore as qt_core
        from PySide6 import QtGui as qt_gui
        from PySide6 import QtWidgets as qt_widgets

        signal = qt_core.Signal
        slot = qt_core.Slot
        prop = qt_core.Property

    elif binding_name == "PySide2":
        from PySide2 import QtCore as qt_core
        from PySide2 import QtGui as qt_gui
        from PySide2 import QtWidgets as qt_widgets

        signal = qt_core.Signal
        slot = qt_core.Slot
        prop = qt_core.Property

    elif binding_name == "PyQt6":
        from PyQt6 import QtCore as qt_core
        from PyQt6 import QtGui as qt_gui
        from PyQt6 import QtWidgets as qt_widgets

        signal, slot, prop = _apply_pyqt_aliases(qt_core)

    elif binding_name == "PyQt5":
        from PyQt5 import QtCore as qt_core
        from PyQt5 import QtGui as qt_gui
        from PyQt5 import QtWidgets as qt_widgets

        signal, slot, prop = _apply_pyqt_aliases(qt_core)

    else:
        raise ImportError(f"Unsupported Qt binding '{binding_name}'")

    if binding_name in ("PySide6", "PyQt6") and hasattr(qt_core, "Qt"):
        _apply_qt6_enum_aliases(qt_core, qt_gui, qt_widgets)

    return qt_core, qt_gui, qt_widgets, signal, slot, prop


def _init_binding() -> None:
    """Initialize module globals from the first available Qt binding."""
    global Property, QT_BINDING, QtCore, QtGui, QtWidgets, Signal, Slot  # pylint: disable=global-statement

    import_errors = {}

    for binding_name in _binding_order():
        try:
            (
                QtCore,
                QtGui,
                QtWidgets,
                Signal,
                Slot,
                Property,
            ) = _import_binding(binding_name)

        except ImportError as error:
            import_errors[binding_name] = error

        else:
            QT_BINDING = binding_name
            return

    details = ", ".join(f"{name}: {error}" for name, error in import_errors.items())
    raise ImportError(
        "No supported Qt binding found. Tried: "
        f"{', '.join(_binding_order())}. {details}"
    )


# =============================================================================

_init_binding()

__all__ = [
    "Property",
    "QT_BINDING",
    "QtCore",
    "QtGui",
    "QtWidgets",
    "SUPPORTED_BINDINGS",
    "Signal",
    "Slot",
]

"""Test nodegraph key prompt compatibility across Houdini versions."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import importlib.util
import sys
import types
from pathlib import Path

# Third Party
import pytest


ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = str(ROOT / "python")


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _clear_nodegraph_modules():
    """Remove imported nodegraph modules from the current test process."""
    sys.modules.pop("houdini_toolbox.ui.nodegraph", None)

    ui_package = sys.modules.get("houdini_toolbox.ui")
    if ui_package is not None and hasattr(ui_package, "nodegraph"):
        delattr(ui_package, "nodegraph")


def _install_houdini_modules(monkeypatch, set_key_prompt):
    """Install fake Houdini modules needed by nodegraph imports."""
    class KeyboardEvent:
        """Fake Houdini keyboard event."""

    hou = types.ModuleType("hou")
    hou.undos = types.SimpleNamespace(group=lambda name: None)

    nodegraphdisplay = types.ModuleType("nodegraphdisplay")
    nodegraphdisplay.setKeyPrompt = set_key_prompt

    canvaseventtypes = types.ModuleType("canvaseventtypes")
    canvaseventtypes.KeyboardEvent = KeyboardEvent

    events = types.ModuleType("houdini_toolbox.events")
    events.__path__ = []

    events_manager = types.ModuleType("houdini_toolbox.events.manager")
    events_manager.EVENT_MANAGER = types.SimpleNamespace(run_event=lambda *args: None)

    event_types = types.ModuleType("houdini_toolbox.events.types")
    event_types.KeyboardEvents = types.SimpleNamespace(
        PostPasteEvent="PostPasteEvent"
    )

    monkeypatch.setitem(sys.modules, "hou", hou)
    monkeypatch.setitem(sys.modules, "nodegraphutils", types.ModuleType("nodegraphutils"))
    monkeypatch.setitem(sys.modules, "nodegraphdisplay", nodegraphdisplay)
    monkeypatch.setitem(sys.modules, "canvaseventtypes", canvaseventtypes)
    monkeypatch.setitem(sys.modules, "houdini_toolbox.events", events)
    monkeypatch.setitem(sys.modules, "houdini_toolbox.events.manager", events_manager)
    monkeypatch.setitem(sys.modules, "houdini_toolbox.events.types", event_types)

    return KeyboardEvent


def _import_nodegraph(monkeypatch, set_key_prompt):
    """Import nodegraph with fake Houdini modules installed."""
    _install_houdini_modules(monkeypatch, set_key_prompt)
    monkeypatch.syspath_prepend(PYTHON_ROOT)
    _clear_nodegraph_modules()

    import houdini_toolbox.ui.nodegraph as nodegraph

    return nodegraph


def _load_nodegraphhooks(path):
    """Load a nodegraphhooks module from a Houdini library path."""
    spec = importlib.util.spec_from_file_location(f"nodegraphhooks_{path.parent.name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# =============================================================================
# TESTS
# =============================================================================


@pytest.fixture(autouse=True)
def clean_nodegraph_imports():
    """Clear fake nodegraph imports between tests."""
    _clear_nodegraph_modules()
    yield
    _clear_nodegraph_modules()


def test_match_key_prompt_uses_four_argument_signature(monkeypatch):
    """Test older Houdini setKeyPrompt signatures that include event type."""
    calls = []

    def set_key_prompt(*args):
        calls.append(args)
        return True

    nodegraph = _import_nodegraph(monkeypatch, set_key_prompt)

    assert nodegraph.match_key_prompt("editor", "key", "h.paste", "keyhit") is True
    assert calls == [("editor", "key", "h.paste", "keyhit")]


def test_match_key_prompt_falls_back_to_houdini_21_signature(monkeypatch):
    """Test Houdini 21.0.631 setKeyPrompt signatures without event type."""
    calls = []

    def set_key_prompt(*args):
        calls.append(args)

        if len(args) == 4:
            raise TypeError("setKeyPrompt() takes 3 positional arguments but 4 were given")

        return True

    nodegraph = _import_nodegraph(monkeypatch, set_key_prompt)

    assert nodegraph.match_key_prompt("editor", "key", "h.paste", "keyhit") is True
    assert calls == [
        ("editor", "key", "h.paste", "keyhit"),
        ("editor", "key", "h.paste"),
    ]


def test_match_key_prompt_reraises_unrelated_type_errors(monkeypatch):
    """Test that real TypeError failures are not hidden."""
    calls = []

    def set_key_prompt(*args):
        calls.append(args)
        raise TypeError("internal prompt error")

    nodegraph = _import_nodegraph(monkeypatch, set_key_prompt)

    with pytest.raises(TypeError, match="internal prompt error"):
        nodegraph.match_key_prompt("editor", "key", "h.paste", "keyhit")

    assert calls == [("editor", "key", "h.paste", "keyhit")]


@pytest.mark.parametrize(
    "hook_path",
    [
        ROOT / "houdini" / "python3.9libs" / "nodegraphhooks.py",
        ROOT / "houdini" / "python3.11libs" / "nodegraphhooks.py",
    ],
)
def test_nodegraphhooks_use_compatible_key_prompt_helper(monkeypatch, hook_path):
    """Test that hooks avoid direct setKeyPrompt calls."""
    calls = []

    def set_key_prompt(*args):
        calls.append(args)
        return False

    KeyboardEvent = _install_houdini_modules(monkeypatch, set_key_prompt)
    monkeypatch.syspath_prepend(PYTHON_ROOT)
    _clear_nodegraph_modules()

    import houdini_toolbox.ui.nodegraph as nodegraph

    paste = types.ModuleType("houdini_toolbox.ui.paste")
    paste.copy_items_from_graph = lambda editor: (None, True)
    paste.paste_items_to_graph = lambda eventtype, editor, uievent: (None, True)
    monkeypatch.setitem(sys.modules, "houdini_toolbox.ui.paste", paste)

    hook_calls = []

    def match_key_prompt(editor, key, prompt, eventtype):
        hook_calls.append((editor, key, prompt, eventtype))
        return False

    monkeypatch.setattr(nodegraph, "match_key_prompt", match_key_prompt)
    monkeypatch.setattr(nodegraph, "is_houdini_paste_event", lambda uievent: False)

    hooks = _load_nodegraphhooks(hook_path)

    event = KeyboardEvent()
    event.editor = "editor"
    event.eventtype = "keyhit"
    event.key = "key"

    assert hooks.createEventHandler(event, []) == (None, False)
    assert hook_calls == [
        ("editor", "key", "h.tool:copy_items", "keyhit"),
        ("editor", "key", "h.tool:paste_items", "keyhit"),
    ]
    assert calls == []

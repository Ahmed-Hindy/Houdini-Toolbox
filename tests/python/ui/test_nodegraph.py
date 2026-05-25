"""Test the houdini_toolbox.ui.nodegraph module."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Third Party
import pytest

# Houdini Toolbox
import houdini_toolbox.ui.nodegraph

# Houdini
from canvaseventtypes import KeyboardEvent

# ==============================================================================
# TESTS
# ==============================================================================


class Test_handle_houdini_paste_event:
    """Test houdini_toolbox.ui.nodegraph.handle_houdini_paste_event."""

    def test_menukeyhit(self, mocker):
        """Test when the eventtype is "menukeyhit"."""
        mock_undos = mocker.patch("hou.undos.group")

        mock_editor = mocker.MagicMock()

        mock_event = mocker.MagicMock(spec=KeyboardEvent)
        mock_event.editor = mock_editor
        mock_event.eventtype = "menukeyhit"

        mock_paste = mocker.patch("nodegraphutils.pasteItems")
        mock_move = mocker.patch("nodegraphutils.moveItemsToLocation")
        mock_update = mocker.patch("nodegraphutils.updateCurrentItem")

        mock_run_event = mocker.patch(
            "houdini_toolbox.ui.nodegraph.EVENT_MANAGER.run_event"
        )

        result = houdini_toolbox.ui.nodegraph.handle_houdini_paste_event(mock_event)

        assert result == (None, True)

        mock_undos.assert_called_with("Paste from clipboard")

        mock_paste.assert_called_with(mock_editor)

        mock_editor.posFromScreen.assert_called_with(
            mock_editor.screenBounds().center()
        )

        mock_move.assert_called_with(
            mock_editor,
            mock_editor.posFromScreen(),
            mock_editor.screenBounds().center(),
        )
        mock_update.assert_called_with(mock_editor)

        scriptargs = {"items": mock_editor.pwd().selectedItems(), "uievent": mock_event}
        mock_run_event.assert_called_with(
            houdini_toolbox.ui.nodegraph.KeyboardEvents.PostPasteEvent, scriptargs
        )

    def test_keyhit(self, mocker):
        """Test when the eventtype is "keyhit"."""
        mock_undos = mocker.patch("hou.undos.group")

        mock_editor = mocker.MagicMock()

        mock_event = mocker.MagicMock(spec=KeyboardEvent)
        mock_event.editor = mock_editor

        mock_paste = mocker.patch("nodegraphutils.pasteItems")
        mock_move = mocker.patch("nodegraphutils.moveItemsToLocation")
        mock_update = mocker.patch("nodegraphutils.updateCurrentItem")

        mock_run_event = mocker.patch(
            "houdini_toolbox.ui.nodegraph.EVENT_MANAGER.run_event"
        )

        result = houdini_toolbox.ui.nodegraph.handle_houdini_paste_event(mock_event)

        assert result == (None, True)

        mock_undos.assert_called_with("Paste from clipboard")

        mock_paste.assert_called_with(mock_editor)

        mock_editor.posFromScreen.assert_called_with(mock_event.mousepos)

        mock_move.assert_called_with(
            mock_editor, mock_editor.posFromScreen(), mock_event.mousepos
        )
        mock_update.assert_called_with(mock_editor)

        scriptargs = {"items": mock_editor.pwd().selectedItems(), "uievent": mock_event}
        mock_run_event.assert_called_with(
            houdini_toolbox.ui.nodegraph.KeyboardEvents.PostPasteEvent, scriptargs
        )

    def test_parentkeyhit(self, mocker):
        """Test when the eventtype is "parentkeyhit"."""
        mock_undos = mocker.patch("hou.undos.group")

        mock_editor = mocker.MagicMock()

        mock_event = mocker.MagicMock(spec=KeyboardEvent)
        mock_event.editor = mock_editor
        mock_event.eventtype = "parentkeyhit"

        mock_paste = mocker.patch("nodegraphutils.pasteItems")
        mock_move = mocker.patch("nodegraphutils.moveItemsToLocation")
        mock_update = mocker.patch("nodegraphutils.updateCurrentItem")

        mock_run_event = mocker.patch(
            "houdini_toolbox.ui.nodegraph.EVENT_MANAGER.run_event"
        )

        result = houdini_toolbox.ui.nodegraph.handle_houdini_paste_event(mock_event)

        assert result == (None, True)

        mock_undos.assert_called_with("Paste from clipboard")

        mock_paste.assert_called_with(mock_editor)

        mock_move.assert_not_called()
        mock_update.assert_called_with(mock_editor)

        scriptargs = {"items": mock_editor.pwd().selectedItems(), "uievent": mock_event}
        mock_run_event.assert_called_with(
            houdini_toolbox.ui.nodegraph.KeyboardEvents.PostPasteEvent, scriptargs
        )


def test_is_houdini_paste_event(mocker):
    """Test houdini_toolbox.ui.nodegraph.is_houdini_paste_event."""
    mock_event = mocker.MagicMock()
    mock_match = mocker.patch("houdini_toolbox.ui.nodegraph.match_key_prompt")

    result = houdini_toolbox.ui.nodegraph.is_houdini_paste_event(mock_event)

    assert result == mock_match.return_value

    mock_match.assert_called_with(
        mock_event.editor, mock_event.key, "h.paste", mock_event.eventtype
    )


def test_match_key_prompt_uses_eventtype_when_supported(mocker):
    """Test matching a key prompt with the older four-argument API."""
    mock_set = mocker.patch(
        "houdini_toolbox.ui.nodegraph.setKeyPrompt", return_value=True
    )

    result = houdini_toolbox.ui.nodegraph.match_key_prompt(
        "editor", "key", "h.paste", "keyhit"
    )

    assert result is True
    mock_set.assert_called_once_with("editor", "key", "h.paste", "keyhit")


def test_match_key_prompt_falls_back_to_houdini_21_signature(mocker):
    """Test matching a key prompt with Houdini 21.0.631's three-argument API."""
    mock_set = mocker.patch(
        "houdini_toolbox.ui.nodegraph.setKeyPrompt",
        side_effect=(TypeError("setKeyPrompt() takes 3 positional arguments"), True),
    )

    result = houdini_toolbox.ui.nodegraph.match_key_prompt(
        "editor", "key", "h.paste", "keyhit"
    )

    assert result is True
    mock_set.assert_has_calls(
        [
            mocker.call("editor", "key", "h.paste", "keyhit"),
            mocker.call("editor", "key", "h.paste"),
        ]
    )


def test_match_key_prompt_reraises_other_type_errors(mocker):
    """Test that unrelated TypeError exceptions are not hidden."""
    mock_set = mocker.patch(
        "houdini_toolbox.ui.nodegraph.setKeyPrompt",
        side_effect=TypeError("internal prompt error"),
    )

    with pytest.raises(TypeError, match="internal prompt error"):
        houdini_toolbox.ui.nodegraph.match_key_prompt(
            "editor", "key", "h.paste", "keyhit"
        )

    mock_set.assert_called_once_with("editor", "key", "h.paste", "keyhit")

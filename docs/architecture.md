# Architecture

Houdini Toolbox is organized as a Houdini package payload plus a Python library
and optional compiled plugins.

## Loading Flow

The Houdini package file `houdini-toolbox.json` is the package-entry path for a
non-Rez setup. It adds:

- `houdini/` to Houdini's package path
- `python/` to `PYTHONPATH`

When Houdini starts, files under `houdini/` are discovered using standard
Houdini conventions.

Important startup files include:

- `houdini/python3.9libs/pythonrc.py`
- `houdini/scripts/456.py`
- `houdini/scripts/beforescenesave.py`
- `houdini/scripts/afterscenesave.py`
- node event scripts under `houdini/scripts/On*.py`

`pythonrc.py` initializes logging, imports event/style/AOV packages, and
registers dynamic callbacks.

## Python Package

The main package lives under `python/houdini_toolbox/`.

Major modules:

- `events`: central event registration and dispatch.
- `geometry`: geometry helper classes.
- `inline`: helpers for Houdini `inlinecpp` and HOM/HDK bridge code.
- `logging`: Houdini-aware logging handlers and adapters.
- `nodes`: node badges, parameter queries, helpcard generation, and styling.
- `pyfilter`: Mantra PyFilter manager and operations.
- `sohohooks`: SOHO hook dispatch and automatic AOV generation.
- `ui`: PySide2 UI for AOVs, copy/paste, menus, and network graph behavior.

## Houdini Payload

The `houdini/` folder contains the files Houdini discovers at runtime.

Key subfolders and files:

- `config/aovs`: JSON AOV definitions.
- `config/styles`: JSON node style rules.
- `config/NodeShapes`: custom node shape JSON files.
- `help/aov_manager`: Houdini help pages for the AOV UI.
- `otls`: digital assets and expanded HDA content.
- `pyfilter`: Mantra PyFilter entry point and operation registry.
- `python_panels`: Python panel definitions.
- `python3.9libs`: Houdini startup and nodegraph hook modules.
- `scripts`: scene and node lifecycle script hooks.
- `soho`: SOHO hook and parameter definition files.
- `toolbar`: shelf tool definitions.
- `OPmenu.xml`, `PARMmenu.xml`, `NetworkViewMenu.xml`, `MainMenuCommon.xml`:
  menu integration files.

## Render-Time Systems

There are two render-time systems.

### SOHO / IFD Hooks

`houdini/soho/IFDuserhooks.py` forwards hook calls into
`houdini_toolbox.sohohooks.manager.HOOK_MANAGER`.

The AOV manager uses this path to create image plane definitions while Mantra is
generating IFD data.

### PyFilter

`houdini/pyfilter/ht-pyfilter.py` is a Mantra PyFilter script. Mantra loads it
with the `-P` option. The script creates a `PyFilterManager`, which loads
operation classes from `pyfilter/operations.json`.

Operations implement stage methods such as:

- `filter_camera`
- `filter_instance`
- `filter_material`
- `filter_plane`
- `filter_render`
- `filter_end_render`
- `filter_quit`

The manager runs any operation that reports it should run for the current
render and parsed command-line arguments.

## AOV Data Model

Automatic AOVs are represented by:

- `AOV`
- `AOVGroup`
- `IntrinsicAOVGroup`
- `AOVFile`
- `AOVManager`

Definitions are loaded from JSON files found either through `HT_AOV_PATH` or
`config/aovs` folders on `HOUDINI_PATH`.

AOV group references are represented with `@group_name` syntax. Commas and
spaces are both accepted as separators.

## UI Systems

The UI layer uses PySide2 through Houdini's Qt environment.

The AOV Manager UI follows a model/view split:

- `ui/aovs/models.py`
- `ui/aovs/widgets.py`
- `ui/aovs/dialogs.py`
- `ui/aovs/utils.py`

The copy/paste UI stores reusable network item snippets through source objects.
The default source stores `.cpio` payloads and JSON sidecars in `~/copypaste`.

## Plugin Build Architecture

The root `CMakeLists.txt` installs the Python and Houdini payload, compiles Qt
resources, processes HDAs, and enters the `plugins/` build.

`plugins/CMakeLists.txt` locates Houdini through `$HFS/toolkit/cmake`, imports
Houdini's CMake target, and builds:

- OPUI badge plugins
- SOP plugins
- the Script ROP
- Python extension modules used by badge helpers

Rez install rules then place built Houdini payloads and Python outputs into the
package.

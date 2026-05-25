# Development Notes

This repository is designed for Houdini-aware development. Many tests and build
steps expect Houdini's Python interpreter, libraries, headers, and runtime
environment.

## Python Style

Project configuration lives in `pyproject.toml`.

Configured tools include:

- pytest
- coverage
- isort
- mypy
- pylint

The import sorter has a large list of Houdini modules so imports can be grouped
separately from third-party and first-party package imports.

## Running Tests

The Rez package defines the unit test command as:

```shell
coverage erase && hython -m pytest tests
```

The test environment sets `HOUDINI_TOOLBOX_TESTING` to avoid loading the full
`HOUDINI_PATH` payload during coverage runs. For unit tests it also prepends:

- `houdini/dso` to `HOUDINI_DSO_PATH`
- `houdini/otls` to `HOUDINI_OTLSCAN_PATH`
- `houdini/toolbar` to `TOOLBAR_PATH`

## Local Python Dependencies

Runtime Python dependencies are listed in `requirements.txt`:

```text
Jinja2
numpy
scipy
```

Test dependencies are listed in `test-requirements.txt`:

```text
pytest
pytest-cov
pytest-mock
```

Use a project-local environment for non-Houdini helper work. Houdini-specific
tests should run under `hython` so `hou`, SOHO modules, HDK extension modules,
and Houdini paths are available.

## Building Plugins

The HDK plugins use CMake. The Houdini installation must be discoverable through
`$HFS`, and CMake appends `$HFS/toolkit/cmake` to `CMAKE_PREFIX_PATH`.

The plugin build includes:

- `OPUI/OPUI_GenericImageBadge`
- `OPUI/OPUI_GenericTextBadge`
- `ROP/ROP_Script`
- `SOP/SOP_DopImpactPoints`
- `SOP/SOP_PointsFromVoxels`
- `SOP/SOP_PrimCentroid`
- `SOP/SOP_PrimGroupCentroid`
- `PY/PY_generic_image_badge`
- `PY/PY_generic_text_badge`

## Editing HDAs

At least one asset is stored expanded in version control:

- `houdini/otls/Sop-cppwrangle.1.otl`

The root build processes expanded assets and collapses them for installation.
Avoid editing generated/collapsed output when the expanded source is the
authoritative representation.

## Compatibility Work

Areas most likely to need attention when moving to newer Houdini versions:

- PySide2 API usage
- `houdini/python3.9libs` path assumptions
- Mantra, SOHO, IFD, and PyFilter behavior
- HDK API changes for compiled SOP/ROP/OPUI plugins
- CMake/Houdini toolkit changes
- package variants in `package.py`

For Houdini 21.0 support, start by adding an explicit Rez variant, then test
package loading, Python startup, AOV Manager UI creation, SOHO/PyFilter render
paths, and HDK plugin compilation.

## Useful Validation Checklist

After making changes, validate the area touched:

- Python-only code: run focused `hython -m pytest` tests.
- Houdini menus or shelf tools: launch Houdini and confirm menu/tool discovery.
- AOV Manager: open the Python panel and apply AOVs to a Mantra ROP.
- PyFilter: render to `ip` with overrides enabled.
- SOHO hooks: generate an IFD and confirm automatic planes are written.
- HDK plugins: rebuild with Houdini's toolkit and create each operator in a test
  scene.
- Nodegraph hooks: verify copy/paste hotkeys and standard Houdini paste behavior.

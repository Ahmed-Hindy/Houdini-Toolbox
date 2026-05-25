# Installation and Loading

Houdini Toolbox can be loaded either as a Houdini package or through the Rez
package definition.

## Houdini Package Loading

The simplest loading path is Houdini Packages.

1. Put or clone this repository somewhere stable.
2. Add that folder to `HOUDINI_PACKAGE_DIR`.
3. Start Houdini.

Houdini reads `houdini-toolbox.json`, which adds:

- `${HOUDINI_PACKAGE_PATH}/houdini` to Houdini's package search path
- `${HOUDINI_PACKAGE_PATH}/python` to `PYTHONPATH`

This loads the Python package, Houdini menus, scripts, panels, config files,
SOHO hooks, PyFilter files, and installed HDAs.

## Rez Package Loading

The repository also contains `package.py` for Rez. The Rez package:

- depends on `houdini`
- uses CMake as the build system
- uses PySide2 at build time for Qt resource compilation
- prepends `python/` to `PYTHONPATH`
- prepends `houdini/` to `HOUDINI_PATH` outside test runs

The declared variants currently target:

- `houdini-19.5`
- `houdini-20.0`

## Build Outputs

CMake installs the Python files and Houdini payload, compiles Qt resources, folds
expanded HDAs under `houdini/otls`, and builds the HDK plugins under `plugins/`.

Compiled plugin outputs are expected to land in Houdini-compatible locations
under the package payload, such as:

- `houdini/dso`
- `houdini/dso/opui`
- `python/` for Python extension modules

## Runtime Requirements

The Python requirements are listed in `requirements.txt`:

- Jinja2
- numpy
- scipy

Tests additionally use:

- pytest
- pytest-cov
- pytest-mock

## Compatibility Notes

The toolbox contains Mantra, SOHO, IFD, and PyFilter integrations. These are most
relevant to Mantra render workflows. Houdini releases focused on Karma/Solaris
may still load many UI and Python features, but render-specific behavior should
be tested carefully.

The repository also uses PySide2 and Houdini Python 3.9 library paths in places,
which may need updates for newer Houdini versions.

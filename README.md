# Houdini Toolbox

Houdini Toolbox is a collection of Houdini pipeline utilities, UI extensions,
render-time helpers, HDAs, and compiled HDK plugins. It is aimed at Houdini TDs
and technical artists who want reusable tooling for node workflow, Mantra AOVs,
render-time filtering, node styling, and geometry processing.

The repository is not a single tool. It installs several layers into Houdini:

- Python modules under `houdini_toolbox`
- Houdini package files, menus, shelf tools, Python panels, scripts, and config
- Mantra/SOHO hooks and PyFilter operations
- expanded and binary HDAs under `houdini/otls`
- compiled HDK plugins under `plugins`

## Documentation

- [Documentation index](docs/README.md)
- [Installation and loading](docs/installation.md)
- [Feature overview](docs/features.md)
- [Architecture](docs/architecture.md)
- [Development notes](docs/development.md)

## Library Versions

This repository will generally closely follow the [VFX Platform](https://vfxplatform.com/) versions matching the most
recently released version of [Houdini](https://www.sidefx.com/docs/houdini/licenses/index.html).

### Legacy (Python 2.7) Support

Python 2.7 compatible code is still available in the **python2.7** branch.

### Compatibility Notes

The current package variants in `package.py` target Houdini 19.5, Houdini 20.0,
and Houdini 21.0. Some parts of the toolbox are tied to Mantra, SOHO, IFD
generation, and Houdini Qt APIs, so render-specific and UI behavior should be
tested before production use on newer builds.

---

## Installation

This project primarily uses [rez](https://github.com/AcademySoftwareFoundation/rez/) in order to build and package
itself, including compiled HDK plugins and Qt resources.

That said, if you want to use it without those, in order to use most of the features contained in this repo it is
necessary to add/modify certain entries in your environment:
- HOUDINI_PATH
- PYTHONPATH

### Using Houdini Packages

The easiest way to get this working is to use [Houdini Packages](https://www.sidefx.com/docs/houdini/ref/plugins.html).

Simply add the location of this repository to **$HOUDINI_PACKAGE_DIR** in order for Houdini to find the package definition and load it.

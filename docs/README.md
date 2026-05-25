# Houdini Toolbox Documentation

This documentation explains what the repository contains, how Houdini loads it,
and where the main systems live in the source tree.

## Start Here

- [Installation and loading](installation.md): how the package is discovered by
  Houdini, what Rez/CMake builds, and what environment variables matter.
- [Feature overview](features.md): artist- and TD-facing tools grouped by area.
- [Architecture](architecture.md): how the Python package, Houdini startup
  files, render hooks, UI files, HDAs, and HDK plugins fit together.
- [Development notes](development.md): local testing, formatting, package
  layout, and compatibility cautions.

## Repository Map

| Path | Purpose |
| --- | --- |
| `houdini/` | Houdini package payload: menus, scripts, panels, config, shelf tools, SOHO/PyFilter files, and HDAs. |
| `python/houdini_toolbox/` | Main Python package used by Houdini. |
| `plugins/` | HDK/C++ plugins and CMake build definitions. |
| `icons/` | Qt resource inputs and generated icon assets. |
| `tests/` | pytest tests intended to run under `hython`. |
| `package.py` | Rez package definition. |
| `houdini-toolbox.json` | Houdini package file for package-based loading. |

## High-Level Summary

Houdini Toolbox provides:

- automatic Mantra AOV definition and grouping tools
- a graphical AOV Manager Python panel
- Mantra PyFilter operations for preview/render overrides
- custom SOHO hook dispatch
- nodegraph copy/paste-to-file tools
- custom OP and parameter menu entries
- node style rules and custom node shapes
- generic node text/image badges
- render and scene event registration helpers
- HDK SOP/ROP plugins
- a C++ Wrangle HDA powered by Houdini `inlinecpp`

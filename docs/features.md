# Feature Overview

This page groups the main user-facing features by workflow area.

## AOV Manager

The AOV Manager is a Mantra AOV definition and application system.

Primary files:

- `python/houdini_toolbox/sohohooks/aovs/`
- `python/houdini_toolbox/ui/aovs/`
- `houdini/config/aovs/`
- `houdini/python_panels/aov_manager.pypanel`
- `houdini/help/aov_manager/`

The system reads AOV and group definitions from JSON files. AOV definitions can
specify fields such as:

- VEX variable
- VEX type
- output channel
- quantization
- sample filter
- pixel filter
- component export
- light export mode
- custom plane file
- comments and grouping metadata

Groups can include named AOVs and are referenced with `@group_name` syntax.
Intrinsic groups are generated automatically from AOV intrinsic tags.

The UI lets users create, edit, inspect, drag, install, uninstall, and apply AOVs
or groups. It can apply AOVs at render time through the Automatic AOV parameter,
or bake them into the Mantra ROP's Extra Image Planes multiparm.

## SOHO and IFD Hooks

Primary files:

- `houdini/soho/IFDuserhooks.py`
- `python/houdini_toolbox/sohohooks/manager.py`
- `python/houdini_toolbox/sohohooks/aovs/`

`IFDuserhooks.py` delegates hook calls to `SohoHookManager`. Registered hooks can
run during IFD generation. The AOV system uses this path to write plane
definitions at render time.

## PyFilter Operations

Primary files:

- `houdini/pyfilter/ht-pyfilter.py`
- `houdini/pyfilter/operations.json`
- `python/houdini_toolbox/pyfilter/`

The PyFilter runner loads operation classes from JSON and dispatches them to
Mantra filter stages, including camera, instance, material, plane, error, and
render lifecycle callbacks.

Included operations support:

- preview render resolution scaling
- pixel sample scaling
- disabling motion blur
- disabling non-primary AOVs
- disabling deep output
- disabling displacement
- disabling subdivision
- disabling tile callbacks
- disabling matte/phantom objects
- overriding bucket size
- setting transparent sample counts
- setting primary image output
- setting deep output behavior
- Z-depth pass helpers
- render log output

## Houdini Menus and Nodegraph Tools

Primary files:

- `houdini/OPmenu.xml`
- `houdini/PARMmenu.xml`
- `houdini/NetworkViewMenu.xml`
- `houdini/MainMenuCommon.xml`
- `houdini/python3.9libs/nodegraphhooks.py`
- `houdini/python3.11libs/nodegraphhooks.py`
- `python/houdini_toolbox/ui/paste/`
- `python/houdini_toolbox/ui/menus/`

The toolbox adds menu entries for:

- creating absolute reference copies
- saving a node/network item to file
- copying selected network items to file
- pasting saved network items from file
- promoting a parameter to another node
- converting node reference paths between absolute and relative forms
- refreshing Houdini menus

The copy/paste system stores `.cpio` files under `~/copypaste` and writes JSON
sidecar metadata containing author, context, date, name, and optional
description.

## Node Styling

Primary files:

- `python/houdini_toolbox/nodes/styles/`
- `houdini/config/styles/gcs.json`
- `houdini/config/NodeShapes/`

The node styling system reads JSON rules and applies node colors and node shapes
based on:

- node type name
- Houdini tool menu category
- node name patterns

This supports consistent visual conventions for network graphs, such as output
nodes, switches, subnets, merges, lights, cameras, and VOP utility nodes.

## Node Badges

Primary files:

- `python/houdini_toolbox/nodes/badges.py`
- `plugins/OPUI/OPUI_GenericImageBadge/`
- `plugins/OPUI/OPUI_GenericTextBadge/`
- `plugins/PY/PY_generic_image_badge/`
- `plugins/PY/PY_generic_text_badge/`

The badge helpers set Houdini node user data that compiled OPUI plugins render
as generic text or image badges in the network editor.

## Event System

Primary files:

- `python/houdini_toolbox/events/`
- `houdini/scripts/`
- `houdini/python3.9libs/pythonrc.py`
- `houdini/python3.11libs/pythonrc.py`

Startup imports initialize logging, register event callbacks, load node styles,
and initialize the AOV manager. Houdini script files then forward scene and node
events to a central event manager.

Supported event groups include:

- scene load/save/exit
- hip file events
- node lifecycle events
- ROP render lifecycle events
- keyboard/post-paste events

The built-in ROP render event group logs render start, frame start, frame write,
frame duration, and render completion.

## HDK Plugins

Primary files:

- `plugins/SOP/SOP_PrimCentroid/`
- `plugins/SOP/SOP_PrimGroupCentroid/`
- `plugins/SOP/SOP_PointsFromVoxels/`
- `plugins/SOP/SOP_DopImpactPoints/`
- `plugins/ROP/ROP_Script/`

The compiled plugins include:

- Primitive Centroid SOP: creates points at primitive centers.
- Primitive Group Centroid SOP: creates points at primitive group centers and
  can transform matching geometry from input points.
- Points From Voxels SOP: creates points at fog-volume voxel centers.
- DOP Impact Points SOP: extracts DOP impact record data as points.
- Script ROP: runs HScript or Python as a render operation.

## HDAs and Inline C++

Primary files:

- `houdini/otls/Sop-cppwrangle.1.otl/`
- `python/houdini_toolbox/inline/`

The C++ Wrangle HDA lets users define C++ functions compiled by Houdini's
`inlinecpp` module and call them from Python in a SOP context.

The inline helper modules provide utilities for:

- converting Python sequences to C arrays
- mapping HOM attribute/group types to HDK enum values
- resolving Houdini objects from returned integer/path data
- working with geometry, groups, attributes, multiparms, bounding boxes, vectors,
  matrices, and digital asset metadata

## Geometry Utilities

Primary files:

- `python/houdini_toolbox/geometry/pointcloud.py`

The `PointCloud` helper wraps `scipy.spatial.KDTree` for nearest-point and
radius searches on Houdini geometry.

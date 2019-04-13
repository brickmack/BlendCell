Blender python script (soon to be addon) for visualization of cellular automata.

Version 0.0

Usage:

Currently only available as a script, must be manually run and parameters are all hard-coded. Cells are represented as cubes, and render visibility is turned off/on depending on whether the cell is live or not (color changing as an alternate representation is in progress). Generates keyframes so it can be rendered as an animation (currently you MUST render it to view, doesn't work in the viewport)

Planned features:

* 2d and 3d versions

* configurable rules (currently uses the standard Conway's Game of Life rules)

* Addon instead of independent script

* multiple boundary handling modes (infinite grid with finite/infinite display, non-crossable boundary, toroidal projection on finite grid). Currently only toroidal projection is supported

* Multiple cell shape options

* Grid lines

* Highlight newly added/killed cells

* Visually set initial state instead of hardcoded array of live cells

* Automatically clear previous board when simulation is re-run

* Parent all cell objects to an empty so the whole thing can be moved around

Known issues:

* Color-based live/dead cell display is halfway implemented (use displayMode = 1), but fails with "property "active_material_index" not animatable". Turns out that doesnt work. Solution known to exist: https://blender.stackexchange.com/questions/132295/insert-keyframe-for-active-material-slot-with-python

* Keyframing is not optimal, adds unneccessary keyframes to cells which have not changed
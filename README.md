# BlendCell

Blender python addon for visualization of cellular automata.

Version 0.1

## Usage:

Currently only available as a script, must be manually run and parameters are all hard-coded. Cells are represented as cubes, and render visibility is turned off/on depending on whether the cell is live or not (color changing as an alternate representation is in progress). Generates keyframes so it can be rendered as an animation (currently you MUST render it to view, doesn't work in the viewport)

## Planned features:

* 2d and 3d versions

* configurable rules (currently uses the standard Conway's Game of Life rules)

* Addon instead of independent script

* multiple boundary handling modes (infinite grid with finite/infinite display, non-crossable boundary, toroidal projection on finite grid). Currently only toroidal projection is supported

* Multiple cell shape options

* Grid lines

* Highlight newly added/killed cells

* Visually set initial state instead of hardcoded array of live cells

* Automatically clear previous board when simulation is re-run

## Known issues:

* Keyframing is not optimal, adds unneccessary keyframes to cells which have not changed

##Changelog:

### 0.1:

* Replaced show/hide alive/dead cells with object info-based material change, consolidated to a single display mode. A single material is shared between live/dead cells and a mix node with fac = pass_index is used to control what it looks like object-by-object. User changes to this material are persistent

* All cells are now parented to an empty object, to allow the grid as a whole to be moved around

### 0.0:

* Initial test release
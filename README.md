# BlendCell

Blender python addon for visualization of cellular automata.

Version 0.2

## Usage:

Currently only available as a script, must be manually run and parameters are all hard-coded. Cells are represented as cubes. Cell aliveness is indicated by object pass_index controlling a mix shader node in a material. Generates keyframes so it can be rendered as an animation (currently you MUST render it to view, doesn't work in the viewport)

## Planned features:

* 2d and 3d versions

* configurable rules (currently uses the standard Conway's Game of Life rules)

* multiple boundary handling modes (infinite grid with finite/infinite display, non-crossable boundary, toroidal projection on finite grid). Currently only toroidal projection is supported

* Multiple cell shape options

* Grid lines

* Highlight newly added/killed cells

* Visually set initial state instead of hardcoded array of live cells

* Automatically clear previous board when simulation is re-run

## Known issues:

* Keyframing is not optimal, adds unneccessary keyframes to cells which have not changed

* Matrix reconstruction in RunSimOP is not optimal. Should store coordinates in custom object properties. Safer, much faster

## Changelog:

### 0.3:

* Fix incorrect variable scope

* Add function to run simulation after grid has been set up

### 0.2:

* Converted to blender addon instead of standalone script

* Demo code for custom properties, separate initialize/run/reset functions, etc

### 0.1:

* Replaced show/hide alive/dead cells with object info-based material change, consolidated to a single display mode. A single material is shared between live/dead cells and a mix node with fac = pass_index is used to control what it looks like object-by-object. User changes to this material are persistent

* All cells are now parented to an empty object, to allow the grid as a whole to be moved around

### 0.0:

* Initial test release
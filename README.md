# BlendCell

Blender python addon for visualization of cellular automata.

Version 0.4

## Usage:

Cells are represented as cubes. Cell aliveness is indicated by object pass_index controlling a mix shader node in a material. Generates keyframes so it can be rendered as an animation (currently you MUST render it to view, doesn't work in the viewport)

Use "Build grid" to generate the board. Select desired live cells, then use "Set cells alive". Then use "Run simulation" and view the results (must render to see board state at time t)

## Planned features:

* 2d and 3d versions

* Configurable rules (currently uses the standard Conway's Game of Life rules)

* Multiple boundary handling modes (infinite grid with finite/infinite display, non-crossable boundary, toroidal projection on finite grid). Currently only toroidal projection is supported

* Grid lines

* Highlight newly added/killed cells

* Blender 2.80 support

* Ability to add certain standard patterns (glider, etc)

* Set starting frame using the timeline, and set location of the overall grid using the 3d cursor

## Known issues:

* Keyframing is not optimal, adds unneccessary keyframes to cells which have not changed

* Matrix reconstruction process is not optimal. Should store coordinates in custom object properties. Safer, much faster

* BuildGrid creates a duplicate for cell 0,0 because of the instancing. User can manually remove this.

## Changelog:

### 0.4:

* Remove deprecated RunSimCombined class

* Number of simulation steps is no longer hard-coded, saved in custom property of the parent object and can be set via slider in RunSim

* Add tool to reset simulation

* Add tool to set selected cells to be alive

* Add tool to add predefined patterns (needs work. Currently only supports gliders, and only at a predefined point)

* Cells are now all instances of a single cell. Vastly faster and uses less memory (on a mid-range laptop, now comfortably supports a 2d grid of 75x75 cells. Previously topped out around 20x20), and allows the user to easily change the mesh of all at once

* General optimizations to BuildGrid now that many functionalities have been moved to other tools

* Refactoring

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
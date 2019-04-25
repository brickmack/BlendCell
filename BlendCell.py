bl_info = {
	"name": "BlendCell",
	"author": "Mackenzie Crawford",
	"version": (0, 4),
	"blender": (2, 79, 0),
	"description": "Visualization tool for cellular automata",
	"warning": "",
	"tracker_url": "",
	"category": "3D View"}

import bpy
import re
import time

def stepForward(Matrix, n, t):
	newMatrix = [[0 for x in range(n)] for y in range(n)] #stores born/live/die = 1/0/-1 for each cell in the next step, NOT a reference to the cells themselves

	for i in range(n):
		for j in range(n):
			#compute 8-neighbor sum using toroidal boundary conditions - x and y wrap around so that the simulaton takes place on a toroidal surface
			total = 0
			if Matrix[i][(j-1)%n].pass_index == 1:
				total = total + 1
			if Matrix[i][(j+1)%n].pass_index == 1:
				total = total + 1
			if Matrix[(i-1)%n][j].pass_index == 1:
				total = total + 1
			if Matrix[(i+1)%n][j].pass_index == 1:
				total = total + 1
			if Matrix[(i-1)%n][(j-1)%n].pass_index == 1:
				total = total + 1
			if Matrix[(i-1)%n][(j+1)%n].pass_index == 1:
				total = total + 1
			if Matrix[(i+1)%n][(j-1)%n].pass_index == 1:
				total = total + 1
			if Matrix[(i+1)%n][(j+1)%n].pass_index == 1:
				total = total + 1
        
			#apply conways rules
			if Matrix[i][j].pass_index == 1:
				if (total < 2) or (total > 3):
					#die
					newMatrix[i][j] = -1
			else:
				if total == 3:
					#birth
					newMatrix[i][j] = 1
			#otherwise, newMatrix[i][j] = 0/continue living

	#now we have the next set of cell states, apply them to the cells themselves
	for i in range(0, n):
		for j in range(0, n):
			if newMatrix[i][j] == 1:
				Matrix[i][j].pass_index = 1
			elif newMatrix[i][j] == -1:
				Matrix[i][j].pass_index = 0

	#set next keyframe for all cells
	keyframeAll(Matrix, n, t)
			
def keyframeAll(Matrix, count, t):
	#set next keyframe for all cells
    for x in range(0, count):
        for y in range(0, count):
            Matrix[x][y].keyframe_insert(data_path="pass_index", frame=t)
			
def rebuildMatrix(children, count):
	#these may be out of order, so we need to place them back in a 2d array with the same structure as the original
	Matrix = [[0 for x in range(count)] for y in range(count)]
	for child in children:
		coords = [int(s) for s in re.findall(r'\d+', child.name)]
		
		Matrix[coords[0]][coords[1]] = child
		
	return Matrix
            
def findMaterial():
    #first check if a BlendCell material is already set
    mat = bpy.data.materials.get("BlendCell material")
    if mat is None:
        #create the material
        return createMaterial()
    
    return mat

def createMaterial():
    mat = bpy.data.materials.new(name="BlendCell material")

    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    #clear all nodes to start clean
    for node in nodes:
        nodes.remove(node)

    #create mix shader node
    node_mix = nodes.new(type='ShaderNodeMixShader')
    node_mix.location = 200,0

    #create first diffuse node
    node_diffuse_1 = nodes.new(type='ShaderNodeBsdfDiffuse')
    node_diffuse_1.inputs[0].default_value = (0, 1, 0, 1) #green RGBA
    node_diffuse_1.location = 0,0

    #create second diffuse node
    node_diffuse_2 = nodes.new(type='ShaderNodeBsdfDiffuse')
    node_diffuse_2.inputs[0].default_value = (1, 0, 0, 1) #red RGBA
    node_diffuse_1.location = 0,200

    #create object info node
    node_obj_info = nodes.new(type='ShaderNodeObjectInfo')
    node_obj_info.location = 0,400

    #create output node
    node_output = nodes.new(type='ShaderNodeOutputMaterial')   
    node_output.location = 400,0

    #create links between nodes
    links = mat.node_tree.links
    links.new(node_mix.outputs[0], node_output.inputs[0]) #mix to output
    links.new(node_obj_info.outputs[1], node_mix.inputs[0]) #object info to mix
    links.new(node_diffuse_1.outputs[0], node_mix.inputs[1]) #diffuse 1 to mix
    links.new(node_diffuse_2.outputs[0], node_mix.inputs[2]) #diffuse 2 to mix
    
    return mat
	
class BuildGridOP(bpy.types.Operator):
	bl_idname = "object.build_grid"
	bl_label = "Build grid"
	bl_options = {'REGISTER', 'UNDO'}
	
	count = bpy.props.IntProperty(name="Count", default=12, min=3, max=2147483647)
	cubeWidth = bpy.props.FloatProperty(name="Cell width", default=2, min=0, max=2147483647)
	gap = bpy.props.FloatProperty(name="Gap width", default=1, min=0, max=2147483647)
	
	def execute(self, context):
		offset = self.count * (self.cubeWidth + self.gap) / 2 - self.cubeWidth + (self.gap/2)

		#create parent empty
		parent = bpy.data.objects.new("Parent", None)
		bpy.context.scene.objects.link(parent)
		parent.empty_draw_size = 2
		parent.empty_draw_type = 'PLAIN_AXES'
		
		#we use custom properties to store the grid configuration information for later use
		parent["count"] = self.count
		parent["cellWidth"] = self.cubeWidth
		parent["gapWidth"] = self.gap
		parent["simulationSteps"] = 50 #default
		mat = findMaterial()
		
		#set initial cell, since we need a non-instanced object
		x = -offset
		y = -offset
		z = 0
		
		bpy.ops.mesh.primitive_cube_add(location=(x,y,z), radius=self.cubeWidth/2)
		origCell = bpy.context.active_object
		origCell.name = "Cell 0, 0"
		origCell.data.materials.append(mat)
		originalMeshData = origCell.data
		
		#for the rest of the cells, we create them as instances of the original
		for xIndex in range(0, self.count):
			x = (xIndex) * (self.cubeWidth + self.gap) - offset
			for yIndex in range(0, self.count):
				y = (yIndex) * (self.cubeWidth + self.gap) - offset
				
				newObject = bpy.data.objects.new(("Cell " + str(xIndex) + ", " + str(yIndex)), originalMeshData)
				newObject.location = (x,y,z)
				bpy.context.scene.objects.link(newObject)
				
				newObject.parent = parent
		
		return {'FINISHED'}
		
class AddPatternOP(bpy.types.Operator):
	bl_idname = "object.add_pattern"
	bl_label = "Add pattern"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		selected = bpy.context.selected_objects
		if (selected is not None) and (len(selected) == 1) and (selected[0].type == "EMPTY"):
			return True
		
		return False
		
	def execute(self, context):
		#get the cells (children of the parent empty) and data (custom properties of the empty)
		selected = bpy.context.selected_objects
		parent = selected[0]
		count = parent["count"]
		
		Matrix = rebuildMatrix(parent.children, count)
			
		#add selected pattern at center
		occupied = [[7, 7], [8,6], [8,5], [7,5], [6,5]] #glider
		
		#highlight initial live cells
		for pair in occupied:
			Matrix[pair[0]][pair[1]].pass_index = 1
		
		return {'FINISHED'}
		
class SetLiveOP(bpy.types.Operator):
	bl_idname = "object.set_live"
	bl_label = "Set cells alive"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		selected = bpy.context.selected_objects
		if (selected is not None):
			return True
			
		return False
		
	def execute(self, context):
		#set all the selected cells alive
		selected = bpy.context.selected_objects
		
		for cell in selected:
			cell.pass_index = 1
		
		return {'FINISHED'}

class ResetSimOP(bpy.types.Operator):
	bl_idname = "object.reset_sim"
	bl_label = "Reset simulation"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		selected = bpy.context.selected_objects
		if (selected is not None) and (len(selected) == 1) and (selected[0].type == "EMPTY"):
			return True
		
		return False
	
	def execute(self, context):
		#get the cells (children of the parent empty)
		selected = bpy.context.selected_objects
		parent = selected[0]
		children = parent.children
		
		for child in children:
			#clear all keyframes
			child.animation_data_clear()
			
		return {'FINISHED'}
		
class RunSimOP(bpy.types.Operator):
	bl_idname = "object.run_sim"
	bl_label = "Run simulation"
	bl_options = {'REGISTER', 'UNDO'}
	
	simulationSteps = bpy.props.IntProperty(name="Steps", default=50, min=0, max=2147483647)
	
	@classmethod
	def poll(cls, context):
		selected = bpy.context.selected_objects
		if (selected is not None) and (len(selected) == 1) and (selected[0].type == "EMPTY"):
			return True
		
		return False
		
	def invoke(self, context, event):
		selected = bpy.context.selected_objects[0]
		self.simulationSteps = selected["simulationSteps"]
		
		return self.execute(context)
	
	def execute(self, context):
		#get the cells (children of the parent empty) and data (custom properties of the empty)
		selected = bpy.context.selected_objects
		parent = selected[0]
		count = parent["count"]
		
		#update the simulationSteps custom property in the parent object
		parent["simulationSteps"] = self.simulationSteps
		
		Matrix = rebuildMatrix(parent.children, count)
		
		#set first keyframe for all cells
		keyframeAll(Matrix, count, 0)
		
		#start the simulation
		for step in range(1, self.simulationSteps):
			stepForward(Matrix, count, step)
		
		return {'FINISHED'}
		
classes = (RunSimOP, ResetSimOP, BuildGridOP, AddPatternOP, SetLiveOP)

def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)
	
def unregister():
	from bpy.utils import unregister_class
	for cls in reverse(classes):
		unregister_class(cls)

if __name__ == "__main__":
	register()
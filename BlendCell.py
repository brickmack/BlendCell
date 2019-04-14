bl_info = {
	"name": "BlendCell",
	"author": "Mackenzie Crawford",
	"version": (0, 2),
	"blender": (2, 79, 0),
	"description": "Visualization tool for cellular automata",
	"warning": "",
	"tracker_url": "",
	"category": "3D View"}

import bpy

count = 12
cubeWidth = 2
gap = 1
steps = 50

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
    for x in range(0, count):
        for y in range(0, count):
            Matrix[x][y].keyframe_insert(data_path="pass_index", frame=t)
            
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
	
class BuildGrid(bpy.types.Operator):
	bl_idname = "object.build_grid"
	bl_label = "Build grid"
	bl_options = {'REGISTER', 'UNDO'}
	
	count = bpy.props.IntProperty(name="Count", default=12, min=3, max=2147483647)
	cellWidth = bpy.props.FloatProperty(name="Cell width", default=2, min=0, max=2147483647)
	gapWidth = bpy.props.FloatProperty(name="Gap width", default=1, min=0, max=2147483647)
	
	def execute(self, context):
		offset = count * (cubeWidth + gap) / 2 - cubeWidth + (gap/2)

		#create parent empty
		parent = bpy.data.objects.new("Parent", None)
		bpy.context.scene.objects.link(parent)
		parent.empty_draw_size = 2
		parent.empty_draw_type = 'PLAIN_AXES'
		
		#we use custom properties to store the grid configuration information for later use
		parent["count"] = count
		parent["cellWidth"] = cellWidth
		parent["gapWidth"] = gapWidth

		mat = findMaterial()

		Matrix = [[0 for x in range(count)] for y in range(count)]
		occupied = [[7, 7], [8,6], [8,5], [7,5], [6,5]] #glider

		for xIndex in range(0, count):
			x = (xIndex) * (cubeWidth + gap) - offset
			for yIndex in range(0, count):
				y = (yIndex) * (cubeWidth + gap) - offset
				z = 0
				bpy.ops.mesh.primitive_cube_add(location=(x,y,z), radius=cubeWidth/2)
				bpy.context.active_object.name = "Cell " + str(xIndex) + ", " + str(yIndex)
				Matrix[xIndex][yIndex] = bpy.context.active_object
				
				#set material
				Matrix[xIndex][yIndex].data.materials.append(mat)
				Matrix[xIndex][yIndex].pass_index = 0
			
				#set parent
				Matrix[xIndex][yIndex].parent = parent

		#highlight initial live cells
		for pair in occupied:
			Matrix[pair[0]][pair[1]].pass_index = 1

		#set initial keyframe for all cells
		for x in range(0, count):
			for y in range(0, count):
				Matrix[x][y].keyframe_insert(data_path="pass_index", frame=0)
		
		return {'FINISHED'}
	
class RunSimOP(bpy.types.Operator):
	bl_idname = "object.run_sim"
	bl_label = "Run simulation"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		offset = count * (cubeWidth + gap) / 2 - cubeWidth + (gap/2)

		#create parent empty
		parent = bpy.data.objects.new("Parent", None)
		bpy.context.scene.objects.link(parent)
		parent.empty_draw_size = 2
		parent.empty_draw_type = 'PLAIN_AXES'

		mat = findMaterial()

		Matrix = [[0 for x in range(count)] for y in range(count)]
		occupied = [[7, 7], [8,6], [8,5], [7,5], [6,5]] #glider

		for xIndex in range(0, count):
			x = (xIndex) * (cubeWidth + gap) - offset
			for yIndex in range(0, count):
				y = (yIndex) * (cubeWidth + gap) - offset
				z = 0
				bpy.ops.mesh.primitive_cube_add(location=(x,y,z), radius=cubeWidth/2)
				bpy.context.active_object.name = "Cell " + str(xIndex) + ", " + str(yIndex)
				Matrix[xIndex][yIndex] = bpy.context.active_object
				
				#set material
				Matrix[xIndex][yIndex].data.materials.append(mat)
				Matrix[xIndex][yIndex].pass_index = 0
			
				#set parent
				Matrix[xIndex][yIndex].parent = parent

		#highlight initial live cells
		for pair in occupied:
			Matrix[pair[0]][pair[1]].pass_index = 1

		#set initial keyframe for all cells
		for x in range(0, count):
			for y in range(0, count):
				Matrix[x][y].keyframe_insert(data_path="pass_index", frame=0)

		for step in range(1, steps):
			stepForward(Matrix, count, step)
			
		return {'FINISHED'}

def register():
	from bpy.utils import register_class
	register_class(RunSimOP)
	register_class(BuildGrid)
	
def unregister():
	from bpy.utils import unregister_class
	unregister_class(RunSimOP)
	unregister_class(BuildGrid)

if __name__ == "__main__":
	register()
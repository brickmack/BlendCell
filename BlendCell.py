#cellular automata visualization tool. Version 0.0

import bpy

count = 15
cubeWidth = 2
gap = 1
displayMode = 0 #0 for show/hide living/dead cells, 1 for material highlighting

def stepForward(Matrix, n, t):
    newMatrix = [[0 for x in range(n)] for y in range(n)] #stores born/live/die = 1/0/-1 for each cell in the next step, NOT a reference to the cells themselves
    
    for i in range(n):
        for j in range(n):
            #compute 8-neighbor sum using toroidal boundary conditions - x and y wrap around so that the simulaton takes place on a toroidal surface
                         
            total = 0
            if Matrix[i][(j-1)%n].hide_render == False:
                total = total + 1
            if Matrix[i][(j+1)%n].hide_render == False:
                total = total + 1
            if Matrix[(i-1)%n][j].hide_render == False:
                total = total + 1
            if Matrix[(i+1)%n][j].hide_render == False:
                total = total + 1
            if Matrix[(i-1)%n][(j-1)%n].hide_render == False:
                total = total + 1
            if Matrix[(i-1)%n][(j+1)%n].hide_render == False:
                total = total + 1
            if Matrix[(i+1)%n][(j-1)%n].hide_render == False:
                total = total + 1
            if Matrix[(i+1)%n][(j+1)%n].hide_render == False:
                total = total + 1
            
            #apply conways rules
            if Matrix[i][j].hide_render == False:
                if (total < 2) or (total > 3):
                    #die
                    newMatrix[i][j] = -1
            else:
                if total == 3:
                    #birth
                    newMatrix[i][j] = 1
            #otherwise, newMatrix[i][j] = 0/continue living

    #now we have the next set of cell states, apply them to the cells themselves
    if displayMode == 0: #show/hide mode
        for i in range(0, n):
            for j in range(0, n):
                if newMatrix[i][j] == 1:
                    Matrix[i][j].hide_render = False
                elif newMatrix[i][j] == -1:
                    Matrix[i][j].hide_render = True
                
        #set next keyframe for all cells
        for x in range(0, count):
            for y in range(0, count):
                Matrix[x][y].keyframe_insert(data_path="hide_render", frame=t)
    elif displayMode == 1:
        for i in range(0, n):
            for j in range(0, n):
                if newMatrix[i][j] == 1:
                    Matrix[i][j].data.materials[0] = liveMat
                elif newMatrix[i][j] == -1:
                    Matrix[i][j].data.materials[0] = mat
        
        #set next keyframe for all cells
        for x in range(0, count):
            for y in range(0, count):
                Matrix[x][y].keyframe_insert(data_path="active_material_index", frame=t)

offset = count * (cubeWidth + gap) / 2 - cubeWidth + (gap/2)

#empty cell color. Used regardless of displayMode
mat = bpy.data.materials.new(name="Cell")
mat.diffuse_color = (0, 0, 0)

if displayMode == 1: #color living/dead cells
    #live cell color
    liveMat = bpy.data.materials.new(name="Live Cell")
    liveMat.diffuse_color = (1, 0, 0)

Matrix = [[0 for x in range(count)] for y in range(count)]
#occupied = [[1, 2], [1, 3], [2, 4]]
#occupied = [[0, 0], [1, 1], [2, 2]]
#occupied = [[3, 1], [3, 2], [3, 3]]
#occupied = [[4, 4], [5,3], [6,3], [6,4], [6,5]] #oscillates
#occupied = [[5,5], [6,5], [5,4], [7,3], [7,4], [6,3]] #ship
occupied = [[7, 7], [8,6], [8,5], [7,5], [6,5]] #glider

for xIndex in range(0, count):
    x = (xIndex) * (cubeWidth + gap) - offset
    for yIndex in range(0, count):
        y = (yIndex) * (cubeWidth + gap) - offset
        z = 0
        bpy.ops.mesh.primitive_cube_add(location=(x,y,z), radius=cubeWidth/2)
        bpy.context.active_object.name = "Cell " + str(xIndex) + ", " + str(yIndex)
        Matrix[xIndex][yIndex] = bpy.context.active_object
        
        #hide by default
        Matrix[xIndex][yIndex].hide_render = True
        
        #set material
        Matrix[xIndex][yIndex].data.materials.append(mat)

for x in range(0, count):
    for y in range(0, count):
        print(Matrix[x][y].name)

if displayMode == 0:
    #set initial visible cells    
    for pair in occupied:
       Matrix[pair[0]][pair[1]].hide_render = False
elif displayMode == 1:
    #highlight initial live cells
    for pair in occupied:
        Matrix[pair[0]][pair[1]].data.materials[0] = liveMat

#set initial keyframe for all cells
for x in range(0, count):
    for y in range(0, count):
        Matrix[x][y].keyframe_insert(data_path="hide_render", frame=0)

for step in range(1, 10):
    stepForward(Matrix, count, step)
from Box2D import (b2DistanceJointDef, b2EdgeShape, b2FixtureDef,
                   b2PolygonShape, b2CircleShape, b2DistanceJoint)
import math

class SoftBody:
    cells = []
    muscles = []

    # ideally, cell_positions would be a dict with proper ids to each cell so muscle connections could be more reliable
    def __init__(self, pos, cell_positions, muscle_connections, cell_radius, world, muscle_groups, intersecting=False, min_extension=0.5, max_extension=3.0):
        self.min_extension = min_extension
        self.max_extension = max_extension

        self.fixture = b2FixtureDef(shape=b2CircleShape(radius=cell_radius), density=0.5, friction=1.5) 
        if not intersecting:
            self.fixture.filter.groupIndex = -2 # collides with itself, but not other bodies

        self.cells = [world.CreateDynamicBody(position=(pos[0] + x, pos[1] + y), fixtures=self.fixture, fixedRotation=True) for x, y in cell_positions]

        self.world = world

        # for c in self.cells:
        #     f = c.fixtures[0]
        #     f.filter.groupIndex = 2

        for a, b in muscle_connections:
            dfn = b2DistanceJointDef(
                frequencyHz=4,
                dampingRatio=1,
                bodyA=self.cells[a[1]],
                bodyB=self.cells[b[1]],
                localAnchorA=(0, 0),
                localAnchorB=(0, 0)
            )
            
            self.muscles.append(world.CreateJoint(dfn))

        self.muscle_groups = muscle_groups

        if self.muscle_groups:
            self.muscle_group_extensions = [0 for _ in range(len(self.muscle_groups))] # initial extensions are all 0
        
        self.initial_lengths = self.get_extensions()
        
        print("New Softbody with {}, masses, {} springs, and {} muscle groups".format(len(cell_positions), len(muscle_connections), len(self.muscle_groups)))
    
    def new_from_points(pos, cell_positions, cell_size, world, intersecting=False):
        return SoftBody(pos, cell_positions, calc_muscles_by_proximity(cell_positions), cell_size, world, None, intersecting=intersecting)
    
    def new_as_voxel(base_pos, matrix, cell_size, cell_radius, world, separate_perimeter=False, intersecting=False): # matrix: 2D Array
        # fill out a dict of positions
        # for each cell, try to find in the dict the coords of each point
        # if it exists, use it, else add it
        # add all connections
        # keep track of index, that's what the muscles will rely on
        # after listifying, sort by index

        cells = {} # {(float x, float y) : int id}
        connections = {} # {(int id_a, int id_b) : int ???? _ it's not going to be used } # dict for instant lookup only
        index = 0
        muscle_index = 0
        muscle_groups = []

        for i in range(len(matrix)): # index matrix by [x][y]
            for j in range(len(matrix[i])):
                if matrix[i][j] != 1:
                    continue

                transformations = [(0, 0), (1, 0), (0, 1), (1, 1)]
                positions = [((i + a) * cell_size, (j + b) * cell_size) for a, b in transformations]

                for pos in positions: # after this, we can be sure that all of our positions exist
                    if pos not in cells:
                        cells[pos] = index
                        index += 1
                
                top_left, top_right, bottom_left, bottom_right = [cells[pos] for pos in positions]

                # [x] pattern
                # top left -- bottom right
                # top right -- bottom left
                # top left -- top right
                # top right -- bottom right
                # bottom right -- bottom left
                # bottom left -- top left

                cell_connections = [
                    (top_left, bottom_right),
                    (top_right, bottom_left),
                    (top_left, top_right),
                    (top_right, bottom_right),
                    (bottom_right, bottom_left),
                    (bottom_left, top_left),
                ]

                temp = []

                for c in cell_connections: # same number of operations as checking before setting
                    if not (c in connections):
                        connections[c] = muscle_index
                        temp += [muscle_index]
                        muscle_index += 1

                muscle_groups += [temp]
                # save index

        for (x, y), i in cells.items(): # perimeter
            transformations = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
            for a, b in transformations:
                other = (x + (a * cell_size), y + (b * cell_size))
                if (other in cells):
                    c = (i, cells[other])
                    if (not c in connections):
                        connections[c] = muscle_index
                        muscle_index += 1

        # print(muscle_groups)

        sorted_connections = sorted(connections.items(), key=lambda a: a[1])
        # print(sorted_connections)

        cell_positions = [p for p, _ in sorted(cells.items(), key=lambda a: a[1])] # turn to list of tuples and sort by index
        ret_connections = [((cell_positions[a], a), (cell_positions[b], b)) for (a, b), i in sorted_connections] # sort of unnecessary

        # get connections as list and sort by index

        return SoftBody(base_pos, cell_positions, ret_connections, cell_radius, world, muscle_groups, intersecting=intersecting)
    
    def contract_muscles (self, muscles_indeces, length):
        for index in muscles_indeces:
            self.contract_muscle(index, length)

    def contract_muscle (self, index, length):
        for c in self.cells:
            c.awake = True
        self.muscles[index].length = float(cap(length, self.min_extension, self.max_extension))
        # self.muscles[index].length = length

    def contract_relative (self, index, length):
        for c in self.cells:
            c.awake = True
        new = self.muscles[index].length + length
        self.muscles[index].length = float(cap(new, self.min_extension, self.max_extension))

    def get_extensions (self):
        return [m.length for m in self.muscles]
    
    def muscle_distances_from_initial(self):
        return [final - initial for (final, initial) in zip(self.get_extensions(), self.initial_lengths)]
    
    def contract_muscle_group(self, index, amount):
        new = self.muscle_group_extensions[index] + amount
        capped = float(cap(new, self.min_extension, self.max_extension))
        self.muscle_group_extensions[index] = capped

        for i in self.muscle_groups[index]:
            self.muscles[i].length = capped
    
    def destroy_all (self, world):
        for m in self.muscles:
            world.DestroyJoint(m)
        for i in range(len(self.muscles))[::-1]: # THIS !!! Only thing that worked to get rid of memory
            del self.muscles[i]
        
def cap(v, min, max):
    if v < min:
        return min
    elif v > max:
        return max
    else:
        return v

def calc_muscles_by_proximity (cell_positions):
    modified = list(zip(cell_positions, range(len(cell_positions))))
    muscles = []
    for a in modified:
        smallest = sorted(modified, key=lambda x: get_dist(a[0], x[0]))[1:7]
        # print(smallest)
        for b in smallest:
            if not any(is_same_connection((a, b), (a, x)) for x in muscles):
                muscles.append((a, b))
            else:
                print("SKIPPED")

    # print(muscles)

    return muscles
        
    # for each cell, find the nearest cells
    # then create a bond between each cell, as long as that bond doesn't already exist

def is_same_connection (a, b):
    return a == b or a == (b[1], b[0])

def get_dist (a, b):
    return math.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)

# TODO: define max extension ???

def rect_positions(width, height, scale):
    ret = []
    for i in range(width):
        for j in range(height):
            ret += [(i * scale, j * scale)]

    return ret

def make_matrix(width, height, value):
    return [[value] * height] * width

def transpose_matrix(m): # assuming sublists of equal length
    ret = []

    height = len(m)
    width = len(m[0])

    for i in range(width):
        current = []
        for j in range(height):
            current += [m[(height - 1 - j)][i]]
        ret += [current]
    
    return ret
import Box2D  # The main library
from Box2D.b2 import (world, polygonShape, staticBody, dynamicBody, edgeShape, fixtureDef, circleShape)
from tools.environment import (Environment, RunTestbed)
from tools.softbody import (SoftBody, rect_positions, make_matrix, transpose_matrix)
import math

# TEST 1 "Snake"
# body: 2 x 10 matrix
# 33 masses and 160 springs
# fitness: |dx| ie abs(delta x)

m = [ # will come out transposed, because code interprets matrices as m[x][y]
    [0, 0, 0, 0, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 1, 0],
    [0, 0, 0, 0, 1, 1, 1, 0],
    [0, 0, 0, 0, 1, 1, 1, 0],
    [0, 0, 0, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 0],
]

body_matrix = make_matrix(10, 2, 1)
# body_matrix = m

io_size = None
dummy_world = world(gravity=(0, -10), doSleep=True)
dummy = SoftBody.new_as_voxel((0, 0.5), body_matrix, 1.5, 0.5, dummy_world)
print("{} Muscle groups".format(len(dummy.muscle_group_extensions)))
io_size = len(dummy.muscle_group_extensions)
dummy.destroy_all(dummy_world)

class SampleEnv(Environment):
    def __init__(self, **kwargs):
        self.time = 0
        self.platform_length = 200
        self.xi = None
        self.index = 0
        self.a = 2
        super().__init__(world(gravity=(0, -10), doSleep=True), **kwargs) 
        
    def init_bodies (self, world):
        ground = world.CreateBody(
            shapes=edgeShape(vertices=[(-self.platform_length / 2, 0), (self.platform_length / 2, 0)])
        )

        # self.body = SoftBody.new_as_voxel((0, 0.5 * len(body_matrix[0])), body_matrix, 1.5, 0.5, world)
        # self.body = SoftBody.new_as_voxel((0, 5), transpose_matrix(m), 1.5, 0.5, world, intersecting=True)
        self.body = SoftBody.new_as_voxel((0, 0.5), body_matrix, 1.5, 0.5, world)

        print(len(self.body.muscles))

        xi, _ = self.body.cells[0].GetWorldPoint((0, 0)) # tracks relative to one cell. Probably wiser to calculate center of mass.
        self.xi = xi

        # print(self.body.initial_lengths)
        # print(self.body.muscle_distances_from_initial())
        # print(len(self.body.muscle_group_extensions))
    
    def tick (self, world):
        # every_n(self.time, 60*3, lambda: print(self.body.muscle_distances_from_initial()))
        # for i in range(len(self.body.muscles)):
        #     self.body.contract_relative(i, math.sin(self.time / 10) * 0.1)

        # every_n(self.time, 60*2, )
        l = [1, 3, 5, 7, 9]

        # if self.time % 40 == 0:
        #     self.body.contract_muscle_group(self.index, -1)
        #     self.index = (self.index + 1) % len(self.body.muscle_group_extensions)
        #     print(self.body.muscle_group_extensions)
        #     if self.index > 1:
        #         self.body.contract_muscle_group(self.index - 2, 1)

        # if self.time % 60*2 == 0:
        #     if self.a == 2:
        #         self.a = -2
        #     elif self.a == -2:
        #         self.a = 2

        #     for i in l:
        #         self.body.contract_muscle_group(i, self.a)

        #     print(self.body.muscle_group_extensions)

        self.time += 1
    
    def calc_fitness (self):
        xf, _ = self.body.cells[0].GetWorldPoint((0, 0))
        dx = xf - self.xi

        return abs(dx)

def every_n (time, interval, f):
    if time % interval == 0:
        f()

# env = SampleEnv()
# env.body.contract_muscle(0, 1.0)
# env.body.destroy_all(env.world)
# bruh = SampleEnv()

# print(env.calc_fitness())

# for _ in range(200):
#     env.Step()

RunTestbed(SampleEnv, start_paused=True)
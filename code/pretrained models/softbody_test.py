# BROCKEN
# pass class to runtestbed and kwargs with init

import Box2D  # The main library
from Box2D.b2 import (world, polygonShape, staticBody, dynamicBody, edgeShape, fixtureDef, circleShape)
from tools.environment import (Environment, RunTestbed)
from tools.softbody import (SoftBody, rect_positions, make_matrix, transpose_matrix)

class SampleEnv(Environment):
    def __init__(self):
        super().__init__(world(gravity=(0, -10), doSleep=True))

    def init_bodies (self, world):
        ground = world.CreateBody(
            shapes=edgeShape(vertices=[(-40, 0), (40, 0)])
        )

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

        # self.body = SoftBody.new_from_points((0, 5), rect_positions(5, 20, 1.5), 0.5, world)
        # self.body = SoftBody.new_as_voxel((0, 5), make_matrix(5, 20, 1), 1.5, 0.5, world)
        # self.body = SoftBody.new_as_voxel((0, 5), transpose_matrix(m), 1.5, 0.5, world, intersecting=True)
        self.body = SoftBody.new_as_voxel((-20, 5), transpose_matrix(m), 1.5, 0.5, world, intersecting=True)
    
    def tick (self, world):
        pass

env = SampleEnv()

# for _ in range(200):
#     env.Step()

RunTestbed(env)
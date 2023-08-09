import Box2D  # The main library
from Box2D.b2 import (world, polygonShape, staticBody, dynamicBody, edgeShape, fixtureDef, circleShape)
from tools.environment import (Environment, RunTestbed)
from tools.softbody import (SoftBody, rect_positions, make_matrix, transpose_matrix)
import math
import neat
import pickle

# TEST 1 "Snake"
# body: 2 x 10 matrix
# 33 masses and 160 springs
# fitness: |dx| ie abs(delta x)

# NEW Extension model
# inputs will be given in relative to the initial configuration of lengths
# so taking 

class SampleEnv(Environment):
    def __init__(self, **kwargs):
        self.time = 0
        self.platform_length = 200
        self.xi = None
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'nn data/config-feedforward-softbody-1')
        file = open('nn data/winner-feedforward-softbody-1', 'rb')
        winner = pickle.load(file)
        file.close()

        self.net = neat.nn.FeedForwardNetwork.create(winner, config)
        print(self.net.input_nodes)
        print(self.net.output_nodes)
        print(winner.nodes.keys())
        super().__init__(world(gravity=(0, -10), doSleep=True), **kwargs) 
        
    def init_bodies (self, world):
        ground = world.CreateBody(
            shapes=edgeShape(vertices=[(-self.platform_length / 2, 0), (self.platform_length / 2, 0)])
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
        self.body = SoftBody.new_as_voxel((0, 0.5), make_matrix(10, 2, 1), 1.5, 0.5, world)
        # self.body = SoftBody.new_as_voxel((0, 5), transpose_matrix(m), 1.5, 0.5, world, intersecting=True)
        # self.body = SoftBody.new_as_voxel((-20, 5), transpose_matrix(m), 1.5, 0.5, world, intersecting=True)
        print(len(self.body.muscles))

        xi, _ = self.body.cells[0].GetWorldPoint((0, 0)) # tracks relative to one cell. Probably wiser to calculate center of mass.
        self.xi = xi
    
    def tick (self, world):
        # every_n(self.time, 60*3, lambda: print(self.calc_fitness()))
        # for i in range(len(self.body.muscles)):
        #     self.body.contract_muscle(i, 0)
        lengths = [m.length for m in self.body.muscles]
        new_lengths = self.net.activate(lengths)
        # print(self.body.cells[0].linearVelocity)
        # print(new_lengths)
        for i, v in enumerate(new_lengths):
            # print("{}, {}".format(i, v))
            # env.body.contract_muscle(i, v) # doesn't work for some reason
            self.body.muscles[i].length = 3 + v
        # print(self.body.cells[0].GetWorldPoint((0, 0)))

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
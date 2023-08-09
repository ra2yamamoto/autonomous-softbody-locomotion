import Box2D  # The main library
from Box2D.b2 import (world, polygonShape, staticBody, dynamicBody, edgeShape, fixtureDef, circleShape)
from tools.environment import (Environment, RunTestbed)
from tools.framework import (Keys)
from tools.softbody import (SoftBody, rect_positions, make_matrix, transpose_matrix)
import math
import neat
import pickle

# TEST 1 "Snake"
# body: 2 x 10 matrix
# 33 masses and 160 springs
# fitness: |dx| ie abs(delta x)

TIME_CONST = 1/60 # or 0.01

l = ["square", "long snake", "snake"]

class SampleEnv(Environment):
    def __init__(self, **kwargs):
        self.time = 0
        self.platform_length = 200
        self.xi = None
        self.direction = 1
        self.body_matrices = []
        self.nets = []

        for folder in l:
            config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'nn data/arbitrary bodies/{}/config-recurrent-trial-2'.format(folder))

            file = open('nn data/arbitrary bodies/{}/winner-recurrent-trial-2'.format(folder), 'rb')
            winner = pickle.load(file)
            file.close()

            file = open('nn data/arbitrary bodies/{}/body_matrix'.format(folder), 'rb')
            self.body_matrices += [pickle.load(file)]
            file.close()

            self.nets += [neat.ctrnn.CTRNN.create(winner, config, TIME_CONST)]

        super().__init__(world(gravity=(0, -10), doSleep=True), **kwargs) 
        
    def init_bodies (self, world):
        ground = world.CreateBody(
            shapes=edgeShape(vertices=[(-self.platform_length / 2, 0), (self.platform_length / 2, 0)])
        )

        self.bodies = []

        for m in self.body_matrices:
            self.bodies += [SoftBody.new_as_voxel((0, 0.5), m, 1.5, 0.5, world, intersecting=False)]
    
    def tick (self, world):
        for net, body in zip(self.nets, self.bodies):
            lengths = body.muscle_group_extensions
            new_lengths = net.advance(lengths, TIME_CONST, TIME_CONST)
            # print("BEFORE: ")
            # print(env.body.get_extensions())
            for i, n in enumerate(new_lengths):
                body.contract_muscle_group(i, n)
                # print("AFTER: ")
                # print(env.body.get_extensions())
            
            xf, _ = body.cells[0].GetWorldPoint((0, 0))

            # print(dir(self.body.cells[0]))
            
            if abs(xf) >= 80:
                for cell in body.cells:
                    lx, ly = cell.position
                    cell.position = (lx - 100 * sign(xf), ly)

        self.time += 1
    
    def calc_fitness (self):
        xf, _ = self.body.cells[0].GetWorldPoint((0, 0))
        dx = xf - self.xi
        
        if self.direction == 0:
            return self.time
        else:
            return dx * self.direction

        # return (dx)

def every_n (time, interval, f):
    if time % interval == 0:
        f()

def sign (val):
    if val >= 0:
        return 1
    else:
        return -1

# env = SampleEnv()
# env.body.contract_muscle(0, 1.0)
# env.body.destroy_all(env.world)
# bruh = SampleEnv()

# print(env.calc_fitness())

# for _ in range(200):
#     env.Step()

RunTestbed(SampleEnv, start_paused=True)
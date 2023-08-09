# The Balancing Pole problem as solved by NEAT using Box2D for physics

import Box2D  # The main library
from Box2D.b2 import (world, polygonShape, staticBody, kinematicBody, dynamicBody, edgeShape, fixtureDef, circleShape, revoluteJointDef, distanceJointDef)
from tools.environment import (Environment, RunTestbed)
from tools.softbody import (SoftBody, rect_positions, make_matrix, transpose_matrix)
import math
import random
from inspect import signature
import neat
import pickle

class SampleEnv(Environment):
    def __init__(self, **kwargs):
        self.time = 0
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'nn data/config-feedforward')
        file = open('nn data/winner-feedforward', 'rb')
        winner = pickle.load(file)
        file.close()

        self.net = neat.nn.FeedForwardNetwork.create(winner, config)
        super().__init__(world(gravity=(0, -10), doSleep=True), **kwargs)

        self.auto_stim = True
        self.thinking = True

    def init_bodies (self, world):
        self.time = 0

        boxFixture = fixtureDef(shape=polygonShape(box=(1, 1)), density=5, friction=0.2) 

        fixture = fixtureDef(shape=polygonShape(box=(5, 0.5)), density=5, friction=0)
        fixture.filter.groupIndex = -2
        fixture2 = fixtureDef(shape=polygonShape(box=(5, 0.5)), density=5, friction=0)
        fixture2.filter.groupIndex = -2

        ground = world.CreateBody(
            shapes=edgeShape(vertices=[(-40, 0), (40, 0)])
        )

        self.paddle = world.CreateBody(shapes=polygonShape(box=(5, 0.5)), position=(0, 1))
        # self.paddle = world.CreateDynamicBody(position=(0, 0.5), fixtures=fixture)
        self.pole = world.CreateDynamicBody(position=(0, 5.5), angle=math.pi / 2, fixtures=fixture2)

        for i in range(10):
            world.CreateDynamicBody(position=(-15, 2 + i * 2), fixtures=boxFixture)

        dfn = revoluteJointDef(
            bodyA=self.paddle,
            bodyB=self.pole,
            anchor=(0, 1),
        )

        self.joint = world.CreateJoint(dfn)
        # self.pole.ApplyLinearImpulse((-100, 0), self.pole.GetWorldPoint((0, 0)), True)
    
    def tick (self, world):
        if self.thinking:
            if self.time % (60*3) == 0 and self.auto_stim:
                mag = random.random() * 200
                impulse = -mag if random.random() > 0.5 else mag
                self.pole.ApplyLinearImpulse((impulse, 0), self.pole.GetWorldPoint((0, 0)), True)

            angle = self.joint.angle
            # print(angle)

            vel, _ = self.pole.linearVelocity
            # print(self.paddle.GetWorldPoint((0, 0)))

            [offset] = self.net.activate((angle, vel))

            self.move_paddle(offset)

            pole_x, pole_y = self.pole.GetWorldPoint((0, 0))
            paddle_x, paddle_y = self.paddle.GetWorldPoint((0, 0))

            if (abs(paddle_x) > 40):
                self.paddle.position = (0, paddle_y)
                self.pole.position = (0, pole_y)

        self.time += 1

    def move_paddle (self, amount):
        x, y = self.paddle.GetWorldPoint((0, 0))
        self.paddle.position = (x + amount, y)

# env = SampleEnv()

# for _ in range(200):
#     env.Step()
#     print(env.bruh.GetWorldPoint((0, 0)))

RunTestbed(SampleEnv)
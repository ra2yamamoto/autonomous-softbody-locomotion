# Environment for easy testing/visualizing
# Allows the same setup to be either manually stepped or run with the testbed

TIME_STEP = 1.0 / 60 # will not carry over into testbed
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480

from .framework import (Framework, Keys, main)
try:
    pass
except:
    print("Unable to import TestBed Framework, so running in testbed will not work.")

class Environment: # OOP <3 ;(
    def __init__(self, world, init_bodies=True): # kwargs should be passed along in implementations to avoide memory issues. (Otherwise data gets created twice in the same place.)
        if init_bodies:
            self.world = world
            self.init_bodies(self.world)

    def init_bodies (self, world): # Must be implemented. This is where all world setup should occur.
        # Be careful to add things to local variable world rather than self.world.
        # It's only set up as a separate function to allow for the same objects to be added to arbritrary worlds,
        # such as when running the test bed.
        raise Exception("init_bodies must be implemented.")
    
    def tick(self, world): # An arbitrary tick function meant to work on different world, similar to init_bodies.
        # Put everything that runs each frame here, EXCEPT stepping the simulation.
        # Again mind local variable world vs self.world.
        # Also keep in mind self can be used to track data, although again calling tick won't Step the simulation.
        raise Exception("tick must be implemented.")

    def Step(self):
        self.tick(self.world)
        self.world.Step(TIME_STEP, 10, 10)
    
    def KeyPress(self, key):
        pass


def RunTestbed(env_class, start_paused=False): # must be given class, instead of instance
    class Sample(Framework):
        def __init__(self):
            super(Sample, self).__init__()
            try:
                self.env_obj = env_class(init_bodies=False)
                self.env_obj.init_bodies(self.world)
                self.paused = start_paused
                self.callback = 0
            except Exception as bruh:
                print(bruh)

        def Step(self, settings):
            if self.callback == 1:
                self.callback += 1
            elif self.callback == 2:
                self.callback = 0
                self.paused = True

            settings.pause = self.paused
            if not self.paused:
                self.env_obj.tick(self.world)

            super(Sample, self).Step(settings)
        
        def Keyboard(self, key):
            if key == Keys.K_p:
                self.paused = not self.paused
            if key == Keys.K_s: # step sim
                if self.paused:
                    self.paused = False
                    self.callback = 1
            self.env_obj.KeyPress(key)

    main(Sample)

import simpylc as sp


class Timing(sp.Chart):
    def __init__(self):
        sp.Chart.__init__(self)

    def define(self):
        self.channel(sp.world.sailboat.acceleration, sp.white, -1, 1, 80)
        self.channel(sp.world.sailboat.drag, sp.white, 0, 0.5, 40)
        self.channel(sp.world.sailboat.forward_velocity, sp.white, 0, 8, 40)
        self.channel(sp.world.sailboat.perpendicular_sail_force, sp.red, 0, sp.world.wind.wind_scalar, 40)
        self.channel(sp.world.sailboat.forward_sail_force, sp.red, 0, sp.world.wind.wind_scalar, 40)


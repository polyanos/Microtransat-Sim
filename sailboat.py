from SimPyLC import *


class Sailboat (Module):
    def __init__(self):
        Module.__init__(self)

        self.page('sailboat')

        self.group('position', True)
        self.position_x = Register()
        self.position_y = Register()
        self.position_z = Register()

        self.group('wind vane')
        self.wind_vane_angle = Register()

        self.group('sail')
        self.target_sail_angle = Register(0)
        self.sail_angle = Register(0)

    def input(self):
        self.part('target sail angle')
        self.target_sail_angle.set(world.control.target_sail_angle)

    def sweep(self):
        self.position_x.set(self.position_x - world.control.movement_speed)

        if self.sail_angle > self.target_sail_angle:
            self.sail_angle.set(self.sail_angle - 1)

        if self.sail_angle < self.target_sail_angle:
            self.sail_angle.set(self.sail_angle + 1)

        self.wind_vane_angle.set(self.wind_vane_angle + 1)

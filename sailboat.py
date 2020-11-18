from simpylc import *


class Sailboat (Module):
    def __init__(self):
        Module.__init__(self)

        self.page('sailboat')

        self.group('position', True)
        self.position_x = Register()
        self.position_y = Register()
        self.position_z = Register()

        self.group('sail')
        self.target_sail_angle = Register(0)
        self.local_sail_angle = Register(0)
        self.global_sail_angle = Register(self.local_sail_angle)

    def input(self):
        self.part('target sail angle')
        self.target_sail_angle.set(world.control.target_sail_angle)

    def sweep(self):
        if self.local_sail_angle > self.target_sail_angle:
            self.local_sail_angle.set(self.local_sail_angle - 1)

        if self.local_sail_angle < self.target_sail_angle:
            self.local_sail_angle.set(self.local_sail_angle + 1)

        self.global_sail_angle.set((self.local_sail_angle - 90) % 360)

        perpendicular_angle = self.local_sail_angle % 360
        alpha = abs(perpendicular_angle - world.wind.wind_direction)
        perpendicular_thrust = math.cos(math.radians(alpha)) * world.wind.wind_scalar
        forward_thrust = math.sin(math.radians(45)) * perpendicular_thrust



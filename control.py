from simpylc import *


class Control(Module):
    def __init__(self):
        Module.__init__(self)

        self.page('sailboat movement control')

        self.group('control', True)
        self.movement_speed = Register()

        self.group('sail')
        self.target_sail_angle = Register()

    def sweep(self):
        if self.target_sail_angle > 90:
            self.target_sail_angle.set(90)

        if self.target_sail_angle < -90:
            self.target_sail_angle.set(-90)


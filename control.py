import simpylc as sp


class Control(sp.Module):
    def __init__(self):
        sp.Module.__init__(self)

        self.page('sailboat movement control')

        self.group('control', True)
        self.movement_speed_x = sp.Register(0)
        self.movement_speed_y = sp.Register(0)

        self.group('sail')
        self.target_sail_angle = sp.Register()

        self.group('rudder')
        self.target_gimbal_rudder_angle = sp.Register()

    def sweep(self):
        if self.target_sail_angle > 90:
            self.target_sail_angle.set(90)

        if self.target_sail_angle < -90:
            self.target_sail_angle.set(-90)

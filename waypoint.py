from simpylc import *


class Waypoint (Module):
    def __init__(self):
        Module.__init__(self)

        self.page('waypoint')

        self.group('waypoints', True)
        self.waypoint1_x = Register(3)
        self.waypoint1_y = Register(-5)
        self.waypoint1_z = Register()

        self.waypoint2_x = Register(5)
        self.waypoint2_y = Register(-20)
        self.waypoint2_z = Register()

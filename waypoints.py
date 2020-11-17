from simpylc import *


class Waypoints (Module):
    def __init__(self):
        Module.__init__(self)

        self.page('waypoints')

        self.group('settings', True) # x,y,z
        self.waypointX = Register()
        self.waypointY = Register()
        self.waypointZ = Register()

    def sweep(self):
        print("s")


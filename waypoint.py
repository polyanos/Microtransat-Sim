from simpylc import *
from routeWaypoint import RouteWaypoint


class Waypoint (Module):
    def __init__(self):
        Module.__init__(self)

        self.startPosition = RouteWaypoint(0, 0)
        self._waypointList = [RouteWaypoint(3, -5)]
        self._waypointList.append(RouteWaypoint(6, -7))
        self._waypointList.append(RouteWaypoint(10, -3))

        self.page('waypoint')
        self.group('waypoints', True)

        self.waypoint1_x = Register(self._waypointList[0].X)
        self.waypoint1_y = Register(self._waypointList[0].Y)
        self.waypoint1_z = Register()

        self.waypoint2_x = Register(self._waypointList[1].X)
        self.waypoint2_y = Register(self._waypointList[1].Y)
        self.waypoint2_z = Register()

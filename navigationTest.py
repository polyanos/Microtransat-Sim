from navigation.units import Leg, Speed
from navigation.units import Distance
from navigation.units import SpeedDistanceTime
from navigation.units import CompassBearing
from navigation.units import Coordinate
from navigation.units import Waypoint
from navigation.units import Route

# Basic Units
speed = Speed(10)
distance = Distance(100)
sdt = SpeedDistanceTime(speed=speed, distance=distance)
bearing = CompassBearing(83)

# Positioning Units
latitude = Coordinate(56, 12, 34, "N")
longitude = Coordinate(2, 54, 19, "W")
waypoint = Waypoint(latitude, longitude)

# Routing Units
leg = Leg(sdt, waypoint, bearing)
legs = [leg]

route = Route(legs)

# Example methods

knots = speed.in_knots
time = sdt.time
latitude_in_decimal_format = latitude.as_decimal
longitude_from_decimal = Coordinate.longitude_from_decimall(-2.76543)

end_wpt = leg.end_waypoint
number_of_legs = route.number_of_legs
starting_point = route.start_waypoint


for leg in range(number_of_legs):
    current_leg = route.current_leg(leg)
    next_leg = route.next_leg(leg)
    previous_leg = route.previous_leg(leg)
from control import Control
from visualisation import Visualisation
from simpylc import *
from enum import Enum
from math import *

class CompassDirection(Enum):
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270

class Sailboat (Module):
    def __init__(self ):
        Module.__init__(self )

        self.page('sailboat')

        self.group('position', True)
        self.position_x = Register()
        self.position_y = Register()
        self.position_z = Register()
        
        self.group('rotation', True)
        self.sailboat_rotation = Register(0)  

        self.group('sail')
        self.target_sail_angle = Register(0)
        self.local_sail_angle = Register(0)
        self.global_sail_angle = Register(self.local_sail_angle)
        
        self.group('gimbal rudder')
        self.target_gimbal_rudder_angle = Register(0)
        self.gimbal_rudder_angle = Register(0)
        
        self.group('rudder forces')
        self.drag_force =Register(0)
        self.perpendicular_force = Register(0)
        self.forward_force = Register(0)

    def distanceToWaypoint(self):
        target_x = world.visualisation.wayPointMarker.center[0]
        target_y = world.visualisation.wayPointMarker.center[1]

        sailboat_x = self.position_x
        sailboat_y = self.position_y

        distance_x = target_x - sailboat_x
        distance_y = target_y - sailboat_y

        #print("Distance to waypoint: (", distance_x,  ",", distance_y, ")")

        return distance_x, distance_y

    def angleToWaypoint(self, distance_x, distance_y):
        deltaX = distance_x
        deltaY = distance_y
        rad = math.atan2(deltaY, deltaX)
        deg = abs(rad * (180/ math.pi))
 
        print("delta X: ", deltaX, "delta Y: ", deltaY)
        print("angle waypoint: ", deg)

        return deg

    def input(self):
        self.part('target sail angle')
        self.target_sail_angle.set(world.control.target_sail_angle)
        
        self.part('gimbal rudder angle')
        self.target_gimbal_rudder_angle.set(world.control.target_gimbal_rudder_angle)

    def sweep(self):

        if self.local_sail_angle > self.target_sail_angle:
            self.local_sail_angle.set(self.local_sail_angle - 1)
        
        if self.gimbal_rudder_angle > self.target_gimbal_rudder_angle:
            self.gimbal_rudder_angle.set(self.gimbal_rudder_angle - 1)
         
        if self.gimbal_rudder_angle < self.target_gimbal_rudder_angle:
            self.gimbal_rudder_angle.set(self.gimbal_rudder_angle + 1)

        self.global_sail_angle.set((self.sailboat_rotation + self.local_sail_angle) % 360)
        alpha = abs(self.global_sail_angle - world.wind.wind_direction)
        perpendicular_thrust = math.cos(math.radians(alpha)) * world.wind.wind_scalar
        forward_thrust = math.sin(math.radians(45)) * perpendicular_thrust
        self.position_x.set(self.position_x + world.control.movement_speed_x)
        self.position_y.set(self.position_y + world.control.movement_speed_y)
            
        if self.perpendicular_force.set(self.drag_force / cos(self.target_gimbal_rudder_angle * (180/(22/7)))):
            self.perpendicular_force % 360

        # TODO: Discuss
        # if self.forward_force.set(forward_thrust * cos(self.target_gimbal_rudder_angle * (180/(22/7)))):
        #     self.forward_force % 360

        # TODO: Discuss
        if self.gimbal_rudder_angle < 90:
            self.sailboat_rotation += (0.01*forward_thrust)*self.gimbal_rudder_angle
        else:
            self.gimbal_rudder_angle.set(90)
        self.angleToWaypoint(self.distanceToWaypoint()[0], self.distanceToWaypoint()[1])
        #print(forward_thrust)

        # if self.distanceToWaypoint()[0] < 1 and self.distanceToWaypoint()[1] < 1:
        #     world.control.movement_speed_x = 0.0
        #     world.control.movement_speed_y = 0.0

        if self.distanceToWaypoint()[0] > 1:
            if world.visualisation.wayPointMarker.center[0] >= self.position_x:
                world.control.movement_speed_x = 0.05
            else:
                world.control.movement_speed_x = -0.05
        else:
            world.control.movement_speed_x = 0

        if self.distanceToWaypoint()[1] > 1:
            if world.visualisation.wayPointMarker.center[1]>= self.position_y:
                world.control.movement_speed_y = 0.05
            else:
                world.control.movement_speed_y = -0.05
        else:
            world.control.movement_speed_y = 0
        


        #         target_x = world.visualisation.wayPointMarker.center[0]
        # target_y = world.visualisation.wayPointMarker.center[1]

        # sailboat_x = self.position_x
        # sailboat_y = self.position_y



        # if self.distanceToWaypoint()[0] < 5 and self.distanceToWaypoint()[1] < 5:
        #     #world.control.movement_speed = 0.0
        #     #print("reached waypoint radius")
        # else: 
        #     tempVane = self.wind_vane_angle
        #     # print("speed: ", world.control.movement_speed)
        #     # print("wind direction is ", tempVane+0)

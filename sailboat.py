from simpylc import *
from enum import Enum
from math import *
from pid import *
import time

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
        self.globalBoatRotation = Register(self.sailboat_rotation)

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

        self.group("time")
        self.last_time = Register(time.time())
        

    def distanceToWaypoint(self):
        target_x = world.visualisation.wayPointMarker.center[0]
        target_y = world.visualisation.wayPointMarker.center[1]

        sailboat_x = self.position_x
        sailboat_y = self.position_y

        distance_x = target_x - sailboat_x
        distance_y = target_y - sailboat_y

        print("Distance to waypoint: (", distance_x,  ",", distance_y, ")")

        return distance_x, distance_y

    def angleToWaypoint(self, distance_x, distance_y):
        deltaX = distance_x
        deltaY = distance_y
        rad = math.atan2(deltaY, deltaX)
        deg = rad * (180/ math.pi)
 
        # print("delta X: ", deltaX, "delta Y: ", deltaY)
        # print("angle waypoint: ", deg)

        return deg

    def input(self):
        self.part('target sail angle')
        self.target_sail_angle.set(world.control.target_sail_angle)
        
        self.part('gimbal rudder angle')
        self.target_gimbal_rudder_angle.set(world.control.target_gimbal_rudder_angle)

    def sweep(self):


        self.currentTime = time.time()
        self.deltaTime = (self.currentTime - self.last_time)
        self.last_time = time.time()
        if self.deltaTime > 0:
            self.deltaTime
        else:
            self.deltaTime = 1e-16
        
        print("ZZZ:   ", self.deltaTime)
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
        self.globalBoatRotation.set(self.sailboat_rotation)
            
        if self.perpendicular_force.set(self.drag_force / cos(self.target_gimbal_rudder_angle * (180/(22/7)))):
            self.perpendicular_force % 360

        # TODO: Discuss
        if self.forward_force.set(forward_thrust * cos(self.target_gimbal_rudder_angle * (180/(22/7)))):
            self.forward_force % 360

        # TODO: Discuss
        if self.gimbal_rudder_angle < 90:
            #self.sailboat_rotation += (0.01*forward_thrust)*self.gimbal_rudder_angle
            self.sailboat_rotation += (0.01)*self.gimbal_rudder_angle
            
            print("wtf am i doing?: ", self.sailboat_rotation)
            print("FORWARD TRUSTERS: ", forward_thrust)
        else:
            self.gimbal_rudder_angle.set(90)

        pidMainOutput = Pid().control(self.angleToWaypoint(self.distanceToWaypoint()[0],self.distanceToWaypoint()[1]), 2)
        world.control.movement_speed_x = 0.02
        world.control.movement_speed_y = 0.02
        # pidRudderOutput = Pid().control(1,1,1)
        # pidSailOutput = Pid().control(1,1,1)

        #missingAngle = self.angleToWaypoint(self.distanceToWaypoint()[0],self.distanceToWaypoint()[1])
        #print("pid output outside loop: ", pidMainOutput)
        #print("missing angle: ", missingAngle)



        # if  pidMainOutput > 5:
        print("pid output inside loop: ", pidMainOutput)
        #angleToAdjust = ((self.sailboat_rotation + missingAngle))
       # print("angleToAdjust: ", angleToAdjust)
        # if (missingAngle >  self.sailboat_rotation)%360:
        #     world.control.target_gimbal_rudder_angle.set(self.target_gimbal_rudder_angle + 1)
        # elif(missingAngle < self.sailboat_rotation)%360:
        #     world.control.target_gimbal_rudder_angle.set(self.target_gimbal_rudder_angle - 1)
        # else:
        #     world.control.target_gimbal_rudder_angle.set(0)



        # if missingAngle > 0:
        #     world.control.target_gimbal_rudder_angle.set(self.target_gimbal_rudder_angle + 1)
        # else:
        #     world.control.target_gimbal_rudder_angle.set(self.target_gimbal_rudder_angle - 1)

        # elif pidMainOutput < 5:
        #     world.control.gimbal_rudder_angle.set(0)
            
        
            
            #world.control.target_gimbal_rudder_angle.set(self.target_gimbal_rudder_angle + 1)
            # world.control.movement_speed_x = 0.1
            # world.control.movement_speed_y = 0.1
            #print("oi: ", self.target_gimbal_rudder_angle)

        # print("angle of boat: ", self.sailboat_rotation)



        # if heading between north and west x+ y-
        # if heading between north and east x+ y+
        # if heading between south and west x- y-
        #if heading between south and east x- y+





        #     if world.visualisation.wayPointMarker.center[0] >= self.position_x:
        #         world.control.movement_speed_x = 0.05
        #     else:
        #         world.control.movement_speed_x = -0.05
        # else:
        #     world.control.movement_speed_x = 0

        # if self.distanceToWaypoint()[1] > 1:
        #     if world.visualisation.wayPointMarker.center[1]>= self.position_y:
        #         world.control.movement_speed_y = 0.05
        #     else:
        #         world.control.movement_speed_y = -0.05
        # else:
        #     world.control.movement_speed_y = 0
        


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
       

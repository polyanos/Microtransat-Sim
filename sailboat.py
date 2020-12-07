from simpylc import *
from enum import Enum
from math import *
from pid import *
import time
import random

class CompassDirection(Enum):
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270

def is_between_angles(n, a, b):
    if a < b:
        return a <= n <= b
    return a <= n or n <= b


class Sailboat (Module):
    def __init__(self ):
        Module.__init__(self )

        self.page('sailboat')

        self.group('position', True)
        self.position_x = Register()
        self.position_y = Register()
        self.position_z = Register()
        
        self.group('rotation', True)
        self.sailboat_rotation = Register(90)  
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

        self.group("waypoint direction")
        self.angleToSail = Register(90)
        self.skp = Register(0)
        self.ski = Register(0)
        self.skd = Register(0)

        #self.pidMainOutput = Pid().control(self.angleToSail, world.period)
        self.pidMainOuput = Pid()


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
        deg = rad * (180/ math.pi)

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

        self.globalBoatRotation.set((self.sailboat_rotation - 90) % 360)

        
        if self.local_sail_angle > self.target_sail_angle:
            self.local_sail_angle.set(self.local_sail_angle - 1)
        
        if self.local_sail_angle < self.target_sail_angle:
            self.local_sail_angle.set(self.local_sail_angle + 1)
        
        if self.gimbal_rudder_angle > self.target_gimbal_rudder_angle:
            self.gimbal_rudder_angle.set(self.gimbal_rudder_angle - 1)
         
        if self.gimbal_rudder_angle < self.target_gimbal_rudder_angle:
            self.gimbal_rudder_angle.set(self.gimbal_rudder_angle + 1)


        # TODO: Refactor and document
        # Wat is de hoek van de wind ten opzichten van de x-as, tegen de klok is positief
        # Wat is de gewenste koershoek
        # Wat is het hoekverschil tussen de gewenste koershoek en de windhoek
        # Wat is de zeilstand (helft van stap 3)
        # Wat is de component van de wind die effect heeft op het zeil
        # loodrecht = totale windkracht * sin (alpha)
        # voorwaards = loodrecht * cos (beta)
        # beta = 90 - hoek van het zeil met de boot

        global_sailboat_rotation = (self.sailboat_rotation + 90) % 360
        global_sail_angle = (global_sailboat_rotation + self.local_sail_angle) % 360

        alpha = abs(global_sail_angle - world.wind.wind_direction) % 360
        alpha = 180 - alpha if alpha > 90 else alpha
        alpha = abs(alpha)

        perpendicular_force = world.wind.wind_scalar * sin(alpha)
        forward_force = perpendicular_force * sin(self.local_sail_angle + 0)
        forward_force = abs(forward_force)

        min_threshold = (global_sail_angle - 180) % 360
        if self.local_sail_angle < 0 and global_sail_angle < min_threshold:
            if not is_between_angles(global_sail_angle, min_threshold, world.wind.wind_direction):
                forward_force = forward_force * 0.01
        elif self.local_sail_angle < 0 and global_sail_angle > min_threshold:
            if is_between_angles(min_threshold, global_sail_angle, world.wind.wind_direction):
                forward_force = forward_force * 0.01

        max_threshold = (global_sail_angle + 180) % 360
        if self.local_sail_angle > 0 and global_sail_angle < max_threshold:
            if is_between_angles(global_sail_angle, max_threshold, world.wind.wind_direction):
                forward_force = forward_force * 0.01
        elif self.local_sail_angle > 0 and global_sail_angle > max_threshold:
            if not is_between_angles(max_threshold, global_sail_angle, world.wind.wind_direction):
                forward_force = forward_force * 0.01

        horizontal_force = cos(global_sailboat_rotation) * forward_force
        vertical_force = sin(global_sailboat_rotation) * forward_force

        multiSpeed = 0.01
        self.position_x.set(self.position_x - vertical_force * multiSpeed)
        self.position_y.set(self.position_y + horizontal_force * multiSpeed)

        if self.perpendicular_force.set(self.drag_force / cos(self.target_gimbal_rudder_angle * (180 / (22 / 7)))):
            self.perpendicular_force % 360

        if self.forward_force.set(forward_force * cos(self.target_gimbal_rudder_angle * (180 / (22 / 7)))):
            self.forward_force % 360

        if self.gimbal_rudder_angle < 90:
            self.sailboat_rotation += (0.01)*self.gimbal_rudder_angle
        else:
            self.gimbal_rudder_angle.set(90)

        self.pidMainOuput.control(self.angleToSail, world.period)

        self.pidMainOuput.setKp(self.skp)
        self.pidMainOuput.setKi(self.ski)
        self.pidMainOuput.setKd(self.skd)
        print(world.period)
        #random.randint(1,10)
        # pidMainOutput = Pid().control(self.angleToWaypoint(self.distanceToWaypoint()[0],self.distanceToWaypoint()[1]), 2)
        # world.control.movement_speed_x = 0.02
        # world.control.movement_speed_y = 0.02


            

       

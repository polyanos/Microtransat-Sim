# from simpylc import *
from enum import Enum
from math import *
from pid import *
import simpylc as sp
import time
import random

class CompassDirection(Enum):
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270


# TODO: better naming
def is_between_angles(n, a, b):
    if a < b:
        return a <= n <= b
    return a <= n or n <= b

def is_between_deadwind(n, a, b):
    #n = desired heading
    #k = current heading
    #a = deadzone 1
    #b = deadzone 2

    if a > n or b < n:
        print("big deadzone")



def is_sailing_against_wind(min_threshold,
                            max_threshold,
                            local_sail_angle,
                            global_sail_angle,
                            wind_direction):
    if local_sail_angle < 0 and \
            global_sail_angle < min_threshold and not \
            is_between_angles(global_sail_angle, min_threshold, wind_direction):
        return True

    if local_sail_angle < 0 and \
            global_sail_angle > min_threshold and \
            is_between_angles(min_threshold, global_sail_angle, wind_direction):
        return True

    if local_sail_angle > 0 and \
            global_sail_angle < max_threshold and \
            is_between_angles(global_sail_angle, max_threshold, wind_direction):
        return True

    if local_sail_angle > 0 and \
            global_sail_angle > max_threshold and not \
            is_between_angles(max_threshold, global_sail_angle, wind_direction):
        return True

    return False


class Sailboat (sp.Module):
    def __init__(self):
        sp.Module.__init__(self)

        self.page('sailboat')

        self.group('transform', True)
        self.position_x = sp.Register()
        self.position_y = sp.Register()
        self.position_z = sp.Register()
        self.sailboat_rotation = sp.Register()

        self.group('body')
        self.mass = sp.Register(20)

        self.group('velocity')
        self.drag = sp.Register()
        self.acceleration = sp.Register()
        self.forward_velocity = sp.Register()
        self.horizontal_velocity = sp.Register()
        self.vertical_velocity = sp.Register()

        self.group('sail')
        self.target_sail_angle = sp.Register()
        self.local_sail_angle = sp.Register()
        self.global_sail_angle = sp.Register()
        self.sail_alpha = sp.Register()
        self.perpendicular_sail_force = sp.Register()
        self.forward_sail_force = sp.Register()
        
        self.group('rudder')
        self.target_gimbal_rudder_angle = sp.Register(0)
        self.gimbal_rudder_angle = sp.Register(0)
        self.rotation_speed = sp.Register()

        self.group("time")
        self.last_time = Register(time.time())

        self.group("waypoint direction")
        self.angleToSail = Register(90)
        self.correctedAngle = Register()
        self.skp = Register(0.5)
        self.ski = Register(0.2)
        self.skd = Register(0.0005)

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
        self.target_sail_angle.set(sp.world.control.target_sail_angle)
        
        self.part('gimbal rudder angle')
        self.target_gimbal_rudder_angle.set(sp.world.control.target_gimbal_rudder_angle)

    def test(self, ats):
        test3 = ats +45
        test4 = ats -45

        if sp.world.wind.wind_direction < test3 and sp.world.wind.wind_direction > test4:
            print("wind: ", sp.world.wind.wind_direction)
            return True
        else:
            return False

            



    def sweep(self):
        
        if self.test(self.angleToSail):
            if self.sailboat_rotation < self.angleToSail:
                self.correctedAngle = self.angleToSail - 45
                #print(self.correctedAngle)
            else:
                self.correctedAngle = self.angleToSail + 45
        else:
            self.correctedAngle = self.angleToSail

        self.local_sail_angle.set(self.local_sail_angle - 1, self.local_sail_angle > self.target_sail_angle)
        self.local_sail_angle.set(self.local_sail_angle + 1, self.local_sail_angle < self.target_sail_angle)
        self.global_sail_angle.set((self.sailboat_rotation + self.local_sail_angle + 180) % 360)

        self.gimbal_rudder_angle.set(self.gimbal_rudder_angle - 1,
                                     self.gimbal_rudder_angle > self.target_gimbal_rudder_angle)
        self.gimbal_rudder_angle.set(self.gimbal_rudder_angle + 1,
                                     self.gimbal_rudder_angle < self.target_gimbal_rudder_angle)

        # Calculate forward force in N based on the angle between the sail and the wind
        self.sail_alpha.set(sp.abs(self.global_sail_angle - sp.world.wind.wind_direction) % 360)
        self.sail_alpha.set(sp.abs(180 - self.sail_alpha) % 360, self.sail_alpha > 90)
        self.perpendicular_sail_force.set(sp.world.wind.wind_scalar * sp.sin(self.sail_alpha))
        self.forward_sail_force.set(self.perpendicular_sail_force * sp.sin(self.local_sail_angle))
        self.forward_sail_force.set(sp.abs(self.forward_sail_force))

        # Sailing against wind
        min_threshold = (self.global_sail_angle - 180) % 360
        max_threshold = (self.global_sail_angle + 180) % 360
        self.forward_sail_force.set(0,
                                    is_sailing_against_wind(min_threshold,
                                                            max_threshold,
                                                            self.local_sail_angle,
                                                            self.global_sail_angle,
                                                            sp.world.wind.wind_direction))

        # Newton's second law
        self.drag.set(self.forward_velocity * 0.05)
        self.acceleration.set(self.forward_sail_force / self.mass - self.drag)
        self.forward_velocity.set(sp.limit(self.forward_velocity + self.acceleration * sp.world.period, 8))

        # Splitting forward velocity vector into vertical and horizontal components
        self.vertical_velocity.set(sp.cos(self.sailboat_rotation) * self.forward_velocity)
        self.horizontal_velocity.set(sp.sin(self.sailboat_rotation) * self.forward_velocity)

        self.position_x.set(self.position_x + self.horizontal_velocity * 0.001)
        self.position_y.set(self.position_y - self.vertical_velocity * 0.001)
        self.rotation_speed.set(0.001 * self.gimbal_rudder_angle * self.forward_velocity)
        self.sailboat_rotation.set((self.sailboat_rotation - self.rotation_speed) % 360)


        self.pidMainOuput.control(self.correctedAngle, world.period)
        #need to check if time function

        self.pidMainOuput.setKp(self.skp)
        self.pidMainOuput.setKi(self.ski)
        self.pidMainOuput.setKd(self.skd)

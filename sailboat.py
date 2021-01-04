# from simpylc import *
from enum import Enum
import math
import simpylc as sp
import pid as pid
import pid_sail as pids
import time


# to run python world.py
# need to manually change wind direction currently

# pid_sail is WIP so it is not being used
# some functions will be made into their own files
# some functions need changing/missing

# WIP
class Compass_direction(Enum):
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270


# TODO: better naming
def is_between_angles(n, a, b):
    if a < b:
        return a <= n <= b
    return a <= n or n <= b


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


class Sailboat(sp.Module):
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
        self.last_time = sp.Register(time.time())

        self.group("waypoint direction")
        self.angle_to_sail = sp.Register(90)
        self.corrected_angle = sp.Register()

        # standard values kp 0.5, ki 0.2, kd 0.0005
        self.skp = sp.Register(0.5)
        self.ski = sp.Register(0.2)
        self.skd = sp.Register(0.0005)

        # USE THIS TO SET WAYPOINT DESTINATION
        self.targetx = sp.Register(25)
        self.targety = sp.Register(25)

        # object declarations
        self.pid_main_output = pid.Pid()
        self.pid_sail_output = pids.Pid_sail()

    def distance_to_waypoint(self):
        target_x = self.targetx
        target_y = self.targety

        sailboat_x = self.position_x
        sailboat_y = self.position_y

        distance_x = target_x - sailboat_x
        distance_y = target_y - sailboat_y

        return distance_x, distance_y

    # WIP
    # has bug where it does not work in all situations
    # needs changing
    def angle_to_waypoint(self, distance_x, distance_y):
        deltaX = distance_x
        deltaY = distance_y
        rad = math.atan2(deltaY, deltaX)
        deg = rad * (180 / math.pi)

        return deg % 360

    def input(self):

        self.part('target sail angle')
        self.target_sail_angle.set(sp.world.control.target_sail_angle)
        self.part('gimbal rudder angle')
        self.target_gimbal_rudder_angle.set(sp.world.control.target_gimbal_rudder_angle)

    def check_for_deadwind(self, ats):
        deadwind_right = ats + 45
        deadwind_left = ats - 45

        if sp.world.wind.wind_direction < deadwind_right and sp.world.wind.wind_direction > deadwind_left:
            return True
        else:
            return False

    def tacking(self):

        # check if we need to tack left or right
        # depending on direction +- 90 so we turn 45 degree
        # tacking will be called if the sum of n of accelaration is higher than current value
        # need to figure out how to control rudder and sail angles to reach correct position
        # might need to only change corrected angle to sail to ?
        ##big bug bomb potential

        print("placeholder")

    def sweep(self):

        # calculates the angle to waypoint
        # need better naming
        self.calculated_angle = self.angle_to_waypoint(self.distance_to_waypoint()[0], self.distance_to_waypoint()[1])

        # This makes it turn 45 deg to the left or right if sailing into deadwind
        if self.check_for_deadwind(self.calculated_angle):
            if self.sailboat_rotation < self.calculated_angle:
                self.corrected_angle = self.calculated_angle - 45
            else:
                self.corrected_angle = self.calculated_angle + 45
        else:
            self.corrected_angle = self.calculated_angle

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
        self.vertical_velocity.set(sp.sin(self.sailboat_rotation) * self.forward_velocity)
        self.horizontal_velocity.set(sp.cos(self.sailboat_rotation) * self.forward_velocity)

        self.position_x.set(self.position_x + self.horizontal_velocity * 0.001)
        self.position_y.set(self.position_y + self.vertical_velocity * 0.001)
        self.rotation_speed.set(0.001 * self.gimbal_rudder_angle * self.forward_velocity)
        self.sailboat_rotation.set((self.sailboat_rotation - self.rotation_speed) % 360)

        self.delta_time = 0.05
        self.current_time = time.time()
        self.elapsed_time = self.current_time - self.last_time
        self.delta_time_world = sp.world.period

        # WIP
        # updates PID every delta_time
        # needs checking since it needs to happen without if statement
        # problem probably lies in finetuning/adjusting PID
        if self.elapsed_time > self.delta_time:
            # self.pid_main_output.control(self.corrected_angle, self.delta_time_world)

            sp.world.control.target_gimbal_rudder_angle.set(sp.world.sailboat.target_gimbal_rudder_angle - self.pid_main_output.control(self.corrected_angle,sp.world.sailboat.sailboat_rotation,self.delta_time_world))


            sp.world.control.target_sail_angle.set(
                self.pid_sail_output.sail_control(
                    self.sailboat_rotation, sp.world.wind.wind_direction))
            # print("sail angle?> ", self.target_sail_angle)
            # print("updating rudder info...", self.delta_time)
            self.last_time = self.current_time

        if sp.world.control.target_gimbal_rudder_angle > 35:
            sp.world.control.target_gimbal_rudder_angle.set(35)

        if sp.world.control.target_gimbal_rudder_angle < -35:
            sp.world.control.target_gimbal_rudder_angle.set(-35)
        # temporary to be able to adjust KP/KI/KD values while sim is running
        self.pid_main_output.setKp(self.skp)
        self.pid_main_output.setKi(self.ski)
        self.pid_main_output.setKd(self.skd)

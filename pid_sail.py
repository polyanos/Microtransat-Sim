import simpylc as sp
from pid import *

def distance_between_angles(alpha, beta):
    phi = abs(beta - alpha) % 360
    distance = (180 - phi) % 360 if phi > 90 else phi
    return distance



class Pid_sail (Module):
    def __init__(self):
        Module.__init__(self)

        self.page("sailPID")
        self.group("PID", True)
        self.kp = Register()
        self.ki = Register()
        self.kd = Register()
        self.dt = Register()




    def sail_control(self, sailboat_rotation, wind_direction):

        distance = distance_between_angles((sailboat_rotation + 180) % 360, wind_direction)

        if distance > 180:
            distance = (360 - distance) % 360

        # If wind blows from starboard
        if is_between_angles((sailboat_rotation - 180) % 360, sailboat_rotation, sp.world.wind.wind_direction):
            distance = -distance

        # angle that the sail needs to turn to
        if distance == 0 or distance == -0:
            return distance + 90
        else:
            return distance / 2


    def calculate_proportional(self, error):
        return self.kp * error

    def calculate_intergrational(self, error, dt):
        self.error_integral += self.ki * error * dt

        return self.error_integral
    
    def calculate_differentional(self, dt, error):
        return 0

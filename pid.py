import simpylc as sp


def is_between_angles(n, a, b):
    if a < b:
        return a <= n <= b
    return a <= n or n <= b

#calculate the error and returns by how much are we off desired heading
#distance is in this case the amount of angles we are off compared to our desired heading
def calculate_error(current_heading, desired_heading):
    phi = abs(current_heading - desired_heading) % 360
    distance = 360 - phi if phi > 180 else phi

    if is_between_angles(current_heading, (current_heading - 180) % 360, desired_heading):
        return distance
    else:
        return -distance


class Pid (sp.Module):
    def __init__(self):
        sp.Module.__init__(self)

        self.page("test")
        self.group("PID", True)
        self.error_integral = sp.Register(0)
        self.output_limits = sp.Register()
        self.latest_input = sp.Register()
        self.desired_heading = sp.Register()
        self.current_heading = sp.Register()

        # need cleaning/ redoing
        # Right now the KP/KI/KD is being changed in sailboat.py
        # This was so we can change the values while the sim was working
        # Since it didn't want to work when it was within the pid itself
        self.dt = sp.Register()
        self.kp = sp.Register(0)
        self.ki = sp.Register(0)
        self.kd = sp.Register(0)
        self.test = sp.Register(2)

    # limits the max margin of the error so the number doesn't become too big 
    # where the rudder will -max or max instantly
    def clamp(self, error, clamp_on):
        if self.error < -clamp_on:
            self.error = -clamp_on
            return self.error
        if self.error > clamp_on:
            self.error = clamp_on
            return self.error

    def setDesiredHeading(self, incoming_heading):
        self.desired_heading = incoming_heading

    def setDt(self, dt):
        self.dt = dt

    def setKp(self, kp):
        self.kp = kp

    def setKi(self, ki):
        self.ki = ki

    def setKd(self, kd):
        self.kd = kd

    #the main bulk of the program which calculates the error and adjusts the PID for the rudder
    def control(self, desired_heading, dt):
        current_heading = sp.world.sailboat.sailboat_rotation
        clamp_status = None
        integrater_status = None
        desired_heading = desired_heading % 360
        current_heading = current_heading % 360
        self.error = calculate_error(current_heading, desired_heading)
        self.errorc = calculate_error(current_heading, desired_heading)
        self.clamp(self.error, 5)

        # checks if the error and compare error are equal
        # most of the time it will be true
        if self.error != self.errorc:

            clamp_status = True
        else:
            clamp_status = False

        outputP = self.calculate_proportional(self.error)
        outputI = self.calculate_intergrational(dt, self.error)
        outputD = self.calculate_differentional(current_heading, dt, self.errorc)
        output = outputP + outputI + outputD

        # this checks if the error and output is either increasing together or decreasing
        # Based on the comparison it will let the rest of the program know if the integrater is still working
        # The error is always changing from signs (+/-) before the output so this is how we check if the integrater is still active
        # if the integrater is activate and the error is being clamped that means the integrater is too big
        # so it gets set to 0 until the error is not being clamped or the error changed from sign
        if (self.error > 0 and output > 0) or (self.error < 0 and output < 0):
            integrater_status = True
        else:
            integrater_status = False
        if clamp_status is True and integrater_status is True:
            self.error_integral = 0

        # WIP
        # this function inner if doesn't work i think, bug test needed, if doesn't work remove
        # this function needs fine tuning / redisigning so the it doesn't zig zag as often
        # multiplier needs tweaking, think it is too big right now
        # based on the error output it gets decided if the rudder needs to go left or right
        # how much the rudder needs to adjust is based on the output of the PID
        if self.error < 0:
            sp.world.control.target_gimbal_rudder_angle.set(sp.world.sailboat.target_gimbal_rudder_angle - (0.5 * output))
            if self.error < self.error - self.test:
                sp.world.control.target_gimbal_rudder_angle.set(sp.world.sailboat.target_gimbal_rudder_angle)
        else:
            sp.world.control.target_gimbal_rudder_angle.set(sp.world.sailboat.target_gimbal_rudder_angle - (0.5 * output))
            if self.error > self.error + self.test:
                sp.world.control.target_gimbal_rudder_angle.set(sp.world.sailboat.target_gimbal_rudder_angle)
        
        # clamps the -max/max rudder angle to the most optimal angle
        # if the rudder goes higher than 35 is starts producing drag

        if sp.world.control.target_gimbal_rudder_angle > 35:
            sp.world.control.target_gimbal_rudder_angle.set(35)

        if sp.world.control.target_gimbal_rudder_angle < -35:
            sp.world.control.target_gimbal_rudder_angle.set(-35)

    def calculate_proportional(self, error):
        return self.kp * error

    def calculate_intergrational(self, dt, error):
        self.error_integral += self.ki * error * dt

        return self.error_integral

    def calculate_differentional(self, current_input, dt, error):
        if error < 0:
            return -self.kd * ((current_input + error) / dt)
        else:
            return self.kd * ((current_input - error) / dt)

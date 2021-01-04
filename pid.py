
def is_between_angles(n, a, b):
    if a < b:
        return a <= n <= b
    return a <= n or n <= b


# calculate the error and returns by how much are we off desired heading
# distance is in this case the amount of angles we are off compared to our desired heading
def calculate_error(current_heading, desired_heading):
    phi = abs(current_heading - desired_heading) % 360
    distance = 360 - phi if phi > 180 else phi

    if is_between_angles(current_heading, (current_heading - 180) % 360, desired_heading):
        return distance
    else:
        return -distance


class Pid:
    def __init__(self):
        self.error_integral = 0
        self.output_limits = 0
        self.latest_input = 0
        self.desired_heading = 0
        self.current_heading = 0
        self.error = 0
        self.error_check = 0
        self.clamp_status = None
        self.integrater_status = None

        # need cleaning/ redoing
        # Right now the KP/KI/KD is being changed in sailboat.py
        # This was so we can change the values while the sim was working
        # Since it didn't want to work when it was within the pid itself

        self.kp = 0.5
        self.ki = 0.02
        self.kd = 0.0005

    # limits the max margin of the error so the number doesn't become too big 
    # where the rudder will -max or max instantly
    def clamp(self, clamp_on):
        if self.error < -clamp_on:
            self.error = -clamp_on
            return self.error
        if self.error > clamp_on:
            self.error = clamp_on
            return self.error

    def set_desired_heading(self, incoming_heading):
        self.desired_heading = incoming_heading

    # def setDt(self, dt):
    #     self.dt = dt

    def setKp(self, kp):
        self.kp = kp

    def setKi(self, ki):
        self.ki = ki

    def setKd(self, kd):
        self.kd = kd

    # the main bulk of the program which calculates the error and adjusts the PID for the rudder
    def control(self, desired_heading, dt):
        current_heading = 0  # this needs to come from sensor/ simplyc.world
        desired_heading = desired_heading % 360
        current_heading = current_heading % 360
        self.error = calculate_error(current_heading, desired_heading)
        self.error_check = calculate_error(current_heading, desired_heading)
        self.clamp(5)

        # checks if the error and compare error are equal
        # most of the time it will be true
        if self.error != self.error_check:

            self.clamp_status = True
        else:
            self.clamp_status = False

        output_p = self.calculate_proportional(self.error)
        output_i = self.calculate_intergrational(dt, self.error)
        output_d = self.calculate_differentional(current_heading, dt, self.error_check)
        output = output_p + output_i + output_d

        # this checks if the error and output is either increasing together or decreasing Based on the comparison it
        # will let the rest of the program know if the integrater is still working The error is always changing from
        # signs (+/-) before the output so this is how we check if the integrater is still active if the integrater
        # is activate and the error is being clamped that means the integrater is too big so it gets set to 0 until
        # the error is not being clamped or the error changed from sign
        if (self.error > 0 and output > 0) or (self.error < 0 and output < 0):
            self.integrater_status = True
        else:
            self.integrater_status = False
        if self.clamp_status is True and self.integrater_status is True:
            self.error_integral = 0

        # WIP
        # this function inner if doesn't work i think, bug test needed, if doesn't work remove
        # this function needs fine tuning / redesigning so the it doesn't zig zag as often
        # multiplier needs tweaking, think it is too big right now
        # based on the error output it gets decided if the rudder needs to go left or right
        # how much the rudder needs to adjust is based on the output of the PID
        if self.error < 0:
            print("placeholder if")
            # multiply the output by 0.5 this factor needs to be finetuned but 0.5 is ok for now
            # sp.world.control.target_gimbal_rudder_angle.set(
            #     sp.world.sailboat.target_gimbal_rudder_angle - (0.5 * output))
        else:
            print("placeholder else")
            # sp.world.control.target_gimbal_rudder_angle.set(
            #     sp.world.sailboat.target_gimbal_rudder_angle - (0.5 * output))

        # clamps the -max/max rudder angle to the most optimal angle
        # if the rudder goes higher than 35 is starts producing drag

        # max rotation for the rudder in the sim
        # if sp.world.control.target_gimbal_rudder_angle > 35:
        #     sp.world.control.target_gimbal_rudder_angle.set(35)
        #
        # if sp.world.control.target_gimbal_rudder_angle < -35:
        #     sp.world.control.target_gimbal_rudder_angle.set(-35)

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

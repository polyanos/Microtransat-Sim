import simpylc as sp


def is_between_angles(n, a, b):
    if a < b:
        return a <= n <= b
    return a <= n or n <= b


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
        self.dt = sp.Register()
        self.kp = sp.Register(0)
        self.ki = sp.Register(0)
        self.kd = sp.Register(0)
        self.test = sp.Register(2)

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

    def control(self, desired_heading, dt):
        current_heading = sp.world.sailboat.sailboat_rotation
        clamp_status = None
        integrater_status = None
        desired_heading = desired_heading % 360
        current_heading = current_heading % 360
        self.error = calculate_error(current_heading, desired_heading)
        self.errorc = calculate_error(current_heading, desired_heading)
        self.clamp(self.error, 5)
        if self.error != self.errorc:
            clamp_status = True
        else:
            clamp_status = False

        outputP = self.calculate_proportional(self.error)
        outputI = self.calculate_intergrational(dt, self.error)
        outputD = self.calculate_differentional(current_heading, dt, self.errorc)
        output = outputP + outputI + outputD

        if (self.error > 0 and output > 0) or (self.error < 0 and output < 0):
            integrater_status = True
        else:
            integrater_status = False
        if clamp_status is True and integrater_status is True:
            self.error_integral = 0

#this function inner if don't work i think, bug test needed, if doesn't work remove
        if self.error < 0:
            sp.world.control.target_gimbal_rudder_angle.set(sp.world.sailboat.target_gimbal_rudder_angle - (0.5 * output))
            if self.error < self.error - self.test:
                sp.world.control.target_gimbal_rudder_angle.set(sp.world.sailboat.target_gimbal_rudder_angle)
        else:
            sp.world.control.target_gimbal_rudder_angle.set(sp.world.sailboat.target_gimbal_rudder_angle - (0.5 * output))
            if self.error > self.error + self.test:
                sp.world.control.target_gimbal_rudder_angle.set(sp.world.sailboat.target_gimbal_rudder_angle)
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

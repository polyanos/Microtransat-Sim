from simpylc import *


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


class Pid (Module):
    def __init__(self):
        Module.__init__(self)

        self.page("test")
        self.group("PID", True)
        self.errorIntegral = Register(0)
        self.outputLimits = Register()
        self.latestInput = Register()
        self.desiredHeading = Register()
        self.currentheading = Register()
        self.dt = Register()
        self.kp = Register(0)
        self.ki = Register(0)
        self.kd = Register(0)
        self.test = Register(2)
        

    def clamp(self, error, clampOn):
        #print("IN CLAMP FUNCTION @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        if self.error < -clampOn:
            #print("inside if -")
            self.error = -clampOn
            #print("error inside clamp", error)
            return self.error
        if self.error > clampOn:
            #print("inside if")
            self.error = clampOn
            return self.error

    def setDesiredHeading(self, incomingHeading):
        self.desiredHeading = incomingHeading

    def setDt(self, dt):
        self.dt = dt

    def setKp(self,kp):
        self.kp = kp

    def setKi(self,ki):
        self.ki = ki

    def setKd(self,kd):
        self.kd = kd

    def control(self, desiredHeading, dt):
        currentHeading = world.sailboat.sailboat_rotation
        clampStatus = None
        integraterStatus = None

        desiredHeading = desiredHeading % 360
        currentHeading = currentHeading % 360
        

        # error = currentHeading - desiredHeading  # if - turn left, if + turn right 
        self.error = calculate_error(currentHeading, desiredHeading)
        self.errorc = calculate_error(currentHeading, desiredHeading)
        self.clamp(self.error, 5)
        #print("error after clamping: ", self.error,"  ", self.errorc)
        if self.error != self.errorc:
            #print("clamped@@@@@@")
            clampStatus = True
        else:
            clampStatus = False

        outputP = self.calculateProportional(self.error)
        outputI = self.calculateIntergrational(dt, self.error)
        outputD = self.calculateDifferentional(currentHeading, dt, self.errorc)
        output = outputP + outputI +outputD

        if (self.error > 0 and output > 0) or (self.error < 0 and output < 0):
            #print("S")
            integraterStatus = True
            #integrated still adding
        else:
            integraterStatus = False
        
        #print("clamp status: ", clampStatus, " intstatus: ", integraterStatus)
        if clampStatus == True and integraterStatus == True:
            #print("AM I SET TO 0?!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            self.errorIntegral = 0

        # print("KP: ", self.kp)
        # print("KI: ", self.ki)
        # print("KD: ", self.kd)
        # print("outputP: ", outputP)
        # print("outputI: ", outputI)
        # print("outputD: ", outputD)
        # print("outputMAIN: ", output)
        # print("ERROR: ", self.error)
        # print("CURRENTHEADING: ", currentHeading)
        # print("DESIREDHEADING: ", desiredHeading)




        if self.error < 0:
            #turn left
            world.control.target_gimbal_rudder_angle.set(world.sailboat.target_gimbal_rudder_angle - (0.5 *output))
            if self.error < self.error - self.test:
                world.control.target_gimbal_rudder_angle.set(world.sailboat.target_gimbal_rudder_angle)      
                #print("IF INSIDE IF")
        else:
            #turn right
            world.control.target_gimbal_rudder_angle.set(world.sailboat.target_gimbal_rudder_angle - (0.5 *output))
            if self.error > self.error + self.test:
                #print("IF INSIDE ELSE: ")
                world.control.target_gimbal_rudder_angle.set(world.sailboat.target_gimbal_rudder_angle)
        
        if world.control.target_gimbal_rudder_angle > 35:
            world.control.target_gimbal_rudder_angle.set(35)

        if world.control.target_gimbal_rudder_angle < -35:
            world.control.target_gimbal_rudder_angle.set(-35)
    
       



        # print("ERROR: ", error)
        # print("OUTPUT: ", output)


    def calculateProportional(self, error):
        return self.kp * error

    def calculateIntergrational(self, dt, error):
        #print("in calc errorint: ", self.errorIntegral)
        self.errorIntegral += self.ki * error * dt
        #print("after in calc errorint: ", self.errorIntegral)


        return self.errorIntegral

    def calculateDifferentional(self, currentInput, dt, error):
        if error < 0:
            return -self.kd * ((currentInput + error) / dt)
        else:
            return self.kd * ((currentInput - error) / dt)






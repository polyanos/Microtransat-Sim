from simpylc import *
import time
class Pid (Module):
    def __init__(self):
        Module.__init__(self)

        self.page("test")
        self.group("PID", True)
        self.kp = Register(0.05)
        self.ki = Register(0.2)
        self.kd = Register(0.15)
        self.errorIntegral = Register()
        self.outputLimits = Register()
        self.latestInput = Register()
        self.desiredHeading = Register()
        self.currentheading = Register()
        self.dt = Register()


    def control(self, desiredHeading, dt):
        currentHeading = world.sailboat.globalBoatRotation

        if desiredHeading < 0:
            desiredHeading + 360
        if currentHeading < 0:
            currentHeading + 360
        error = desiredHeading - currentHeading
        outputP = self.calculateProportional(error)
        outputI = self.calculateIntergrational(dt, error)
        outputD = self.calculateDifferentional(currentHeading, dt, error)
        output = outputP + outputI + outputD


        if desiredHeading < currentHeading:
            #turn rudder left currentheading++
            world.control.target_gimbal_rudder_angle.set(world.sailboat.target_gimbal_rudder_angle + output)

            print("IF BOOP")
        elif desiredHeading > currentHeading:
            #turn rudder right currentheading--
            world.control.target_gimbal_rudder_angle.set(world.sailboat.target_gimbal_rudder_angle + output)
            # if world.control.target_gimbal_rudder_angle > 35:
            #     world.control.target_gimbal_rudder_angle.set(35)

            print("ELIF BOOP")
        else:
            #straighten rudder
            print("ELSE YO")
            world.control.target_gimbal_rudder_angle.set(world.sailboat.target_gimbal_rudder_angle + 0.0001)
        if world.control.target_gimbal_rudder_angle > 35:
            world.control.target_gimbal_rudder_angle.set(35)
        if world.control.target_gimbal_rudder_angle < -35:
            world.control.target_gimbal_rudder_angle.set(-35)
        print("ERROR: ", error)
        print("OUTPUT: ", output)


    def calculateProportional(self, error):
        return self.kp * error

    def calculateIntergrational(self, dt, error):
        print("PID CLASS ENTER LOOP: ", self.errorIntegral)
        self.errorIntegral += self.ki * error * dt
        print("PID CLASS EXIT LOOP: ", self.errorIntegral)
        return self.errorIntegral

    def calculateDifferentional(self, currentInput, dt, error):
        return self.kd * ((currentInput - self.latestInput) / dt)






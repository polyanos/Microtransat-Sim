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

    # def sweep(self):
    #     # self.currentInput = random.randint(1,50)
    #     # self.dt = random.randint(1,10)
    #     self.control(self.currentInput, self.expectedInput, self.dt)

    def control(self, desiredHeading, dt):
        #fixing this function, it does it meet the requirements for what we need
        #suppose to take in desired angle and current angle and return the error between those 2
        #KI is checking if we are still turning the wrong way and ramps up as needed
        #KD is checking if we are turning too fast and slows it down
        #KP is a set value between negative and positive

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
            print("boop")
        elif desiredHeading > currentHeading:
            #turn rudder right currentheading--
            world.control.target_gimbal_rudder_angle.set(world.sailboat.target_gimbal_rudder_angle + output)

            print("boop2")
        else:
            #straighten rudder
            print("yo")
            world.control.target_gimbal_rudder_angle.set(world.sailboat.target_gimbal_rudder_angle + 0.0001)

        print("BOOPDIBOOP", error)
        print("OUTPUT: ", output)


        #TODO
        # OUTPUT USED TO CALCULATE HOW MUCH THE RUDDER MUST SPINNY SPIN
        # error = abs(desiredHeading - currentHeading)
        # outputP = self.calculateProportional(error)
        # outputI = self.calculateIntergrational(dt, error)
        # outputD = self.calculateDifferentional(currentHeading, dt, error)

        # #figure out a proper output type for the whole function
        # output = outputP + outputI + outputD
        # self.latestInput = currentHeading
        # print("kp value is: ", outputP, " | ki value is: ", outputI, " | kd value is: ", outputD, " | output: ", output)
        # print(" ")
        # return output

    def calculateProportional(self, error):
        return self.kp * error

    def calculateIntergrational(self, dt, error):
        print("PID CLASS ENTER LOOP: ", self.errorIntegral)
        self.errorIntegral += self.ki * error * dt
        print("PID CLASS EXIT LOOP: ", self.errorIntegral)
        return self.errorIntegral

    def calculateDifferentional(self, currentInput, dt, error):
        return self.kd * ((currentInput - self.latestInput) / dt)






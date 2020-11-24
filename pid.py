from simpylc import *
class Pid (Module):
    def __init__(self):
        Module.__init__(self)

        self.page("test")
        self.group("PID", True)
        self.kp = Register(0.05)
        self.ki = Register(0.2)
        self.kd = Register(0.0001)
        self.errorIntegral = Register()
        self.outputLimits = Register()
        self.latestInput = Register()
        self.currentInput = Register()
        self.expectedInput = Register()
        self.dt = Register()

    # def sweep(self):
    #     # self.currentInput = random.randint(1,50)
    #     # self.dt = random.randint(1,10)
    #     self.control(self.currentInput, self.expectedInput, self.dt)

    def control(self, currentInput, expectedInput, dt):
        error = abs(expectedInput - currentInput)
        outputP = self.calculateProportional(error)
        outputI = self.calculateIntergrational(dt, error)
        outputD = self.calculateDifferentional(currentInput, dt, error)

        output = outputP + outputI + outputD
        self.latestInput = currentInput
        print("kp value is: ", outputP, " | ki value is: ", outputI, " | kd value is: ", outputD, " | output: ", output)
        print(" ")
        return output

    def calculateProportional(self, error):
        return self.kp * error

    def calculateIntergrational(self, dt, error):
        print("PID CLASS ENTER LOOP: ", self.errorIntegral)
        self.errorIntegral += self.ki * error * dt
        print("PID CLASS EXIT LOOP: ", self.errorIntegral)
        return self.errorIntegral

    def calculateDifferentional(self, currentInput, dt, error):
        return self.kd * ((currentInput - self.latestInput) / dt)






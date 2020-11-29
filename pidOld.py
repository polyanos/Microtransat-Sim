from simpylc import *
class Pid (Module):
    def __init__(self):
        Module.__init__(self)

        self.page("PID CONTROLLERS")
        self.group("PID main", True)
        self.kp = Register(0.05)
        self.ki = Register(0.2)
        self.kd = Register(0.0001)
        self.errorIntegral = Register()
        self.outputLimits = Register()
        self.latestInput = Register()
        self.currentInput = Register()
        self.expectedInput = Register()

        self.group("PID rudder")
        self.kpRudder = Register(0.05)
        self.kiRudder = Register(0.2)
        self.kdRudder = Register(0.0001)
        self.errorIntegralRudder = Register()
        self.outputLimitsRudder = Register()
        self.latestInputRudder = Register()
        self.currentInputRudder = Register()
        self.expectedInputRudder = Register()

        self.group("PID sail")
        self.kpSail = Register(0.05)
        self.kiSail = Register(0.2)
        self.kdSail = Register(0.0001)
        self.errorIntegralSail = Register()
        self.outputLimitsSail = Register()
        self.latestInputSail = Register()
        self.currentInputSail = Register()
        self.expectedInputSail = Register()

        self.group("other info")
        self.dt = Register()
    
    
    #calculations for the main pid
    def controlMain(self, currentInput, expectedInput, dt):
        errorMain = abs(expectedInput - currentInput)
        outputP = self.calculateProportionalMain(errorMain)
        outputI = self.calculateIntergrationalMain(dt, errorMain)
        outputD = self.calculateDifferentionalMain(currentInput, dt, error)

        output = outputP + outputI + outputD
        self.latestInput = currentInput
        return output


    def calculateProportionalMain(self, error):
        return self.kp * error

    def calculateIntergrationalMain(self, dt, error):
        self.errorIntegral += self.ki * error * dt
        return self.errorIntegral

    def calculateDifferentionalMain(self, currentInput, dt, error):
        return self.kd * ((currentInput - self.latestInput) / dt)

    #calculations for the rudder
    def controlRudder(self, currentInput, expectedInput, dt):
        error = abs(expectedInput - currentInput)
        outputP = self.calculateProportionalRudder(error)
        outputI = self.calculateIntergrationalRudder(dt, error)
        outputD = self.calculateDifferentionalRudder(currentInput, dt, error)

        output = outputP + outputI + outputD
        self.latestInput = currentInput
        return output


    def calculateProportionalRudder(self, error):
        return self.kp * error

    def calculateIntergrationalRudder(self, dt, error):
        self.errorIntegral += self.ki * error * dt
        return self.errorIntegral

    def calculateDifferentionalRudder(self, currentInput, dt, error):
        return self.kd * ((currentInput - self.latestInput) / dt)

    #calculations for the sail
    def control(self, currentInput, expectedInput, dt):
        error = abs(expectedInput - currentInput)
        outputP = self.calculateProportional(error)
        outputI = self.calculateIntergrational(dt, error)
        outputD = self.calculateDifferentional(currentInput, dt, error)

        output = outputP + outputI + outputD
        self.latestInput = currentInput
        return output


    def calculateProportional(self, error):
        return self.kp * error

    def calculateIntergrational(self, dt, error):
        self.errorIntegral += self.ki * error * dt
        return self.errorIntegral

    def calculateDifferentional(self, currentInput, dt, error):
        return self.kd * ((currentInput - self.latestInput) / dt)





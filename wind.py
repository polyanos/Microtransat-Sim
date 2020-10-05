import random

from SimPyLC import *


class Wind (Module):
    def __init__(self):
        Module.__init__(self)

        self.page('wind physics')

        self.group('wind direction', True)
        self.wind_direction = Register(0)
        self.wind_scalar = Register(15)

    def sweep(self):
        self.wind_direction.set(self.wind_direction + random.randint(-1, 1))

        while self.wind_direction >= 360:
            self.wind_direction.set(self.wind_direction - 360)

        while self.wind_direction < 0:
            self.wind_direction.set(self.wind_direction + 360)

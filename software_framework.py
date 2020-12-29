import simpylc as sp
from poseidon.core.core import Core


class SoftwareFramework (sp.Module):

    def __init__(self):
        sp.Module.__init__(self)
        self.page('software framework')

        self.group('placeholder', True)
        self.optimal_sailing_angle = sp.Register(0)

        self.poseidon = Core('settings.yaml')

    def input(self):
        self.poseidon.set_module_data('sailboat_rotation',
                                      sp.world.sailboat.sailboat_rotation)
        self.poseidon.set_module_data('wind_direction',
                                      sp.world.wind.wind_direction)

    def sweep(self):
        self.optimal_sailing_angle.set(self.poseidon.get_optimal_saling_angle())

from SimPyLC import *


class Visualisation (Scene):
    def __init__(self):
        Scene.__init__(self)

        self.camera = Camera()

        # Hull
        hull_color = (1, 1, 1)
        self.hull = Beam(size=(1, 0.4, 0.15), center=(0, 0, 0), color=hull_color)
        self.nose = Beam(size=(0.275, 0.275, 0.15), center=(-0.5, 0, 0), angle=45, color=hull_color)
        self.rear = Cylinder(size=(0.4, 0.4, 0.15), center=(0.5, 0, 0), color=hull_color)

        # Sail
        mast_color = (1, 1, 1)
        sail_color = (1, 0, 0)
        self.mast = Cylinder(size=(0.05, 0.05, 1), center=(0, 0, 0.5), color=mast_color)
        self.gimbal = Ellipsoid(size=3 * (0.05,), center=(0, 0, -0.25), pivot=(0, 0, 1), color=mast_color)
        self.boom = Cylinder(size=(0.05, 0.05, 0.45), center=(0.25, 0, 0), axis=(0, 1, 0), angle=90, color=mast_color)
        self.sail = Beam(size=(0.4, 0.025, 0.7), center=(0, 0, 0.4), color=sail_color)

        # Wind vane
        wind_vane_color = (0, 1, 0)
        self.wind_vane = Beam(size=(0.05, 0.5, 0.05), center=(0, 0, 1.25), color=wind_vane_color)
        self.wind_vane_pointer = Cone(size=(0.15, 0.15, 0.15), center=(0, 0.25, 0), axis=(1, 0, 0), angle=-90, color=wind_vane_color)

        # Ocean
        water_color = (0, 0.025, 1)
        self.ocean = Beam(size=(100, 100, 0.005), center=(0, 0, -0.5), color=water_color)

    def display(self):
        sailboat_position = tEva((world.sailboat.position_x,  world.sailboat.position_y, world.sailboat.position_z))

        self.camera(
            position=tEva((world.sailboat.position_x + 4,  world.sailboat.position_y, world.sailboat.position_z + 1.5)),
            focus=tEva((world.sailboat.position_x - 1,  world.sailboat.position_y, world.sailboat.position_z))
        )

        self.hull(
            position=sailboat_position,
            parts=lambda:
                self.nose() +
                self.rear() +
                self.mast(
                    parts=lambda:
                        self.gimbal(
                            rotation=world.sailboat.sail_angle,
                            parts=lambda:
                                self.boom(
                                    parts=lambda:
                                        self.sail()
                                )
                        )
                )
        )

        self.wind_vane(
            position=sailboat_position,
            rotation=world.wind.wind_direction,
            parts=lambda:
                self.wind_vane_pointer()
        )

        self.ocean()

from simpylc import *


class Sailboat (Module):
    def __init__(self):
        Module.__init__(self)

        self.page('sailboat')

        self.group('position', True)
        self.position_x = Register()
        self.position_y = Register()
        self.position_z = Register()
        
        self.group('rotation', True)
        self.sailboat_rotation = Register()  

        self.group('sail')
        self.target_sail_angle = Register(0)
        self.local_sail_angle = Register(0)
        self.global_sail_angle = Register(self.local_sail_angle)
        
        self.group('gimbal rudder')
        self.target_gimbal_rudder_angle = Register(0)
        self.gimbal_rudder_angle = Register(0)
        
        self.group('rudder forces')
        self.drag_force = Register(0)
        self.perpendicular_force = Register(0)
        self.forward_force = Register(0)

    def input(self):
        self.part('target sail angle')
        self.target_sail_angle.set(world.control.target_sail_angle)
        
        self.part('gimbal rudder angle')
        self.target_gimbal_rudder_angle.set(world.control.target_gimbal_rudder_angle)

    def sweep(self):
        if self.local_sail_angle > self.target_sail_angle:
            self.local_sail_angle.set(self.local_sail_angle - 1)

        if self.local_sail_angle < self.target_sail_angle:
            self.local_sail_angle.set(self.local_sail_angle + 1)
        
        if self.gimbal_rudder_angle > self.target_gimbal_rudder_angle:
            self.gimbal_rudder_angle.set(self.gimbal_rudder_angle - 1)
         
        if self.gimbal_rudder_angle < self.target_gimbal_rudder_angle:
            self.gimbal_rudder_angle.set(self.gimbal_rudder_angle + 1)

        self.global_sail_angle.set((self.sailboat_rotation + self.local_sail_angle) % 360)
        alpha = abs(self.global_sail_angle - world.wind.wind_direction)
        perpendicular_thrust = math.cos(math.radians(alpha)) * world.wind.wind_scalar
        forward_thrust = math.sin(math.radians(45)) * perpendicular_thrust
            
        if self.perpendicular_force.set(self.drag_force / cos(self.target_gimbal_rudder_angle * (180/(22/7)))):
            self.perpendicular_force % 360

        # TODO: Discuss
        # if self.forward_force.set(forward_thrust * cos(self.target_gimbal_rudder_angle * (180/(22/7)))):
        #     self.forward_force % 360

        # TODO: Discuss
        if self.gimbal_rudder_angle < 90:
            self.sailboat_rotation += (0.01*forward_thrust)*self.gimbal_rudder_angle
        else:
            self.gimbal_rudder_angle.set(90)

        print(forward_thrust)
            


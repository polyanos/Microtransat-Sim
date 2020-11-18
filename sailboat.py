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

        self.group('wind vane')
        self.wind_vane_angle = Register()

        self.group('sail')
        self.target_sail_angle = Register(0)
        self.sail_angle = Register(0)
        
        self.group('gimbal rudder')
        self.target_gimbal_rudder_angle = Register(0)
        self.gimbal_rudder_angle = Register(0)
        
        self.group('fake speed')
        self.fake_speed = Register(0)
        
        self.group('rudder forces')
        self.drag_force =Register(0)
        self.perpendicular_force = Register(0)
        self.forward_force = Register(0)
        
       
    def input(self):
        self.part('target sail angle')
        self.target_sail_angle.set(world.control.target_sail_angle)
        
        self.part('gimbal rudder angle')
        self.target_gimbal_rudder_angle.set(world.control.target_gimbal_rudder_angle)

    def sweep(self):
        self.position_x.set(self.position_x - world.control.movement_speed)

        if self.sail_angle > self.target_sail_angle:
            self.sail_angle.set(self.sail_angle - 1)

        if self.sail_angle < self.target_sail_angle:
            self.sail_angle.set(self.sail_angle + 1)

        #self.sailboat_rotation.set(self.gimbal_rudder_angle + world.control.movement_speed)

        self.wind_vane_angle.set(self.wind_vane_angle + 1)
        
        if self.gimbal_rudder_angle > self.target_gimbal_rudder_angle:
            self.gimbal_rudder_angle.set(self.gimbal_rudder_angle - 1)
         
        if self.gimbal_rudder_angle < self.target_gimbal_rudder_angle:
            self.gimbal_rudder_angle.set(self.gimbal_rudder_angle + 1)
            
        if self.perpendicular_force.set(self.drag_force / cos(self.target_gimbal_rudder_angle * (180/(22/7)))):
            self.perpendicular_force % 360
            
        if self.forward_force.set(self.fake_speed * cos(self.target_gimbal_rudder_angle * (180/(22/7)))):
            self.forward_force % 360

        if self.gimbal_rudder_angle < 90:
            self.sailboat_rotation += 0.05*(self.gimbal_rudder_angle)
        else:
            self.gimbal_rudder_angle.set(90)
            
        # if self.distanceToWaypoint()[0] < 5 and self.distanceToWaypoint()[1] < 5:
        #     #world.control.movement_speed = 0.0
        #     #print("reached waypoint radius")
        # else: 
        #     tempVane = self.wind_vane_angle
        #     # print("speed: ", world.control.movement_speed)
        #     # print("wind direction is ", tempVane+0)

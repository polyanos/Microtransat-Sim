import socket
from poseidon.core.core import Core
from threading import Thread
import time
import canopen
import struct

poseidon = Core('settings.yaml')

poseidon.set_module_data('sailboat_rotation', 0) 
poseidon.set_module_data('rudder_rotation', 0)
poseidon.set_module_data('wind_direction', 0)
poseidon.set_module_data('sailboat_position_x', 0)
poseidon.set_module_data('sailboat_position_y', 0)

host = '192.168.196.229'    #local ip
port = 5560

network = canopen.Network()

master_node = canopen.LocalNode(0, 'master_node.eds')
sensor_node = canopen.RemoteNode(0x01,'sensor_node.eds') #.eds and object dictionary are interchangable
actuator_node = canopen.RemoteNode(0x02,'actuator_node.eds') #.eds and object dictionary are interchangable
network.add_node(master_node)
network.add_node(sensor_node)
network.add_node(actuator_node)

network.connect(bustype='socketcan', channel='can0', bitrate=500000)

def network_scan(network):
# This will attempt to read an SDO from nodes 1 - 127
    network.scanner.search()
    # We may need to wait a short while here to allow all nodes to respond
    time.sleep(0.5)
    for node_id in network.scanner.nodes:
        print("Found node %d!" % node_id)
        print("Hex:", node_id)

def read_without_od(node, index, subindex):
    '''reads from the node without using the Object Dictionary, returns hex byte string'''
    readValue = node.sdo.upload(index, subindex)
    readValue = struct.unpack('h', readValue)
    print(readValue[0])
    return readValue[0]

def write_without_od(node, index, subindex, value):
    '''writes to the node without using the Object Dictionary'''
    data = struct.pack('h', value)
    node.sdo.download(index, subindex, data)

def read_with_od(node, manufacturerObject_name: str):
    '''
    reads to the node using the Object Dictionary, assumes there is no subindex.
    to read subvalue, use:
        node.sdo['ManufacturerObjectName']['ManufacturerSubObjectName'].raw
    raw converts value automatically. .phys, .desc & .bits are also possible.
    '''
    readValue = node.sdo[manufacturerObject_name].raw
    return readValue

def write_with_od(node, manufacturerObject_name: str, value):
    '''
    writes to the node using the Object Dictionary, assumes there is no subindex.
    to write to subvalue, use:
        node.sdo['ManufacturerObjectName']['ManufacturerSubObjectName'].write(value)
    '''
    node.sdo[manufacturerObject_name].write(value)

def can_write_read():
    while(True):
        '''
        reads sensor data and writes the read value to the actuator
        '''
        opt_sail_angle = poseidon.get_optimal_saling_angle()
        #opt_rudder_angle = poseidon.get_optimal_rudder_angle()

    #without using object dictionary
        #data = read_without_od(sensor_node, 0x2000, 0)
        #write_without_od(actuator_node, 0x2001, 0, data)

    #using object dictionary
        sensor_data = read_with_od(sensor_node, 'Sensor')
        write_with_od(actuator_node, 'Actuator', translate(opt_sail_angle, -90, 90, 0, 180))

        print("Optimal sail angle: " , round(opt_sail_angle, 5),
                "\t\tmapped: ", round(translate(opt_sail_angle, -90, 90, 0, 180)),
                "\t\tincoming sensor val:", sensor_data)
        
        time.sleep(0.1)     #reduce spam

    network.disconnect()

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def send():
    while True:
        #get optimal actuator angles
        opt_sail_angle = poseidon.get_optimal_saling_angle()
        opt_rudder_angle = poseidon.get_optimal_rudder_angle()
        
        #print(opt_rudder_angle)
        
        #create a CSV string
        calced_values = str(opt_sail_angle) + "," + str(opt_rudder_angle) + ","
        
        #send data to server
        s.sendall(str.encode(calced_values))
        
        # print("Optimal sail angle: " , round(opt_sail_angle, 5),
        #       "\t\tmapped: ", round(translate(opt_sail_angle, -90, 90, 0, 180)),
        #       "\t\tincoming sensor val:", read_with_od(sensor_node, 'Sensor'))
        
        # write_with_od(actuator_node, 'Actuator', translate(opt_sail_angle, -90, 90, 0, 180))
        
        time.sleep(0.25)    #reduce spam
        
def receive():
    while True:
        #receive and decode incoming data
        reply = s.recv(1024)
        reply.decode('utf-8')
        
        #separate incoming messages by ','
        msg = reply.decode('utf-8').split(',')
        
        #convert strings into floats
        x_pos = float(msg[0])
        y_pos = float(msg[1])
        wind_dir = float(msg[2])
        sailboat_rotation = float(msg[3])
        rudder_rotation = float(msg[4])
        
        #set all data
        poseidon.set_module_data('sailboat_rotation', sailboat_rotation) #
        poseidon.set_module_data('rudder_rotation', rudder_rotation)
        poseidon.set_module_data('wind_direction', wind_dir)
        poseidon.set_module_data('sailboat_position_x', x_pos)
        poseidon.set_module_data('sailboat_position_y', y_pos)
        
        #reduce spam
        time.sleep(0.25)

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host,port))
        
        #create threads
        sending_thread = Thread(target=send)
        receiving_thread = Thread(target=receive)
        can_thread = Thread(target=can_write_read)
        
        #start threads
        sending_thread.start()
        receiving_thread.start()
        can_thread.start()
        
        #ensures threads are terminated correctly
        sending_thread.join()
        receiving_thread.join()
        can_thread.join()
        
    s.close()

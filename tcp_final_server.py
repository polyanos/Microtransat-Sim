import multiprocessing.shared_memory as sm
import shared_memory_list as sml
from threading import Thread
import time

import socket

host = ''
port = 5560

shared_memory_list = sm.ShareableList(name=sml.list_name)
temp_val = ""


def setupServer():  #set up the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created.")
    try:
        s.bind((host, port))
    except socket.error as msg:
        print(msg)
    print("Socket bind complete.")
    return s


def setupConnection():
    s.listen(1) # Allows one connection at a time.
    conn, address = s.accept()
    print("Connected to: " + address[0] + ":" + str(address[1]))
    return conn

def receive():                                                      #receive data from Pi(client)
    while True:                                                     #listening
        calced_vals = conn.recv(1024)
        calced_vals = calced_vals.decode('utf-8').split(',')        #splits incoming CSV data
        opt_sail_angle = float(calced_vals[0])                      #cast values to float from string so that they can be used
        opt_rudder_angle = float(calced_vals[1])
        shared_memory_list[sml.target_sail_angle] = opt_sail_angle  #sets the values in the shared memory list the received data
        shared_memory_list[sml.target_rudder_angle] = opt_rudder_angle
        time.sleep(0.25)                                            #sleep to prevent spam

def send():                                                         #send shared memory list to Pi(client)
    while True:
        #creates a CSV string
        shared_val = (str(round(shared_memory_list[sml.sailboat_position_x], 4)) + ","                  
                        + str(round(shared_memory_list[sml.sailboat_position_y], 4)) + ","
                        + str(shared_memory_list[sml.wind_direction]) + ","
                        + str(round(shared_memory_list[sml.sailboat_rotation], 4)) + ","
                        + str(shared_memory_list[sml.rudder_rotation]) + ",")
        global temp_val
        if shared_val != temp_val:                                  #only send data non-duplicates
            temp_val = shared_val
            conn.sendall(str.encode(shared_val))
        time.sleep(0.25)                                            #prevent spam

s = setupServer()

if __name__ == "__main__":
    conn = setupConnection()
    sending_thread = Thread(target=send)                            #create threads
    receiving_thread = Thread(target=receive)
    sending_thread.start()                                          #starts threads
    receiving_thread.start()
    sending_thread.join()                                           #ensures thread terminated correctly
    receiving_thread.join()
    print("thread finished...exiting")
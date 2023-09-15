# Simulate UDP requests to a server
import struct, socket
import datetime, pickle

import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation

import multiprocessing, time

# Assuming the packet has been received and stored in a variable called 'packet'
# Assuming `data` is the binary data received from the network
delimiter = b'\xef'
end_delimiter = b'\xfe'
vector_format = 'fff'
quaternion_format = 'ffff'
# The format string specifies the data types and their order in the packet
format_string = ">xB7fBx"
format_string_size = struct.calcsize(format_string)
accuracy_info_format = 'B'

all_data = []

# List of tuples to query IMU data from
# 1st floor addrs
ip_head_address = '10.42.0.'
devices = [234, 56, 147, 241, 77]
devices = [77, 234, 56, 147, 50, 103]
# addresses.append(('10.42.0.234', 6970))
# addresses.append(('10.42.0.56', 6971))
# addresses.append(('10.42.0.147', 6972))
# addresses.append(('10.42.0.241', 6973))
# addresses.append(('10.42.0.77', 6974))

# 5th floor addrs
# ip_head_address = '192.168.50.'
# devices = [119, 102]
# addresses.append(('192.168.50.119', 6970))
# addresses.append(('192.168.50.102', 6973))

addresses = []
for i in range(len(devices)):
    addresses.append((ip_head_address + str(devices[i]), 6970 + i))

def set_SlimeVR_port(ip, port):
    # Structure of packet:
    # <\0> <0x99> <Port, 2 chars>
    struct_format = ">IH"

    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Define the message to be sent
    msg = bytearray(6)
    struct.pack_into(struct_format, msg, 0, 99, port)
    print("Set IP address to: " + str(ip) + ":" + str(port))

    # Send the UDP packet
    sock.sendto(msg, (ip, 6969))

def verbose():
    while True:
        print(all_data)
        time.sleep(1)
        
def get_measurements():
    sockets = []
    buffers = []
    for index, addr in enumerate(addresses):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        sock.bind(("", addr[1]))
        sockets.append(sock)
        buffers.append(bytearray())

    # Create list of measurements for accel and rotation
    accels = []
    rotations = []
    for i in range(len(addresses)):
        accels.append([0, 0, 0])
        rotations.append([0, 0, 0])

    out_pose = []

    print("Start collection")

    try:
        debug_i = 0
        while True:
            for index, sock in enumerate(sockets):
                try:
                    # Read any data coming from socket  
                    data, addr = sock.recvfrom(120)
                    stream = data.decode('latin1')
                    buffers[index] += data

                    # # Check if we have received a complete packet
                    # if len(buffers[index]) >= struct.calcsize(format_string):
                    #     # Unpack the packet using struct
                    #     packet = struct.unpack(format_string, buffers[index][:struct.calcsize(format_string)])
                    #     # Extract the data from the packet
                    #     vector = packet[:3]
                    #     quaternion = packet[3:7]
                    #     accuracy_info = packet[7]

                    #     # Do something with the data here
                    #     print(f"Received vector: {vector}, quaternion: {quaternion}, accuracy info: {accuracy_info}")

                    #     # Remove the processed data from the buffer
                    #     buffers[index] = buffers[index][struct.calcsize(format_string):]

                    # Process all complete packets in the buffer
                    if len(buffers[index]) >= format_string_size:
                        offset = buffers[index].find(delimiter)

                        # # Check if we have received a complete packet
                        if offset + format_string_size > len(buffers[index]):
                            break

                        # Unpack the packet using struct
                        packet = struct.unpack_from(format_string, buffers[index][:format_string_size], offset=offset)
                        # Extract the data from the packet
                        # print(packet)
                        sensorId = packet[0]
                        accel = packet[1:4]
                        quaternion = packet[4:8]
                        accuracy_info = packet[8]

                        # # Convert quaternion to euler angles
                        # rot = Rotation.from_quat(list(quaternion))
                        # rot_euler = rot.as_euler('xyz', degrees=True)
                        # print(accel, '\t', rot_euler.tolist())

                        accels[index] = accel
                        rotations[index] = quaternion

                        # Remove the processed data from the buffer
                        buffers[index] = buffers[index][format_string_size:]                
                except socket.timeout:
                    print("Failed read")
                    print(devices[index])
                    pass
            
            # Add to numpy array tuple of accel and rotation
            # Create tuple first then add to numpy array
            temp = []
            for i in range(len(addresses)):
                tu = (accels[i], rotations[i])
                temp.append(tu)
            
            all_data = temp
            out_pose.append(tuple(all_data))

    finally:
        # Close the socket
        for sock in sockets:
            sock.close()

        # Get YYYY-MM-DD_HH-MM-SS
        today = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Output to pkl with date
        print("Saving to pickle")
        with open(f'pose_{today}.pkl', 'wb') as f:
            pickle.dump(out_pose, f)

if __name__ == '__main__':
    # Set port number
    for device in addresses:
        set_SlimeVR_port(device[0], device[1])

    v = multiprocessing.Process(target=verbose)
    m = multiprocessing.Process(target=get_measurements)

    v.start()
    m.start()

    v.join()
    m.join()
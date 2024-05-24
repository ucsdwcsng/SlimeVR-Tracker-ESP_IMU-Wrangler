# Simulate UDP requests to a server
import struct, socket
import datetime, pickle

import numpy as np
from scipy.spatial.transform import Rotation

import multiprocessing, time
import pygame

import vmcp_server

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

all_data = multiprocessing.Manager().list()
mu_lock = multiprocessing.Lock()
pose_mutex = multiprocessing.Lock()
listening = multiprocessing.Value('b', True)

# List of tuples to query IMU data from
# 1st floor addrs
# ip_head_address = '10.42.0.'
# devices = [77, 234, 56, 147, 50, 103]
# devices = [50, 234, 56, 147, 241, 77]

# 5th floor addrs
# ip_head_address = '192.168.1.'
# devices = [119]
# devices = [84, 102, 242, 119, 123, 17, 64]

ip_head_address = '192.168.10.'
devices = [187]

# Timing of recording the data
fps = 60

# Initialize pygame
pygame.init()

# Initialize clock
clock = pygame.time.Clock()
slimevr_pose_data = multiprocessing.Manager().dict()
template_pose_data = {  'unix': 0,
                        'time': 0,
                        'root': [],
                        'bone': {},
                        'device': {},
                        'state': {} }

for key in template_pose_data.keys():
    slimevr_pose_data[key] = template_pose_data[key]

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

def logger():
    out_pose = []
    slimeVR_out_pose = []

    try:
        while True:
            mu_lock.acquire()
            pose_mutex.acquire()
            # if len(all_data) > 0:
            #     # Quaternion outputted by BNO085 is output on pitch, roll, yaw
            #     # DEBUG Steps:
            #     # 1. Record rotation of tracker in two orientations
            #     # 2. Take quaternions and plot one timeframe of quaternion
            #     # 2a. Clear timeframe and plot next timeframe to create animation
            #     quat = all_data[0][0][1]
            #     # Convert quaternion to euler angles
            #     rot = Rotation.from_quat(list(quat))
            #     rot_euler = rot.as_euler('xyz', degrees=True)
                
            #     accel = all_data[0][0][0]
            #     print(accel, end="\t\t")
            #     print(rot_euler.tolist())
            if len(all_data) > 0:
                out_pose.append([time.time(), list(all_data)[0]])
                slimeVR_out_pose.append(slimevr_pose_data.copy())
            mu_lock.release()
            pose_mutex.release()
            # if len(out_pose) > 0:
            #     print("Frame", len(out_pose), out_pose[-1])
            clock.tick(fps)
    finally:
        # Get YYYY-MM-DD_HH-MM-SS
        today = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        vmcp_server.LISTENING = False
        
        # Output to pkl with date
        print("Saving to pickle")
        with open(f'pose_{today}.pkl', 'wb') as f:
            pickle.dump(out_pose, f)
        with open(f'slimeVR_pose_{today}.pkl', 'wb') as f:
            pickle.dump(slimeVR_out_pose, f)
        
def get_measurements():
    sockets = []
    buffers = []
    for index, addr in enumerate(addresses):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.1)
        sock.bind(("", addr[1]))
        sockets.append(sock)
        buffers.append(bytearray())

    # Create list of measurements for accel and rotation
    # Each SlimeVR tracker can have 2 sensors
    accels = [np.array([(0, 0, 0), (0, 0, 0)], dtype=np.float32) for i in range(len(addresses))]
    rotations = [np.array([(None, None, None, None), (None, None, None, None)], dtype=np.float32) for i in range(len(addresses))]

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
                        accel = np.array(packet[1:4], dtype=np.float32)
                        quaternion = np.array(packet[4:8], dtype=np.float32)
                        accuracy_info = packet[8]

                        # # Convert quaternion to euler angles
                        # rot = Rotation.from_quat(list(quaternion))
                        # rot_euler = rot.as_euler('xyz', degrees=True)
                        # print(sensorId, accel, '\t', rot_euler.tolist())

                        accels[index][sensorId] = accel
                        rotations[index][sensorId] = quaternion

                        # Remove the processed data from the buffer
                        buffers[index] = buffers[index][format_string_size:]                
                except socket.timeout:
                    # print("Failed read")
                    # print(devices[index])
                
                    accel_zero = [0, 0, 0]

                    # if len(accels[index]) > 0:
                    #     # If we failed to get a packet, lerp towards 0
                    #     lerp = np.multiply(accels[index], 0.5)
                    #     # Reformat to exclude exponential notation
                    #     formatted = []
                    #     for x in lerp:
                    #         if x < 0.0001:
                    #             formatted.append(0)
                    #         else:   
                    #             formatted.append(x)
                    #     accels[index] = formated
                    # else:
                    #     accels[index] = accel_zero
                    # pass
            
            # Add to numpy array tuple of accel and rotation
            # Create tuple first then add to numpy array
            temp = []
            for i in range(len(addresses)):
                tu = (accels[i], rotations[i])
                temp.append(tu)
            
            mu_lock.acquire()
            if len(all_data) > 0:
                all_data[0] = temp
            else:
                all_data.insert(0, temp)
            mu_lock.release()

    finally:
        # Close the socket
        for sock in sockets:
            sock.close()

if __name__ == '__main__':
    # Set port number
    for device in addresses:
        set_SlimeVR_port(device[0], device[1])

    file_logger = multiprocessing.Process(target=logger)
    imus = multiprocessing.Process(target=get_measurements)
    vmc = multiprocessing.Process(target=vmcp_server.gather_slimeVR_pose_data, args=[slimevr_pose_data, pose_mutex, listening])

    file_logger.start()
    imus.start()
    vmc.start()

    file_logger.join()
    imus.join()
    listening = False
    vmc.join()

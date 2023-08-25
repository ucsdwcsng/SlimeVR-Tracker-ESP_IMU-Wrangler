# Simulate UDP requests to a server
import socket
import struct
import pandas as pd
from scipy.spatial.transform import Rotation

# Assuming the packet has been received and stored in a variable called 'packet'
# Assuming `data` is the binary data received from the network
delimiter = b'\xef'
end_delimiter = b'\xfe'
vector_format = 'fff'
quaternion_format = 'ffff'
# The format string specifies the data types and their order in the packet
format_string = ">x7fBx"
format_string_size = struct.calcsize(format_string)
accuracy_info_format = 'B'

# List of tuples to query IMU data from
addresses = []
addresses.append(('192.168.1.121', 6970))

sockets = []
buffers = []
for addr in addresses:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    sock.bind(("", 6970))
    sockets.append(sock)
    buffers.append(bytearray())

while True:
    for index, sock in enumerate(sockets):
        try:
            # Read any data coming from socket  
            data, addr = sock.recvfrom(1024)
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
            while len(buffers[index]) >= format_string_size:
                offset = buffers[index].find(delimiter)

                # # Check if we have received a complete packet
                if offset + format_string_size > len(buffers[index]):
                    break

                # Unpack the packet using struct
                packet = struct.unpack_from(format_string, buffers[index][:format_string_size], offset=offset)
                # Extract the data from the packet
                # print(packet)
                vector = packet[:3]
                quaternion = packet[3:7]
                accuracy_info = packet[7]

                # # Convert quaternion to euler angles
                rot = Rotation.from_quat(list(quaternion))
                rot_euler = rot.as_euler('xyz', degrees=True)
                print(vector, '\t', rot_euler.tolist())

                # Remove the processed data from the buffer
                buffers[index] = buffers[index][format_string_size:]
                
        except socket.timeout:
            print("Failed read")
            pass
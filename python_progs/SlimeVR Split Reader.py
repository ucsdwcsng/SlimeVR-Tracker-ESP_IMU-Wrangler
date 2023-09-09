# Simulate UDP requests to a server
import re
import socket
import multiprocessing
import struct
from time import sleep

# NOTE: When getting broadcast, string appears after this
#       You need to do the following lines to complete a broadcast packet:
#       
#       length = binary_data[32]
#       unpacked_string = struct.unpack_from(f'{length}s6B', binary_data, offset=33)[0].decode('utf-8')

# These are ordered by integer representation, listed in the dictionary
sensorHeartbeatStruct = '>3xBQ'
sensorBroadcastStruct = '>3xBQ3I12xI'
sensorAccelStruct = '>3xBQ3fB'

sensorBatStruct = '>3xBQ2f'
sensorTapStruct = '>3xBQ2B'
sensorErrStruct = '>3xBQ2B'
sensorInfoStruct = '>3xBQ3B'
sensorRotStruct = '>3xBQ2B4fB'
sensorMagStruct = '>3xBQBf'
sensorSignalStruct = '>3xBQ2B'
sensorTempStruct = '>3xBQBf'

bundleBeginStruct = '>3xBQH'

packetTypeSupported = { 0: (sensorHeartbeatStruct, struct.calcsize(sensorHeartbeatStruct)),
                        3: (sensorBroadcastStruct, struct.calcsize(sensorBroadcastStruct)),
                        4: (sensorAccelStruct, struct.calcsize(sensorAccelStruct)),
                        12: (sensorBatStruct, struct.calcsize(sensorBatStruct)),
                        13: (sensorTapStruct, struct.calcsize(sensorTapStruct)),
                        14: (sensorErrStruct, struct.calcsize(sensorErrStruct)),
                        15: (sensorInfoStruct, struct.calcsize(sensorInfoStruct)),
                        17: (sensorRotStruct, struct.calcsize(sensorRotStruct)),
                        18: (sensorMagStruct, struct.calcsize(sensorMagStruct)),
                        19: (sensorSignalStruct, struct.calcsize(sensorSignalStruct)),
                        20: (sensorTempStruct, struct.calcsize(sensorTempStruct)),
                        100: (bundleBeginStruct, struct.calcsize(bundleBeginStruct))}

zero_seq = re.compile(b'\x00\x00\x00')

# value = struct.unpack('f', bytes)[0]

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
            while True:
                data, addr = sock.recvfrom(2048)
                stream = data.decode('latin1')
                buffers[index] += data

                zero_indexes = [m.start() for m in zero_seq.finditer(buffers[index])]
                packets = []

                # The hare index is the expected index of the next packet
                # Anything before this index is either garbage or part of a packet
                hare_index = 0

                for ind in zero_indexes:
                    if ind == zero_indexes[-1]:
                        # Save the rest of the data for next iteration
                        buffers[index] = buffers[index][ind:]
                        break
                    elif ind < hare_index:
                        # This is garbage data
                        continue
                    else:
                        try:
                            datatype = buffers[index][ind + 3]
                        except IndexError as e:
                            print(len(buffers[index]))
                            print(ind)
                            print(data)
                            # Print actual error
                            print(e)
                            continue

                        if datatype in packetTypeSupported.keys():
                            size = packetTypeSupported[datatype][1]
                            hare_index = ind + packetTypeSupported[datatype][1]
                            packet = None

                            # Check if there is enough data to unpack
                            if len(buffers[index]) < ind + size:
                                # Save the rest of the data for next iteration
                                buffers[index] = buffers[index][ind:]
                                break
                            
                            if datatype == 3:
                                # String is variable length
                                first_half = struct.unpack_from(sensorBroadcastStruct, buffers[index], offset=ind)
                                length = buffers[index][ind + 40]
                                unpacked_string = struct.unpack_from(f'{length}s6B', buffers[index], offset=ind + 41)
                                hare_index += length + 7

                                # Combime structs
                                packet = first_half + unpacked_string
                                
                            else:
                                packet = struct.unpack_from(packetTypeSupported[datatype][0], buffers[index], offset=ind)
                        
                            # if datatype == 4:
                            #     # Accelerometer
                            #     print(packet)

                        if datatype != 0:
                            packets.append(datatype)
                            print(packet)
                        
        except socket.timeout:
            print("Failed read")
            pass
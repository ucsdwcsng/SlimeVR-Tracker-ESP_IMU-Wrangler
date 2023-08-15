# Simulate UDP requests to a server
import socket
import multiprocessing
from time import sleep

# List of tuples to query IMU data from
addresses = []
addresses.append(('192.168.50.120', 6970))

sockets = []
for addr in addresses:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    sock.bind(("", 6970))
    sockets.append(sock)

while True:
    for index, sock in enumerate(sockets):
        try:
            # Read any data coming from socket
            while True:
                data, addr = sock.recvfrom(2048)
                thing = data.decode('utf-8')
                for a in thing:
                    print(ord(a), end=' ', flush=True)
        except socket.timeout:
            print("Failed read")
            pass
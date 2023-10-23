#%%
import struct, socket
import datetime, pickle

import numpy as np
from scipy.spatial.transform import Rotation

import multiprocessing, time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Program to animate acceleration and rotation of IMU from pickle file using matplotlib

# Import the pickle file
imu_data = None
with open('test_rot_test2.pkl', 'rb') as f:
    imu_data = pickle.load(f)

# Data is formated as a list of frames, each frame containing a list of devices
# Each device then contains two lists, one for acceleration and one for rotation

# Extract rotation and acceleration data as separate lists
rot_data = []
acc_data = []

for frame in imu_data:
    device = frame[0][0]
    rot_data.append(device[1])
    acc_data.append(device[0])

# Animate rotation data
fig = plt.figure()
ax = plt.axes(projection='3d')


def rotate(yaw): 
        return np.array([[np.cos(yaw), -np.sin(yaw), 0], 
                         [np.sin(yaw), np.cos(yaw), 0], 
                         [0, 0 ,1]])
        # return np.array([[0, -1, 0], 
        #                  [-1, 0, 0], 
        #                  [0, 0 ,-1]])



# Update function that shows the rotation of the IMU
# Use z axis as up axis 
def update(frame):
    ax.clear()
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    ax.set_title('IMU Rotation')

    # Get rotation data
    rot = frame
    # Get rotation matrix
    rot = Rotation.from_quat(rot)
    matrix = rot.as_matrix()

    
    # matrix = rotate(-np.pi/2) @ matrix 

    # Plot rotation matrix
    ax.quiver(0, 0, 0, matrix[0][0], matrix[1][0], matrix[2][0], length=1, normalize=True, color="tab:red")
    ax.quiver(0, 0, 0, matrix[0][1], matrix[1][1], matrix[2][1], length=1, normalize=True, color="tab:green")
    ax.quiver(0, 0, 0, matrix[0][2], matrix[1][2], matrix[2][2], length=1, normalize=True, color="tab:blue")

    
    # rot_euler = rot.as_euler('xyz', degrees=True)

    # ax.quiver(0, 0, 0, , length=1, normalize=True)
    return ax

print(rot_data)
ani = animation.FuncAnimation(fig, update, frames=rot_data, interval=1/100*1e3)
plt.show()
# %%

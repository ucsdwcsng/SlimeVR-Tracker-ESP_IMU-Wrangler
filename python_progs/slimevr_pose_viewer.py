import struct, socket
import datetime, pickle

import numpy as np
from scipy.spatial.transform import Rotation

import multiprocessing, time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Load slimevr_pose_data file
pose_data = pickle.load(open('slimeVR_pose_2024-05-24_20-05-22.pkl', 'rb'))

"""
template_pose_data = {  'unix': 0,
                        'time': 0,
                        'root': [],
                        'bone': {},
                        'device': {},
                        'state': {} }
"""

# We want to plot root and bone data
combined = []

for frame in pose_data:
    bone_list = []
    for bone in frame['bone']:
        bone_list.append(frame['bone'][bone])

    combined.append([frame['root'], bone_list])

bone_keys = pose_data[0]['bone'].keys()

# All data has Cartesian positions and Quaternion rotations
fig = plt.figure()
plt.title("Slime Pose")
ax = plt.axes(projection='3d')

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

    # Plot root position
    pos_x = frame[0][0][0]
    pos_y = frame[0][0][1]
    pos_z = frame[0][0][2]

    # Get rotation data
    root_rot_x = frame[0][1].x
    root_rot_y = frame[0][1].y
    root_rot_z = frame[0][1].z
    root_rot_w = frame[0][1].w
    root_rot_np = np.array([root_rot_x, root_rot_y, root_rot_z, root_rot_w])

    # Get rotation matrix
    rot = Rotation.from_quat(root_rot_np)
    matrix = rot.as_matrix()

    # Plot rotation matrix
    ax.quiver(pos_x, pos_y, pos_z, matrix[0][0], matrix[1][0], matrix[2][0], length=1, normalize=True, color="tab:red")
    ax.quiver(pos_x, pos_y, pos_z, matrix[0][1], matrix[1][1], matrix[2][1], length=1, normalize=True, color="tab:green")
    ax.quiver(pos_x, pos_y, pos_z, matrix[0][2], matrix[1][2], matrix[2][2], length=1, normalize=True, color="tab:blue")
    # print(pos_x, pos_y, pos_z, root_rot_x, root_rot_y, root_rot_z, root_rot_w)

    # Plot all bone positions
    for i in range(len(bone_keys)):
        bone_x = frame[1][i][0][0]
        bone_y = frame[1][i][0][1]
        bone_z = frame[1][i][0][2]

        bone_rot_x = frame[1][i][1].x
        bone_rot_y = frame[1][i][1].y
        bone_rot_z = frame[1][i][1].z
        bone_rot_w = frame[1][i][1].w

        print(bone_x, bone_y, bone_z, bone_rot_x, bone_rot_y, bone_rot_z, bone_rot_w)

        bone_rot_np = np.array([bone_rot_x, bone_rot_y, bone_rot_z, bone_rot_w])
        rot = Rotation.from_quat(bone_rot_np)
        matrix = rot.as_matrix()

        ax.quiver(bone_x, bone_y, bone_z, matrix[0][0], matrix[1][0], matrix[2][0], length=1, normalize=True, color="tab:red")
        ax.quiver(bone_x, bone_y, bone_z, matrix[0][1], matrix[1][1], matrix[2][1], length=1, normalize=True, color="tab:green")
        ax.quiver(bone_x, bone_y, bone_z, matrix[0][2], matrix[1][2], matrix[2][2], length=1, normalize=True, color="tab:blue")

    return ax

ani = animation.FuncAnimation(fig, update, frames=combined, interval=1/6000000)
plt.show()
# Python IMU Extraction Programs
---
The python programs in this folder are used to extract IMU data from the SlimeVR trackers.

## External_Server.py
---
This program is the server that manages recording the data emitted from the SlimeVR firmware. The output of this program will dump the data into a pickle file along with the date and time of when the recording was finished.

### Setup:
* *You must have SlimeVR running for data to start transmitting to the server.* If the server is not running, the tracker has no idea where to send the extra IMU data.
* *Initial data may not have any data values.* This is because by default the values are populated by 0. It is recommended to induce movement to all trackers so data is initiallized properly.

### Data Format:
The contents of the pickle file are a long list of arrays signifying each frame of the IMU recorded.
- Layer 1: Frames
    * Each index in the first layer of the array is every frame in the recording.

- Layer 2: List of available IMUs
    * Each index in the second layer is a list of trackers that were used in the recording.

- Layer 3: IMU Acceleration and Rotation lists
    * Each index in the third layer is the specific data of that IMU for that frame.
    * 0th index is the acceleration of the IMU
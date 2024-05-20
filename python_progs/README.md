# Python IMU Extraction Programs
---
The python programs in this folder are used to extract IMU data from the SlimeVR trackers.

---
## External_Server.py
---
This program is the server that manages recording the data emitted from the SlimeVR firmware. The output of this program will dump the data into a pickle file along with the date and time of when the recording was finished.

### Setup:
* **You must have SlimeVR running for data to start transmitting to the server.** If the server is not running, the tracker has no idea where to send the extra IMU data.
* **Initial data may not have any data values.** This is because by default the values are populated by 0. It is recommended to induce movement to all trackers so data is initiallized properly.
* **To setup this program, you will need to modify variables inside the code:**
    * `ip_head_address = '192.168.1.'`
        * IP head address represents the IPV4 mask as well as the first part of the IP address representing the tracker.
    * `devices = [1, 2, 3, 4, 5, 6]`
        * Devices represent the last digit of the LAN IPV4 address. This is used to assign unique UDP ports for the trackers.
    * `fps = 60`
        * FPS represents the desired target FPS to record the trackers. This may be 

### Data Format:
The contents of the pickle file are a long list of arrays signifying each frame of the IMU recorded.
- Layer 1: Frames
    * Each index in the first layer of the array is every frame in the recording.

- Layer 2: List of available IMUs
    * Each index in the second layer is a list of trackers that were used in the recording.

- Layer 3: IMU Acceleration and Rotation lists
    * Each index in the third layer is the specific data of that IMU for that frame.
        * 0th index is the acceleration of the IMU in m/s^2. 
        * 1st index is the rotation of the IMU in Quaternion format.

- Layer 4: Sensor specific data
    * **If the contents of this layer for a particular sensor has `NaN`, then that sensor's data has not been initialized yet.**
    * Each index in the 4th layer pertains to which sensor the tracker has.
    * SlimeVR allows auxiliary sensors so there may be a second sensor that is also reading data.
        * 0th index is the first sensor, the sensor that is next to the ESP32.
        * 1st index is the second sensor, the external sensor that is usually attached to the pins of the ESP32.

Data will be encapsulated in the pickle format. Numpy arrays are used to encapsulate the values in float32 datatype.

---
## Rot_Accel_Plot.py
---
This program is used to visualize the rotation of an IMU using `matplotlib`. At the moment, it can only visualize 1 tracker only.


---
## SlimeVR Split Reader.py
---
This program was an initial effort to break away from using SlimeVR's server so as to instead directly get the IMU data. This is not used in favor of the External Server.py program.
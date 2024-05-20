#!/usr/bin/env python3

# A program to manually call the build and remote wifi flashing scripts

import os
import multiprocessing
import subprocess

mcu = 'esp12e'

esp32_cmd = '~/.platformio/penv/bin/python ~/.platformio/packages/framework-arduinoespressif32@3.20007.0/tools/espota.py --auth=SlimeVR-OTA --debug --progress -f .pio/build/esp12e/firmware.bin'
esp12e_cmd = '~/.platformio/penv/bin/python ~/.platformio/packages/framework-arduinoespressif8266/tools/espota.py --auth=SlimeVR-OTA --debug --progress -f .pio/build/esp12e/firmware.bin'

# Choose which kind of device to flash (esp12f or esp32)
ip_head_address = '10.42.0.'
esp12e_devices = [38]
esp32_devices = []
devices = esp12e_devices

addresses = []
for i in range(len(devices)):
    addresses.append(ip_head_address + str(devices[i]))

def flash_and_log(cmd, logfile, ip):
    file = open(logfile, 'w')
    # p = multiprocessing.Process(target=os.system, args=(cmd,), stdout=file, stderr=file)
    # p.start()
    # p.join()
    # if p.exitcode != 0:
    #     print(f"Failed to flash {cmd}")
    s = subprocess.run(cmd, shell=True, stdout=file, stderr=file)
    if s.returncode != 0:
        print(f"Failed to flash {ip}")
    file.close()

# Build the firmware
os.system(f"pio run -e {mcu}")

# Go through every device and flash it at the same time
flash_processes = []
for address in addresses:
    cmd = ""
    if mcu == 'esp32':
        cmd = f"{esp32_cmd} -i {address}"
    elif mcu == 'esp12e':
        cmd = f"{esp12e_cmd} -i {address}"

    p = multiprocessing.Process(target=flash_and_log, args=(cmd, f"flash_{address}.log", address))
    p.start()
    flash_processes.append(p)

for p in flash_processes:
    p.join()

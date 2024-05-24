#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Basic VMC protocol example."""

from math import radians
import numpy as np
import multiprocessing, time
# OSC
from vmcp.osc import OSC
from vmcp.osc.typing import Message
from vmcp.osc.backend.osc4py3 import as_comthreads as backend
# VMC protocol layer
from vmcp.events import (
    Event,
    RootTransformEvent,
    BoneTransformEvent,
    BlendShapeEvent,
    BlendShapeApplyEvent,
    DeviceTransformEvent,
    StateEvent,
    RelativeTimeEvent
)
from vmcp.typing import (
    CoordinateVector,
    Quaternion,
    Bone,
    DeviceType,
    BlendShapeKey as AbstractBlendShapeKey,
    ModelState,
    Timestamp
)

from vmcp.facades import on_receive

def received(event: Event, pose_ref, mutex: multiprocessing.Lock):
    """Receive transmission."""
    global LISTENING  # pylint: disable=global-statement
    # print(event)

    mutex.acquire()
    if isinstance(event, RootTransformEvent):
        x = event.position.x
        y = event.position.y
        z = event.position.z
        pose_ref['root'] = [np.array([x, y, z]), np.array(event.rotation)]
    
    if isinstance(event, BoneTransformEvent):
        x = event.position.x
        y = event.position.y
        z = event.position.z
        pose_ref['bone'][event.joint] = [np.array([x, y, z]), np.array(event.rotation)]

    if isinstance(event, DeviceTransformEvent):
        x = event.position.x
        y = event.position.y
        z = event.position.z
        pose_ref['device'][event.joint] = [np.array([x, y, z]), event.rotation]

    if isinstance(event, RelativeTimeEvent):
        pose_ref['unix'] = time.time()
        pose_ref['time'] = event.delta 
        # LISTENING = False
    mutex.release()

'''
A multiprocessing function that listens for pose data from the SlimeVR server.
Live data can be polled from the curr_pose_data dictionary.
'''
def gather_slimeVR_pose_data(dictRef, mutex, listening):
    try:
        osc = OSC(backend)
        with osc.open():
            # Receiver
            in1 = osc.create_receiver("127.0.0.1", 39539, "receiver1").open()
            on_receive(in1, RootTransformEvent, lambda event : received(event, dictRef, mutex))
            on_receive(in1, BoneTransformEvent, lambda event : received(event, dictRef, mutex))
            on_receive(in1, DeviceTransformEvent, lambda event : received(event, dictRef, mutex))
            on_receive(in1, RelativeTimeEvent, lambda event : received(event, dictRef, mutex))

            # Processing
            while listening:
                osc.run()
    except KeyboardInterrupt:
        osc.close()
        # print("Canceled.")
        return
    finally:
        osc.close()
        return
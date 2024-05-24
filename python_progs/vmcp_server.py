#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Basic VMC protocol example."""

from math import radians
import numpy as np
import time
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
from vmcp.protocol import (
    root_transform,
    bone_transform,
    device_transform,
    blendshape,
    blendshape_apply,
    state,
    time
)

# Facades for easy usage (optional)
from vmcp.facades import on_receive

LISTENING = True
frame_num = 0
curr_pose_data = {  'unix': 0,
                    'time': 0,
                    'root': [],
                    'bone': {},
                    'device': {},
                    'state': {}}

def received(event: Event):
    """Receive transmission."""
    global frame_num
    global LISTENING  # pylint: disable=global-statement
    # print(event)

    if isinstance(event, RootTransformEvent):
        x = event.position.x
        y = event.position.y
        z = event.position.z
        curr_pose_data['root'] = [np.array([x, y, z]), np.array(event.rotation)]
    
    if isinstance(event, BoneTransformEvent):
        x = event.position.x
        y = event.position.y
        z = event.position.z
        curr_pose_data['bone'][event.joint] = [np.array([x, y, z]), np.array(event.rotation)]

    if isinstance(event, DeviceTransformEvent):
        x = event.position.x
        y = event.position.y
        z = event.position.z
        curr_pose_data['device'][event.joint] = [np.array([x, y, z]), event.rotation]

    if isinstance(event, RelativeTimeEvent):
        curr_pose_data['unix'] = time.time()
        curr_pose_data['time'] = event.delta 
        # LISTENING = False

def gather_slimeVR_pose_data():
    try:
        osc = OSC(backend)
        with osc.open():
            # Receiver
            in1 = osc.create_receiver("127.0.0.1", 39539, "receiver1").open()
            on_receive(in1, RootTransformEvent, received)
            on_receive(in1, BoneTransformEvent, received)
            on_receive(in1, DeviceTransformEvent, received)
            # on_receive(in1, StateEvent, received)
            on_receive(in1, RelativeTimeEvent, received)

            # Processing
            while LISTENING:
                osc.run()
            return curr_pose_data
    except KeyboardInterrupt:
        print("Canceled.")
    finally:
        osc.close()
        print(curr_pose_data)

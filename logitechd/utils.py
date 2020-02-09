# SPDX-License-Identifier: MIT

import collections

import pyudev

from typing import List


DeviceInfo = collections.namedtuple('Device', 'vid pid')


def find_usb_parent(device: pyudev.Device, target: List[DeviceInfo]) -> pyudev.Device:
    parent = device.find_parent('usb')
    if parent and 'PRODUCT' in parent.properties:
        for t in target:
            if parent.properties['PRODUCT'].startswith(f'{t.vid:x}/{t.pid:x}'):
                return parent

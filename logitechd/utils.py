# SPDX-License-Identifier: MIT

import dataclasses

import pyudev

from typing import List, Optional


@dataclasses.dataclass
class DeviceInfo(object):
    bus: int = 0x03
    vid: Optional[int] = None
    pid: Optional[int] = None

    def __str__(self) -> str:
        if self.vid is not None and self.pid is not None:
            return f'DeviceInfo({hex(self.bus)}, {hex(self.vid)}, {hex(self.pid)})'
        return f'DeviceInfo(unknown)'


def find_usb_parent(device: pyudev.Device, target: List[DeviceInfo]) -> pyudev.Device:
    if not device:
        return

    parent = device.find_parent('usb')
    if parent and 'PRODUCT' in parent.properties:
        for t in target:
            if parent.properties['PRODUCT'].startswith(f'{t.vid:x}/{t.pid:x}'):
                return parent

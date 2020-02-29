# SPDX-License-Identifier: MIT

import dataclasses

from typing import List, Dict, Optional

import pyudev

import logitechd.device
import logitechd.hidraw


@dataclasses.dataclass
class DeviceInfo(object):
    bus: int = 0x03
    vid: Optional[int] = None
    pid: Optional[int] = None

    def __str__(self) -> str:
        if self.vid is not None and self.pid is not None:
            return f'DeviceInfo({hex(self.bus)}, {hex(self.vid)}, {hex(self.pid)})'
        return f'DeviceInfo(unknown)'


def find_hidraw_children(device: pyudev.Device) -> pyudev.Device:
    for children in device.children:
        if 'SUBSYSTEM' in children.properties and children.properties['SUBSYSTEM'] == 'hidraw':
            yield children


def populate_device_tree(device: pyudev.Device, receiver_info: DeviceInfo,
                         devices: Dict[str, 'logitechd.device.Device']) -> None:
    tree_parent: Optional[logitechd.hidraw.Hidraw] = None
    tree_children: List[logitechd.hidraw.Hidraw] = []

    # discover tree
    for children in find_hidraw_children(device):
        hidraw = logitechd.hidraw.Hidraw(children.device_node)
        if hidraw.has_vendor_page:  # supports vendor protocol
            if hidraw.info == receiver_info:  # receiver
                tree_parent = hidraw
            else:  # device
                tree_children.append(hidraw)

    # populate tree
    if tree_parent:
        devices[tree_parent.path] = logitechd_parent = logitechd.device.Device(tree_parent)
        for children in tree_children:
            logitechd_children = logitechd.device.Device(children, logitechd_parent)
            devices[children.path] = logitechd_children
            logitechd_parent.children.append(logitechd_children)

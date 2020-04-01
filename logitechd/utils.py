# SPDX-License-Identifier: MIT

import dataclasses
import typing

from typing import List, Dict, Optional, Union

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


T = typing.TypeVar('T')


def flatten(items: List[Union[List[T], T]]) -> List[T]:
    '''
    Flattens lists
    Example:
        flatten([0x01, 0x02, [0x03, 0x04, 0x05], 0x06]) == [0x01, 0x02, 0x03, 0x04, 0x05, 0x06]
    '''
    ret = []
    for item in items:
        if isinstance(item, list):
            for i in item:
                ret.append(i)
        else:
            ret.append(item)
    return ret


def ljust(buf: List[int], size: int, char: int = 0x00) -> List[int]:
    '''
    Pads buffer to the right in order to acheive the requested size
    '''
    if len(buf) >= size:
        return buf

    return buf + [char] * (size - len(buf))


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

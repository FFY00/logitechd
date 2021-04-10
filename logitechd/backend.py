# SPDX-License-Identifier: MIT

import abc
import dataclasses

from typing import Optional, Sequence, Set, Tuple


# backend helper data


@dataclasses.dataclass
class _DeviceInfo(object):
    bus: int = 0x03
    vid: Optional[int] = None
    pid: Optional[int] = None

    def __str__(self) -> str:
        if self.vid is not None and self.pid is not None:
            return f'DeviceInfo({hex(self.bus)}, {hex(self.vid)}, {hex(self.pid)})'
        return 'DeviceInfo(unknown)'

    @property
    def as_tuple(self) -> Tuple[int, int, int]:
        if not self.vid or not self.pid:
            raise ValueError(f'Device does not have VID or PID: vid={self.vid}, pid={self.pid}')
        return self.bus, self.vid, self.pid


_TARGET_DEVICES = [
    # Wired
    _DeviceInfo(vid=0x46d, pid=0xc33c),  # G513
    _DeviceInfo(vid=0x46d, pid=0xc33e),  # G915
    _DeviceInfo(vid=0x46d, pid=0xc33f),  # G815
    # Receivers
    _DeviceInfo(vid=0x46d, pid=0xc52b),  # Unifying
    _DeviceInfo(vid=0x46d, pid=0xc539),  # Lightspeed 1.0
    _DeviceInfo(vid=0x46d, pid=0xc53a),  # Powerplay (Lightspeed 1.0)
    _DeviceInfo(vid=0x46d, pid=0xc53f),  # Lightspeed 1.1
    _DeviceInfo(vid=0x46d, pid=0xc541),  # Lightspeed 1.1 v2
]


# backend abstractions


class Device(metaclass=abc.ABCMeta):
    '''HID++ device ABC'''

    @abc.abstractmethod
    def read(self) -> Sequence[int]:
        '''Reads a HID++ report from the device'''

    @abc.abstractmethod
    def write(self, data: Sequence[int]) -> None:
        '''Writes a HID++ report from to the device'''


class Backend(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def devices(self) -> Set[Device]:
        '''
        Set of connected devices

        Receivers are also considered considered "devices" and should be
        included in this Sequence.
        '''
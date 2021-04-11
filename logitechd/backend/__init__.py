# SPDX-License-Identifier: MIT

import abc
import dataclasses
import platform

from typing import Optional, Sequence, Set, Tuple

import logitechd.protocol


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


class IODevice(metaclass=abc.ABCMeta):
    '''HID++ IO device ABC'''

    @abc.abstractmethod
    def read(self) -> Sequence[int]:
        '''Reads a HID++ report from the device'''

    @abc.abstractmethod
    def write(self, data: Sequence[int]) -> None:
        '''Writes a HID++ report to the device'''


class Backend(metaclass=abc.ABCMeta):
    '''
    IO backend ABC

    Backends must discover devices, call logitechd.protocol.construct_device
    with a IODevice instance for each device, and save the returned Device
    instance, so that it can be returned in the ``device`` property.
    '''

    @property
    @abc.abstractmethod
    def devices(self) -> Set[logitechd.protocol.Device]:
        '''
        Set of connected devices

        Receivers are also considered considered "devices" and should be
        included in this set.
        '''


# helpers


def construct_backend() -> Backend:
    '''Instaceates the correct backend for this system'''
    system = platform.uname().system
    if system == 'Linux':
        import logitechd.backend.hidraw

        return logitechd.backend.hidraw.HidrawBackend()
    else:
        raise NotImplementedError('Unsupported operating system')

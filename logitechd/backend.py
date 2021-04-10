# SPDX-License-Identifier: MIT

import abc

from typing import Sequence, Set


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

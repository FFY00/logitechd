# SPDX-License-Identifier: MIT

from __future__ import annotations

import abc
import typing


if typing.TYPE_CHECKING:
    import logitechd.backend


class Device(metaclass=abc.ABCMeta):
    '''Base device class'''

    def __init__(self, io: logitechd.backend.IODevice) -> None:
        self._io = io
        self._init_protocol()

    def _init_protocol(self) -> None:
        '''
        Protocol initialization.

        May be overridden by subclasses.
        '''
        pass

    @property
    def io(self) -> logitechd.backend.IODevice:
        '''IO interface'''
        return self._io

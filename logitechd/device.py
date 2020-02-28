# SPDX-License-Identifier: MIT

import logitechd.hidraw


class Device(object):
    '''
    Represents a device
    '''

    def __init__(self, hidraw: logitechd.hidraw.Hidraw) -> None:
        self._hidraw: logitechd.hidraw.Hidraw = hidraw

    @property
    def path(self) -> str:
        return self._hidraw.path

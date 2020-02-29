# SPDX-License-Identifier: MIT

from typing import List, Optional

import logitechd.hidraw


class Device(object):
    '''
    Represents a device
    '''

    def __init__(self, hidraw: logitechd.hidraw.Hidraw, parent: Optional['Device'] = None) -> None:
        self._hidraw: logitechd.hidraw.Hidraw = hidraw
        self._parent: Optional[Device] = parent
        self.children: List[Device] = []

    def __del__(self) -> None:
        self.destroy()

    def destroy(self) -> None:
        '''
        Removes device from parent device children
        '''
        if self._parent and self in self._parent.children:
            self._parent.children.remove(self)

    @property
    def path(self) -> str:
        return self._hidraw.path

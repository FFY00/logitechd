# SPDX-License-Identifier: MIT

from typing import List, Optional

import logitechd.hidraw
import logitechd.hidpp


class Device(object):
    '''
    Represents a device
    '''

    def __init__(self, hidraw: logitechd.hidraw.Hidraw, parent: Optional['Device'] = None) -> None:
        self._hidraw: logitechd.hidraw.Hidraw = hidraw
        self._parent: Optional[Device] = parent
        self.children: List[Device] = []

        self._read_buf: List[int] = []

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

    def read(self, timeout: int = 1) -> List[int]:
        '''
        Reads data from the device node

        Splits HID++ reports if received multiple concatenated reports
        '''
        buf = self._read_buf if self._read_buf else self._hidraw.read(timeout)

        if buf and buf[0] in logitechd.hidpp.REPORT_SIZE.keys():
            report_size = logitechd.hidpp.REPORT_SIZE[buf[0]]
            if len(buf) != report_size:
                self._read_buf = buf[report_size:]
                buf = buf[:report_size]

        return buf

    def write(self, buf: List[int]) -> None:
        '''
        Writes data to the device node
        '''
        self._hidraw.write(buf)

    def command(self, buf: List[int], timeout: int = 1) -> List[int]:
        '''
        Writes data to the device node and reads the reply
        '''
        self.write(buf)
        return self.read(timeout)

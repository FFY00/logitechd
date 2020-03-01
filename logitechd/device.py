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
        self._online = False
        self._parent: Optional[Device] = parent
        self.children: List[Device] = []

        self._read_buf: List[int] = []

        self._probe_hidpp()

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

    @property
    def online(self) -> bool:
        return self._online

    def _probe_hidpp(self) -> None:
        buf = self.command([0x10, 0xff, 0x00, 0x10, 0x00, 0x00, 0x00])  # HID++ - Protocol version discover routine

        if buf[2] == 0x8f:  # device is HID++ 1.0
            if self._parent:
                print(f'{self.path} ({self._hidraw.name}): Device offline')
                return

            print(f'{self.path} ({self._hidraw.name}): HID++ 1.0 (index {buf[1]:x})')
            self._online = True

        elif buf[2] == 0x00:  # device is HID++ 2.0
            print(f'{self.path} ({self._hidraw.name}): HID++ 2.0 (index {buf[1]:x})')
            self._online = True

        else:
            print(f'{self.path} ({self._hidraw.name}): Unknown protocol')

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
            else:
                self._read_buf = []

        return buf

    def write(self, buf: List[int]) -> None:
        '''
        Writes data to the device node
        '''
        self._hidraw.write(buf)

    def command(self, buf: List[int], timeout: int = 1) -> List[int]:
        '''
        Writes data to the device node and reads the reply

        This clears the read buffer, to make sure we don't read the wrong reply.
        Make sure you process everything in the buffer before calling.
        '''
        self.clear_read_buffer()
        self.write(buf)
        return self.read(timeout)

    def clear_read_buffer(self) -> None:
        '''
        Clears the internal read buffer as well as the hidraw buffer
        '''
        self._read_buf = []
        buf = self._hidraw.read(timeout=0.001)
        while buf:
            buf = self._hidraw.read(timeout=0.001)

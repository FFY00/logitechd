# SPDX-License-Identifier: MIT

import fcntl
import os

import logitechd.hidraw


class Device(object):
    '''
    Represents a device
    '''

    def __init__(self, path):
        self._path = path
        self._fd = open(self._path, 'rb+')
        fcntl.fcntl(self._fd, fcntl.F_SETFL, os.O_NONBLOCK)

        self.hidraw = logitechd.hidraw.Hidraw(self._fd)

        self.name = logitechd.hidraw._HIDIOCGRAWNAME(self._fd)
        print(f'name = {self.name}')
        self.info = logitechd.hidraw._HIDIOCGRAWINFO(self._fd)
        print(f'info = {self.info}')
        self.rdesc_size = logitechd.hidraw._HIDIOCGRDESCSIZE(self._fd)
        print(f'rdesc_size = {self.rdesc_size}')
        self.rdesc = logitechd.hidraw._HIDIOCGRDESC(self._fd, self.rdesc_size)
        print(f'rdesc = {self.rdesc}')

        print('=' * 30)

        self.name = self.hidraw.name
        print(f'name = {self.name}')
        self.info = self.hidraw.info
        print(f'info = {self.info}')
        self.rdesc_size = self.hidraw.report_descriptor_size
        print(f'rdesc_size = {self.rdesc_size}')
        self.rdesc = self.hidraw.report_descriptor
        print(f'rdesc = {self.rdesc}')

        self._get_report_descriptor()
        assert self._is_vendor()

    @property
    def path(self):
        return self._path

    def _get_report_descriptor(self):
        '''
        Gets the report descriptor of a hidraw node

        TODO: Translate include/uapi/linux/hidraw.h to python definitions and
              trigger an ioctl to get the report descriptor (HIDIOCGRDESC)
        '''

    def _is_vendor(self) -> bool:
        '''
        Parses the report descriptor and makes sure it icludes at least one
        vendor usage page

        This is used to make sure we are talking to the correct node (supports
        vendor/arbitary packets)
        '''
        return True

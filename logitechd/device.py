# SPDX-License-Identifier: MIT

import fcntl
import os


class Device(object):
    '''
    Represents a device
    '''

    def __init__(self, path):
        self._path = path
        self._fd = open(self._path, 'rb+')
        fcntl.fcntl(self._fd, fcntl.F_SETFL, os.O_NONBLOCK)

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

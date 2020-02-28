# SPDX-License-Identifier: MIT

import array
import ctypes
import fcntl
import os

from typing import BinaryIO, List, Optional, Union

from logitechd.utils import DeviceInfo


'''
Writing Python wrappers for C APIs is usually hard, and it is the case of
ioctl(s). I tried to write a simple to use and somewhat readable pytyhonic
wrapper for this API. It is still a pain to use... but hopefully we won't have
to touch this code a lot. If anyone has suggestions on how this could be
improved, they are more than welcome!
'''


class IOCTL(object):
    '''
    Constructs and performs ioctl(s)

    See include/asm-generic/ioctl.h
    '''
    NRBITS: int = 8
    TYPEBITS: int = 8

    SIZEBITS: int = 14
    DIRBITS: int = 2

    NRMASK: int = (1 << NRBITS) - 1
    TYPEMASK: int = (1 << TYPEBITS) - 1
    SIZEMASK: int = (1 << SIZEBITS) - 1
    DIRMASK: int = (1 << DIRBITS) - 1

    NRSHIFT: int = 0
    TYPESHIFT: int = NRSHIFT + NRBITS
    SIZESHIFT: int = TYPESHIFT + TYPEBITS
    DIRSHIFT: int = SIZESHIFT + SIZEBITS

    class Direction:
        NONE = 0
        WRITE = 1
        READ = 2

    def __init__(self, dir: int, ty: str, nr: int, size: int = 0, bad: bool = False) -> None:
        assert self.Direction.NONE <= dir <= self.Direction.READ + self.Direction.WRITE

        if dir == self.Direction.NONE:
            size = 0
        elif not bad:
            assert size, size <= self.SIZEMASK

        self.op = (dir << self.DIRSHIFT) | \
                  (ord(ty) << self.TYPESHIFT) | \
                  (nr << self.NRSHIFT) | \
                  (size << self.SIZESHIFT)

    def perform(self, fd: BinaryIO, buf: Optional[Union[str, bytes, 'array.array[int]']] = None) -> bytearray:
        '''
        Performs the ioctl
        '''
        size = self.unpack_size(self.op)

        if buf is None:
            buf = (size * '\x00').encode()

        return bytearray(fcntl.ioctl(fd, self.op, buf))  # type: ignore

    @classmethod
    def unpack_dir(cls, nr: int) -> int:
        return (nr >> cls.DIRSHIFT) & cls.DIRMASK

    @classmethod
    def unpack_type(cls, nr: int) -> int:
        return (nr >> cls.TYPESHIFT) & cls.TYPEMASK

    @classmethod
    def unpack_nr(cls, nr: int) -> int:
        return (nr >> cls.NRSHIFT) & cls.NRMASK

    @classmethod
    def unpack_size(cls, nr: int) -> int:
        return (nr >> cls.SIZESHIFT) & cls.SIZEMASK

    @classmethod
    def IO(cls, ty: str, nr: int) -> 'IOCTL':
        '''
        Default constructor for no direction
        '''
        return cls(cls.Direction.NONE, ty, nr)

    @classmethod
    def IOR(cls, ty: str, nr: int, size: int) -> 'IOCTL':
        '''
        Default constructor for read
        '''
        return cls(cls.Direction.READ, ty, nr, size)

    @classmethod
    def IOW(cls, ty: str, nr: int, size: int) -> 'IOCTL':
        '''
        Default constructor for write
        '''
        return cls(cls.Direction.WRITE, ty, nr, size)

    @classmethod
    def IORW(cls, ty: str, nr: int, size: int) -> 'IOCTL':
        '''
        Default constructor for read & write
        '''
        return cls(cls.Direction.READ | cls.Direction.WRITE, ty, nr, size)


class Hidraw(object):
    '''
    Represents a hidraw node

    See linux/hidraw.h
    '''
    HIDIOCGRDESCSIZE = 0x01
    HIDIOCGRDESC = 0x02
    HIDIOCGRAWINFO = 0x03
    HIDIOCGRAWNAME = 0x04
    HIDIOCGRAWPHYS = 0x05
    HIDIOCSFEATURE = 0x06
    HIDIOCGFEATURE = 0x07

    HID_NAME_SIZE = 1024

    class hidraw_report_descriptor(ctypes.Structure):
        HID_MAX_DESCRIPTOR_SIZE = 4096
        _fields_ = [
            ('size', ctypes.c_uint),
            ('value', ctypes.c_ubyte * HID_MAX_DESCRIPTOR_SIZE),
        ]

    class hidraw_devinfo(ctypes.Structure):
        _fields_ = [
            ('bustype', ctypes.c_uint),
            ('vendor', ctypes.c_ushort),
            ('product', ctypes.c_ushort),
        ]

    def __init__(self, path: str) -> None:
        self._path = path
        self._fd = open(path, 'rb+')
        fcntl.fcntl(self._fd, fcntl.F_SETFL, os.O_NONBLOCK)

    def __str__(self) -> str:
        return f'Hidraw({self.path})'

    @property
    def path(self) -> str:
        return self._path

    @property
    def report_descriptor_size(self) -> int:
        '''
        Size of the report descriptor of the hidraw node
        '''
        return ctypes.c_uint.from_buffer(
               IOCTL.IOR('H', self.HIDIOCGRDESCSIZE, ctypes.sizeof(ctypes.c_uint)).perform(self._fd)).value

    @property
    def report_descriptor(self) -> List[int]:
        '''
        Report descriptor of the hidraw node
        '''
        # fcntl.ioctl does not support such big buffer sizes when using the default buffer so we need to provide our own buffer
        buf = array.array('B', self.report_descriptor_size.to_bytes(4, 'little') +
                          self.hidraw_report_descriptor.HID_MAX_DESCRIPTOR_SIZE * b'\x00')

        IOCTL.IOR('H', self.HIDIOCGRDESC, ctypes.sizeof(self.hidraw_report_descriptor)).perform(self._fd, buf=buf)

        ret = self.hidraw_report_descriptor.from_buffer(buf)
        return list(ret.value)[:ret.size]

    @property
    def info(self) -> DeviceInfo:
        '''
        Device info of the hidraw node
        '''
        dev_info = self.hidraw_devinfo.from_buffer(
                   IOCTL.IOR('H', self.HIDIOCGRAWINFO, ctypes.sizeof(self.hidraw_devinfo)).perform(self._fd))

        return DeviceInfo(dev_info.bustype, dev_info.vendor, dev_info.product)

    @property
    def name(self) -> str:
        '''
        HID name of the hidraw node
        '''
        return IOCTL.IOR('H', self.HIDIOCGRAWNAME, self.HID_NAME_SIZE).perform(self._fd).decode('utf-8')

    @property
    def has_vendor_page(self) -> bool:
        return True

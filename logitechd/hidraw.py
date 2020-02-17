# SPDX-License-Identifier: MIT

import ctypes
import fcntl

import array
import struct


class IOCTL(object):
    '''
    Allows us to calculate and preform ioctl(s)

    See include/asm-generic/ioctl.h (internal kernel header)
    '''
    NRBITS = 8
    TYPEBITS = 8

    SIZEBITS = 14
    DIRBITS = 2

    NRMASK = (1 << NRBITS) - 1
    TYPEMASK = (1 << TYPEBITS) - 1
    SIZEMASK = (1 << SIZEBITS) - 1
    DIRMASK = (1 << DIRBITS) - 1

    NRSHIFT = 0
    TYPESHIFT = NRSHIFT + NRBITS
    SIZESHIFT = TYPESHIFT + TYPEBITS
    DIRSHIFT = SIZESHIFT + SIZEBITS

    class Direction:
        NONE = 0
        WRITE = 1
        READ = 2

    def __init__(self, dir: int, ty, nr, size=0, bad=False):
        assert self.Direction.NONE <= dir <= self.Direction.READ + self.Direction.WRITE

        if dir == self.Direction.NONE:
            size = 0
        #elif not bad:
        #assert size, size <= self.SIZEMASK

        self.op = (dir << self.DIRSHIFT) | \
                  (ord(ty) << self.TYPESHIFT) | \
                  (nr << self.NRSHIFT) | \
                  (size << self.SIZESHIFT)

    def perform(self, fd, buf=None):
        self.perform_ioctl(fd, self.op, buf)

    @classmethod
    def perform_ioctl(cls, fd, op, buf=None):
        size = cls.unpack_size(op)

        if buf is None:
            buf = size * '\x00'

        return fcntl.ioctl(fd, op, buf)

    @classmethod
    def IO(cls, ty, nr):
        return cls(cls.Direction.NONE, ty, nr)

    @classmethod
    def IOR(cls, ty, nr, size):
        return cls(cls.Direction.READ, ty, nr, size)

    @classmethod
    def IOW(cls, ty, nr, size):
        return cls(cls.Direction.WRITE, ty, nr, size)

    @classmethod
    def IORW(cls, ty, nr, size):
        return cls(cls.Direction.READ | cls.Direction.WRITE, ty, nr, size)

    @classmethod
    def unpack_dir(cls, nr):
        return (nr >> cls.DIRSHIFT) & cls.DIRMASK

    @classmethod
    def unpack_type(cls, nr):
        return (nr >> cls.TYPESHIFT) & cls.TYPEMASK

    @classmethod
    def unpack_nr(cls, nr):
        return (nr >> cls.NRSHIFT) & cls.NRMASK

    @classmethod
    def unpack_size(cls, nr):
        return (nr >> cls.SIZESHIFT) & cls.SIZEMASK


class Hidraw(object):
    '''
    Implements hidraw's ioctl methods

    See linux/hidraw.h (public kernel header)
    '''
    HIDIOCGRDESCSIZE = 0x01
    HIDIOCGRDESC = 0x02
    HIDIOCGRAWINFO = 0x03
    HIDIOCGRAWNAME = 0x04
    HIDIOCGRAWPHYS = 0x05
    HIDIOCSFEATURE = 0x06
    HIDIOCGFEATURE = 0x07

    class hidraw_report_descriptor(ctypes.Structure):
        HID_MAX_DESCRIPTOR_SIZE = 4096
        _fields_ = [
            ('size', ctypes.c_uint),
            ('value', ctypes.c_ubyte * HID_MAX_DESCRIPTOR_SIZE),
        ]

    class hidraw_devinfo(ctypes.Structure):
        _fields_ = [
            ('bustype', ctypes.c_uint),
            ('vendor', ctypes.c_short),
            ('product', ctypes.c_short),
        ]

    def __init__(self, fd):
        self._fd = fd
        self.str_size = 1024

    @property
    def report_descriptor_size(self):
        return IOCTL.IOR('H', self.HIDIOCGRDESCSIZE, ctypes.sizeof(ctypes.c_int)).perform(self._fd)

    @property
    def report_descriptor(self):
        return IOCTL.IOR('H', self.HIDIOCGRDESC, ctypes.sizeof(self.hidraw_report_descriptor)).perform(self._fd)

    @property
    def info(self):
        return IOCTL.IOR('H', self.HIDIOCGRAWINFO, ctypes.sizeof(self.hidraw_devinfo)).perform(self._fd)

    @property
    def name(self):
        return (ctypes.c_char * self.str_size)(IOCTL.IOR('H', self.HIDIOCGRAWNAME, self.str_size).perform(self._fd))

    @property
    def phys(self):
        return IOCTL.IOR('H', self.HIDIOCGRAWPHYS, size=1).perform(self._fd)

    @property
    def feature(self):
        return IOCTL.IOR('H', self.HIDIOCGFEATURE, size=IOCTL.SIZEMASK).perform(self._fd)

    @feature.setter
    def feature(self):
        return IOCTL.IOR('H', self.HIDIOCSFEATURE, size=IOCTL.SIZEMASK).perform(self._fd)


def _ioctl(fd, EVIOC, code, return_type, buf=None):
    size = struct.calcsize(return_type)
    if buf is None:
        buf = size * '\x00'
    abs = fcntl.ioctl(fd, EVIOC(code, size), buf)
    return struct.unpack(return_type, abs)


# extracted from <asm-generic/ioctl.h>
_IOC_WRITE = 1
_IOC_READ = 2

_IOC_NRBITS = 8
_IOC_TYPEBITS = 8
_IOC_SIZEBITS = 14
_IOC_DIRBITS = 2

_IOC_NRSHIFT = 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_DIRSHIFT = _IOC_SIZESHIFT + _IOC_SIZEBITS


# define _IOC(dir,type,nr,size) \
# 	(((dir)  << _IOC_DIRSHIFT) | \
# 	 ((type) << _IOC_TYPESHIFT) | \
# 	 ((nr)   << _IOC_NRSHIFT) | \
# 	 ((size) << _IOC_SIZESHIFT))
def _IOC(dir, type, nr, size):
    return ((dir << _IOC_DIRSHIFT) |
            (ord(type) << _IOC_TYPESHIFT) |
            (nr << _IOC_NRSHIFT) |
            (size << _IOC_SIZESHIFT))


# define _IOR(type,nr,size)	_IOC(_IOC_READ,(type),(nr),(_IOC_TYPECHECK(size)))
def _IOR(type, nr, size):
    return _IOC(_IOC_READ, type, nr, size)


# define _IOW(type,nr,size)	_IOC(_IOC_WRITE,(type),(nr),(_IOC_TYPECHECK(size)))
def _IOW(type, nr, size):
    return _IOC(_IOC_WRITE, type, nr, size)


# define HIDIOCGRDESCSIZE	_IOR('H', 0x01, int)
def _IOC_HIDIOCGRDESCSIZE(none, len):
    return _IOR('H', 0x01, len)


def _HIDIOCGRDESCSIZE(fd):
    """ get report descriptors size """
    type = 'i'
    return int(*_ioctl(fd, _IOC_HIDIOCGRDESCSIZE, None, type))


# define HIDIOCGRDESC		_IOR('H', 0x02, struct hidraw_report_descriptor)
def _IOC_HIDIOCGRDESC(none, len):
    return _IOR('H', 0x02, len)


def _HIDIOCGRDESC(fd, size):
    """ get report descriptors """
    format = "I4096c"
    value = '\0' * 4096
    tmp = struct.pack("i", size) + value[:4096].encode('utf-8').ljust(4096, b'\0')
    _buffer = array.array('B', tmp)
    fcntl.ioctl(fd, _IOC_HIDIOCGRDESC(None, struct.calcsize(format)), _buffer)
    size, = struct.unpack("i", _buffer[:4])
    value = _buffer[4:size + 4]
    return size, value


# define HIDIOCGRAWINFO		_IOR('H', 0x03, struct hidraw_devinfo)
def _IOC_HIDIOCGRAWINFO(none, len):
    return _IOR('H', 0x03, len)


def _HIDIOCGRAWINFO(fd):
    """ get hidraw device infos """
    type = 'ihh'
    return _ioctl(fd, _IOC_HIDIOCGRAWINFO, None, type)


# define HIDIOCGRAWNAME(len)     _IOC(_IOC_READ, 'H', 0x04, len)
def _IOC_HIDIOCGRAWNAME(none, len):
    return _IOC(_IOC_READ, 'H', 0x04, len)


def _HIDIOCGRAWNAME(fd):
    """ get device name """
    type = 1024 * 'c'
    cstring = _ioctl(fd, _IOC_HIDIOCGRAWNAME, None, type)
    string = b''.join(cstring).decode('utf-8')
    return "".join(string).rstrip('\x00')

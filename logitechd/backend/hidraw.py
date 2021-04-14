# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
import os
import sys
import threading

from types import TracebackType
from typing import List, Optional, Sequence, Set, Type

import ioctl.hidraw
import pyudev
import treelib

import logitechd.backend
import logitechd.protocol


if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


class HidrawInterface(logitechd.backend.IODeviceInterface):
    '''Linux hidraw read/write interface'''

    def __init__(self, hidraw: ioctl.hidraw.Hidraw) -> None:
        self._hidraw = hidraw

    def read(self) -> Sequence[int]:
        return list(os.read(self._hidraw.fd, 64))

    def write(self, data: Sequence[int]) -> None:
        os.write(self._hidraw.fd, bytes(data))


class HidrawDevice(logitechd.backend.IODevice):
    '''Linux hidraw device'''
    _hidraw: ioctl.hidraw.Hidraw

    __open_nodes: List[str] = []

    def __init__(
        self,
        path: Optional[str] = None,
        *,
        hidraw: Optional[ioctl.hidraw.Hidraw] = None,
    ) -> None:
        if path and hidraw:
            raise ValueError('Suplied both `path` and `hidraw` arguments, only one is aceptable.')
        elif path:
            self._hidraw = ioctl.hidraw.Hidraw(path)
        elif hidraw:
            self._hidraw = hidraw
        else:
            raise ValueError('Missing arguments: please provide either a `path` or `hidraw` argument')

        if self.path in self.__open_nodes:
            raise KeyError(f'Device `{self.path}` already open')
        self.__open_nodes.append(self.path)

        self._interface = HidrawInterface(self._hidraw)
        self._lock = threading.Lock()

    @property
    def path(self) -> str:
        assert isinstance(self._hidraw.path, str)  # make mypy happy
        return self._hidraw.path

    @property
    def name(self) -> str:
        assert isinstance(self._hidraw.name, str)  # make mypy happy
        return self._hidraw.name

    def __enter__(self) -> logitechd.backend.IODeviceInterface:
        self._lock.acquire()
        return self._interface

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Literal[False]:
        self._lock.release()
        return False  # False means we did not handle the exception :)


class HidrawBackend(logitechd.backend.Backend):
    '''
    Linux hidraw backend

    Looks for devices in UDEV, it monitors UDEV for changes in different thread(s).

    Assumes only one hidraw node with a vendor usage page will be exported by the
    hid-logitech-dj driver.
    '''

    def __init__(self) -> None:
        self.__logger = logging.getLogger(self.__class__.__name__)
        self._tree = treelib.Tree()
        self._devices = self._tree.create_node(identifier='devices')

        self._setup_udev()

    @property
    def devices(self) -> Set[logitechd.protocol.Device]:
        return {
            node.data for node in self._tree.all_nodes_itr()
            if node.identifier != 'devices'
        }

    def _setup_udev(self) -> None:
        '''Setup UDEV and register observers to look for devices and populate the device tree'''
        udev_context = pyudev.Context()

        # register parent monitor
        self._monitor_usb = pyudev.Monitor.from_netlink(udev_context)
        self._monitor_usb.filter_by('usb')
        self._observer_usb = pyudev.MonitorObserver(self._monitor_usb, self._event_handler_parent)

        # register child monitor
        self._monitor_hidraw = pyudev.Monitor.from_netlink(udev_context)
        self._monitor_hidraw.filter_by('hidraw')
        self._observer_hidraw = pyudev.MonitorObserver(self._monitor_hidraw, self._event_handler_hidraw)

        # trigger the parent event handler manually for initial population
        for device in udev_context.list_devices(subsystem='usb'):
            self._event_handler_parent('add', device)

        self.__logger.info('Device tree populated:')
        for line in self._tree.show(stdout=False).splitlines():
            self.__logger.info('\t' + line)

        # start observers
        self._observer_usb.start()
        self._observer_hidraw.start()

    def _event_handler_parent(self, action: str, device: pyudev.Device) -> None:
        '''
        Find devices and populate the tree
        '''
        if action == 'add' and device.device_node and 'PRODUCT' in device.properties:
            for target in logitechd.backend._TARGET_DEVICES:
                if device.properties['PRODUCT'].startswith(f'{target.vid:x}/{target.pid:x}'):
                    self._populate_device_tree(device, target)

    def _event_handler_hidraw(self, action: str, device: pyudev.Device) -> None:
        '''
        udev event handler for node (hidraw devices created by the hid-logitech-dj kernel driver) actions
        '''
        if action == 'remove' and device.device_node:
            if device.device_node in self._tree:
                self._tree.remove_node(device.device_node)

    def _find_hidraw_children(self, device: pyudev.Device) -> pyudev.Device:
        '''Find device children in the hidraw subsystem'''
        for child in device.children:
            if 'SUBSYSTEM' in child.properties and child.properties['SUBSYSTEM'] == 'hidraw':
                yield child

    def _populate_device_tree(
        self,
        usb_device: pyudev.Device,
        target_info: logitechd.backend._DeviceInfo,
    ) -> None:
        '''
        Look at children of the USB device, find the hidraw nodes and populate the tree.
        '''
        parent: Optional[HidrawDevice] = None
        children: List[HidrawDevice] = []

        # discover hidraw node of the parent and save the children
        for child in self._find_hidraw_children(usb_device):

            try:
                hidraw = ioctl.hidraw.Hidraw(child.device_node)
            except PermissionError:
                self.__logger.error(f'Could not open device `{child.device_node}`, ignoring...')
                continue

            if self._hidraw_has_vendor_page(hidraw):  # supports vendor protocol
                if hidraw.info == target_info.as_tuple:  # target (parent)
                    parent = HidrawDevice(hidraw=hidraw)
                    self._tree.create_node(
                        tag=hidraw.name,
                        identifier=hidraw.path,
                        parent='devices',
                        data=logitechd.protocol.construct_device(parent),
                    )
                else:  # device
                    children.append(HidrawDevice(hidraw=hidraw))

        # populate tree
        if parent:
            for child in children:
                self._tree.create_node(
                    tag=child.name,
                    identifier=child.path,
                    parent=parent.path,
                    data=logitechd.protocol.construct_device(child),
                )
        else:
            self.__logger.error(
                f'Could not find the hiraw node for the parent device in `{usb_device}` '
                f'(children=`{children}`)'
            )

    def _hidraw_has_vendor_page(self, hidraw: ioctl.hidraw.Hidraw) -> bool:
        '''
        Whether or not the report descriptor of a hidraw node contains a vendor page
        Really basic HID report descriptor parser. You can find the documentation
        in items 5 (Operational Mode) and 6 (Descriptors) of the Device Class
        Definition for HID
        '''

        class Type(object):
            MAIN = 0
            GLOBAL = 1
            LOCAL = 2
            RESERVED = 3

        class TagGlobal(object):
            USAGE_PAGE = 0b0000
            LOGICAL_MINIMUM = 0b0001
            LOGICAL_MAXIMUM = 0b0010
            PHYSICAL_MINIMUM = 0b0011
            PHYSICAL_MAXIMUM = 0b0100
            UNIT_EXPONENT = 0b0101
            UNIT = 0b0110
            REPORT_SIZE = 0b0111
            REPORT_ID = 0b1000
            REPORT_COUNT = 0b1001
            PUSH = 0b1010
            POP = 0b1011

        rdesc = hidraw.report_descriptor
        i = 0
        while i < len(rdesc):
            prefix = rdesc[i]
            tag = (prefix & 0b11110000) >> 4
            typ = (prefix & 0b00001100) >> 2
            size = prefix & 0b00000011

            if size == 3:  # 6.2.2.2
                size = 4

            if typ == Type.GLOBAL and tag == TagGlobal.USAGE_PAGE and rdesc[i+2] == 0xff:  # vendor page
                return True

            i += size + 1

        return False

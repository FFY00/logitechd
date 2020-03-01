#!/usr/bin/env python3
#
# SPDX-License-Identifier: MIT

import pyudev

from typing import Dict, List

import logitechd.device
import logitechd.utils

from logitechd.utils import DeviceInfo


target_devices: List[DeviceInfo] = [
    # Wired
    DeviceInfo(vid=0x46d, pid=0xc33c),  # G513
    DeviceInfo(vid=0x46d, pid=0xc33e),  # G915
    DeviceInfo(vid=0x46d, pid=0xc33f),  # G815
    # Receivers
    DeviceInfo(vid=0x46d, pid=0xc52b),  # Unifying
    DeviceInfo(vid=0x46d, pid=0xc539),  # Lightspeed 1.0
    DeviceInfo(vid=0x46d, pid=0xc53a),  # Powerplay (Lightspeed 1.0)
    DeviceInfo(vid=0x46d, pid=0xc53f),  # Lightspeed 1.1
    DeviceInfo(vid=0x46d, pid=0xc541),  # Lightspeed 1.1 v2
]


def event_handler_parent(action: str, device: pyudev.Device) -> None:
    '''
    udev event handler for parent (USB Reciver, Bluetooth) actions
    '''
    if action == 'add' and device.device_node and 'PRODUCT' in device.properties:
        for target in target_devices:
            if device.properties['PRODUCT'].startswith(f'{target.vid:x}/{target.pid:x}'):
                logitechd.utils.populate_device_tree(device, target, devices)


def event_handler_hidraw(action: str, device: pyudev.Device) -> None:
    '''
    udev event handler for node (hidraw devices created by the hid-logitech-dj kernel driver) actions
    '''
    if action == 'remove' and device.device_node:
        if device.device_node in devices and not devices[device.device_node].children:
            devices[device.device_node].destroy()
            del devices[device.device_node]


if __name__ == '__main__':
    devices: Dict[str, logitechd.device.Device] = {}

    context = pyudev.Context()
    monitor_usb = pyudev.Monitor.from_netlink(context)
    monitor_usb.filter_by('usb')
    monitor_hidraw = pyudev.Monitor.from_netlink(context)
    monitor_hidraw.filter_by('hidraw')

    # Trigger the event handler manually to proccess the already existent devices
    for device in context.list_devices(subsystem='usb'):
        event_handler_parent('add', device)

    pyudev.MonitorObserver(monitor_usb, event_handler_parent).start()
    pyudev.MonitorObserver(monitor_hidraw, event_handler_hidraw).start()
    print('Started listening for udev events...')

    # temporary daemon payload -- print the device tree
    import time
    while(True):
        time.sleep(1.5)
        print()
        for path, device in devices.items():
            if not device._parent:
                try:
                    print(f'{device.path} ({device._hidraw.name})')
                except OSError:
                    print(device.path)
                for chidren in device.children:
                    print(f'\t{chidren.path} ({chidren._hidraw.name})')

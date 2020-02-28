#!/usr/bin/env python3
#
# SPDX-License-Identifier: MIT

import pyudev

from typing import List

import logitechd.utils

from logitechd.device import Device
from logitechd.utils import DeviceInfo

if __name__ == '__main__':
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by('hidraw')

    receivers: List[DeviceInfo] = [
        DeviceInfo(vid=0x46d, pid=0xc33f),
    ]

    devices = {}

    def init_device(device: pyudev.device._device.Device) -> None:
        if logitechd.utils.find_usb_parent(device, receivers):
            hidraw = logitechd.hidraw.Hidraw(device.device_node)
            if hidraw.has_vendor_page:
                devices[device.device_node] = Device(hidraw)

    for device in pyudev.Context().list_devices(subsystem='hidraw'):
        init_device(device)

    def log_event(action: str, device: pyudev.device._device.Device) -> None:
        if device.device_node:

            if device.action == 'add':
                init_device(device)

            elif device.action == 'remove':
                if device.device_node in devices:
                    del devices[device.device_node]

    observer = pyudev.MonitorObserver(monitor, log_event)
    observer.start()
    print('Started listening for udev events...')

    import time
    while(True):
        time.sleep(1)
        print(f'devices = {list(devices.keys())}')
        pass

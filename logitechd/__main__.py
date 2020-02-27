#!/usr/bin/env python3
#
# SPDX-License-Identifier: MIT

import pyudev

import logitechd.utils

from logitechd.device import Device
from logitechd.utils import DeviceInfo

if __name__ == '__main__':
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by('hidraw')

    receivers = [
        DeviceInfo(vid=0x46d, pid=0xc33f)
    ]

    devices = {}

    for device in pyudev.Context().list_devices(subsystem='hidraw'):
        if logitechd.utils.find_usb_parent(device, receivers):
            devices[device.device_node] = Device(device.device_node)

    def log_event(action, device):
        if device.device_node:

            if device.action == 'add':
                parent = logitechd.utils.find_usb_parent(device, receivers)
                if parent:
                    devices[device.device_node] = Device(device.device_node)

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

#!/usr/bin/env python3
#
# SPDX-License-Identifier: MIT

import pyudev

from typing import Dict, List

import logitechd.utils

from logitechd.device import Device
from logitechd.utils import DeviceInfo


def event_handler(action: str, device: pyudev.device._device.Device) -> None:
    if device.device_node:

        if action == 'add':
            if logitechd.utils.find_usb_parent(device, receivers):
                hidraw = logitechd.hidraw.Hidraw(device.device_node)
                if hidraw.has_vendor_page:
                    devices[device.device_node] = Device(hidraw)

        elif action == 'remove':
            if device.device_node in devices:
                del devices[device.device_node]


if __name__ == '__main__':
    receivers: List[DeviceInfo] = [
        DeviceInfo(vid=0x46d, pid=0xc33f),
    ]

    devices: Dict[str, Device] = {}

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by('hidraw')

    # Trigger the event handler manually to proccess the already existent devices
    for device in context.list_devices(subsystem='hidraw'):
        event_handler('add', device)

    observer = pyudev.MonitorObserver(monitor, event_handler)
    observer.start()
    print('Started listening for udev events...')

    import time
    while(True):
        time.sleep(1)
        print(f'devices = {list(devices.keys())}')
        pass

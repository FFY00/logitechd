# SPDX-License-Identifier: MIT

import os
import threading

import ioctl.hidraw
import pytest
import uhid

import logitechd.hid


def find_hidraw(device: uhid.AsyncUHIDDevice) -> ioctl.hidraw.Hidraw:
    visited = set()

    while True:
        for node in os.listdir('/dev'):
            if node in visited:  # pragma: no cover
                continue

            visited.update([node])
            if node.startswith('hidraw'):
                hidraw = ioctl.hidraw.Hidraw(f'/dev/{node}')

                if device.unique_name == hidraw.uniq:
                    return f'/dev/{node}'


@pytest.fixture()
def device(vendor_rdesc):
    device = uhid.UHIDDevice(
        0x4321,
        0x1234,
        'Dummy Mouse',
        vendor_rdesc,
        backend=uhid.PolledBlockingUHID,
    )
    device.wait_for_start()

    stop_dispatch = threading.Event()
    dispatch_thread = threading.Thread(target=device.dispatch, args=(stop_dispatch,))
    dispatch_thread.start()

    try:
        yield device
    finally:
        stop_dispatch.set()
        device.destroy()


@pytest.fixture()
def hidraw(device):
    return logitechd.hid.Hidraw(find_hidraw(device))


@pytest.mark.timeout(1)
def test_read(device, hidraw):
    data = [0x20, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]

    device.send_input(data)

    assert list(hidraw.read()) == data


@pytest.mark.timeout(1)
def test_write(device, hidraw):
    written = []

    device.receive_output = lambda data, rtype: written.append(data)

    data = [0x20, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]

    hidraw.write(data)
    while not written:
        pass

    assert data in written

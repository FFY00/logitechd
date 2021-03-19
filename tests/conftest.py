# SPDX-License-Identifier: MIT

import pytest


@pytest.fixture
def vendor_rdesc():
    return [
        # Vendor page report descriptor
        0x06, 0x00, 0xff,   # Usage Page (Vendor Page)
        0x09, 0x00,         # Usage (Vendor Usage 0)
        0xa1, 0x01,         # Collection (Application)
        0x85, 0x20,         # .Report ID (0x20)
        0x75, 0x08,         # .Report Size (8)
        0x95, 0x08,         # .Report Count (8)
        0x15, 0x00,         # .Logical Minimum (0)
        0x26, 0xff, 0x00,   # .Logical Maximum (255)
        0x09, 0x00,         # .Usage (Vendor Usage 0)
        0x81, 0x00,         # .Input (Data,Arr,Abs)
        0x09, 0x00,         # .Usage (Vendor Usage 0)
        0x91, 0x00,         # .Output (Data,Arr,Abs)
        0xc0,               # End Collection
    ]

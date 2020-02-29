# SPDX-License-Identifier: MIT


class ReportType(object):
    SHORT = 0x10
    LONG = 0x11


REPORT_SIZE = {
    ReportType.SHORT: 7,
    ReportType.LONG: 20,
}

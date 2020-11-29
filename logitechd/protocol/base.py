# SPDX-License-Identifier: MIT

import typing


if typing.TYPE_CHECKING:  # pragma: no cover
    import logitechd.device


class BaseProtocol(object):
    '''
    Base protocol class
    '''
    def __init__(self, device: 'logitechd.device.Device', index: int, sw_id: int = 0):
        self._device = device
        self._index = index
        self.sw_id = sw_id

# SPDX-License-Identifier: MIT

import abc
import os

from typing import Sequence


class HidABC(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def read(self) -> Sequence[int]:
        ...  # pragma: no cover

    @abc.abstractmethod
    def write(self, data: Sequence[int]) -> None:
        ...  # pragma: no cover


class Hidraw(HidABC):
    def __init__(self, path: str) -> None:
        import ioctl.hidraw

        self._hidraw = ioctl.hidraw.Hidraw(path)

    def read(self) -> Sequence[int]:
        return list(os.read(self._hidraw.fd, 64))

    def write(self, data: Sequence[int]) -> None:
        os.write(self._hidraw.fd, bytes(data))

# SPDX-License-Identifier: MIT

import abc

from typing import Sequence


class HidABC(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def read(self) -> Sequence[int]:
        ...  # pragma: no cover

    @abc.abstractmethod
    def write(self, data: Sequence[int]) -> None:
        ...  # pragma: no cover

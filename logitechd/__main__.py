#!/usr/bin/env python
# SPDX-License-Identifier: MIT

import platform

import logitechd.backend


if __name__ == '__main__':
    system = platform.uname().system
    if system == 'Linux':
        backend = logitechd.backend.HidrawBackend()
    else:
        raise NotImplementedError('Unsupported operating system')

    # temporary payload
    import logging
    logging.basicConfig(level=logging.DEBUG)
    import time
    while True:
        backend._tree.show()
        time.sleep(0.5)

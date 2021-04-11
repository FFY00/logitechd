#!/usr/bin/env python
# SPDX-License-Identifier: MIT

import logitechd.backend


if __name__ == '__main__':
    backend = logitechd.backend.construct_backend()

    # temporary payload
    import logging
    logging.basicConfig(level=logging.DEBUG)
    import time
    while True:
        backend._tree.show()
        time.sleep(0.5)

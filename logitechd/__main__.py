#!/usr/bin/env python
# SPDX-License-Identifier: MIT

import logitechd.backend


def main() -> None:
    backend = logitechd.backend.construct_backend()

    # temporary payload
    import logging
    logging.basicConfig(level=logging.DEBUG)
    import time
    while True:
        backend._tree.show()
        time.sleep(0.5)


def entrypoint() -> None:
    try:
        main()
    except KeyboardInterrupt:
        print('Exiting...')


if __name__ == '__main__':
    entrypoint()

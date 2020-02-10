# SPDX-License-Identifier: MIT

from setuptools import setup
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='logitechd',
    version='0.0.1',
    description='Logitech daemon to control HID++ 1.0 and HID++ 2.0 devices',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/FFY00/logitechd',
    author='Filipe Laíns',
    author_email='lains@archlinux.org',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'Topic :: Operating System Kernels :: Linux',
    ],
    keywords='logitech daemon hidpp control configure',
    project_urls={
        'Bug Reports': 'https://github.com/FFY00/logitechd/issues',
        'Source': 'https://github.com/FFY00/logitechd',
    },

    packages=[
        'logitechd',
    ],
    python_requires='>=3.7',
    install_requires=[
        'dbus-python',
        'pyudev',
    ],
    tests_require=[
        'pytest',
        'ratbag-emu',
        'libevdev',
    ],
)

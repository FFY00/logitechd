# SPDX-License-Identifier: MIT

import nox


nox.options.sessions = ['mypy']
nox.options.reuse_existing_virtualenvs = True


@nox.session(python='3.8')
def mypy(session):
    session.install('.', 'mypy')

    session.run('mypy', '-p', 'dbus_objects')

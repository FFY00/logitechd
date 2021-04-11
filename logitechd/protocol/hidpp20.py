# SPDX-License-Identifier: MIT

import textwrap

from typing import Any, Dict, Tuple


class _FeatureMeta(type):
    def __new__(mcs, name: str, bases: Tuple[Any], dic: Dict[str, Any]):  # type: ignore
        if len(bases) != 0:  # not the base class - Feature
            if 'id' not in dic:
                raise ValueError('Missing `id` field')
            for key, obj in dic.items():
                if key == 'id':
                    if not isinstance(obj, int):
                        raise ValueError(f'Expected value of `id` to be an int but got `{obj}`')
                elif not key.startswith('_') and not issubclass(obj, Function) and not issubclass(obj, Event):
                    raise ValueError(f'Expected value of `{key}` to be a Function or Event but got `{obj}`')
        return super().__new__(mcs, name, bases, dic)

    def __repr__(self) -> str:
        return f'{self.__name__}(id={getattr(self, "id")})'


class _FunctionMeta(type):
    def __new__(mcs, name: str, bases: Tuple[Any], dic: Dict[str, Any]):  # type: ignore
        if len(bases) != 0:  # not the base class - Function
            if 'id' not in dic:
                raise ValueError('Missing `id` field')
            if 'request' not in dic and 'response' not in dic:
                raise ValueError('Expecting at least one of `request` and `response` fields to be present but got none')
            for key, obj in dic.items():
                if key == 'id':
                    if not isinstance(obj, int):
                        raise ValueError(f'Expected value of `id` to be an int but got `{obj}`')
                elif key in ('request', 'response'):
                    if not isinstance(obj, dict):
                        raise ValueError(f'Expected value of `{key}` to be a dictionary but got `{obj}`')
                elif not key.startswith('_'):
                    raise ValueError(f'Unexpected field `{key}`')
        return super().__new__(mcs, name, bases, dic)

    def __repr__(self) -> str:
        desc = textwrap.dedent(f'''
            {self.__name__}(
                id={getattr(self, "id")},
        ''')
        for attr in ('request', 'response'):
            if hasattr(self, attr):
                desc += f'    {attr}={tuple(getattr(self, attr).keys())},\n'
        desc += ')'
        return desc


class _EventMeta(type):
    def __new__(mcs, name: str, bases: Tuple[Any], dic: Dict[str, Any]):  # type: ignore
        if len(bases) != 0:  # not the base class - Event
            for field in ('id', 'data'):
                if field not in dic:
                    raise ValueError(f'Missing `{field}` field')
            for key, obj in dic.items():
                if key == 'id':
                    if not isinstance(obj, int):
                        raise ValueError(f'Expected value of `id` to be an int but got `{obj}`')
                elif key == 'data':
                    if not isinstance(obj, dict):
                        raise ValueError(f'Expected value of `data` to be a dictionary but got `{obj}`')
                elif not key.startswith('_'):
                    raise ValueError(f'Unexpected field `{key}`')
        return super().__new__(mcs, name, bases, dic)

    def __repr__(self) -> str:
        return textwrap.dedent(f'''
            {self.__name__}(
                id={getattr(self, "id")},
                data={tuple(getattr(self, "data").keys())},
            )
        ''')


class Feature(metaclass=_FeatureMeta):
    '''
    HID++ 2.0 feature

    Must have an ``id`` field, all other fields should be subclasses of either
    ``Function`` or ``Event``.

    ``id`` should be an integer with the ID of the feature.
    '''


class Function(metaclass=_FunctionMeta):
    '''
    HID++ 2.0 function

    Must have an ``id`` field, and may have ``request`` and/or ``response``
    fields. No other fields are allowed.

    ``id`` should be an integer with the ID of the function.
    ``request`` and ``response`` should be dictionaries describing the packet format.
    '''


class Event(metaclass=_EventMeta):
    '''
    HID++ 2.0 event

    Must have ``id`` and ``data`` fields.

    ``id`` should be an integer with the ID of the event.
    ``data`` should be a dictionary describing the packet format.
    '''

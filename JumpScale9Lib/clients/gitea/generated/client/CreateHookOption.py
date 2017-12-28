"""
Auto-generated class for CreateHookOption
"""
from .CreateHookOptionconfig import CreateHookOptionconfig
from .EnumCreateHookOptionType import EnumCreateHookOptionType
from six import string_types

from . import client_support


class CreateHookOption(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type active: bool
        :type config: CreateHookOptionconfig
        :type events: list[str]
        :type type: EnumCreateHookOptionType
        :rtype: CreateHookOption
        """

        return CreateHookOption(**kwargs)

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'CreateHookOption'
        data = json or kwargs

        # set attributes
        data_types = [bool]
        self.active = client_support.set_property('active', data, data_types, False, [], False, False, class_name)
        data_types = [CreateHookOptionconfig]
        self.config = client_support.set_property('config', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.events = client_support.set_property('events', data, data_types, False, [], True, False, class_name)
        data_types = [EnumCreateHookOptionType]
        self.type = client_support.set_property('type', data, data_types, False, [], False, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)

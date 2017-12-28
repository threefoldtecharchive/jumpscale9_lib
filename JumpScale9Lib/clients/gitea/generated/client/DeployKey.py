"""
Auto-generated class for DeployKey
"""
from datetime import datetime
from six import string_types

from . import client_support


class DeployKey(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type created_at: datetime
        :type id: int
        :type key: str
        :type read_only: bool
        :type title: str
        :type url: str
        :rtype: DeployKey
        """

        return DeployKey(**kwargs)

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'DeployKey'
        data = json or kwargs

        # set attributes
        data_types = [datetime]
        self.created_at = client_support.set_property(
            'created_at', data, data_types, False, [], False, False, class_name)
        data_types = [int]
        self.id = client_support.set_property('id', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.key = client_support.set_property('key', data, data_types, False, [], False, False, class_name)
        data_types = [bool]
        self.read_only = client_support.set_property('read_only', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.title = client_support.set_property('title', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.url = client_support.set_property('url', data, data_types, False, [], False, False, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)

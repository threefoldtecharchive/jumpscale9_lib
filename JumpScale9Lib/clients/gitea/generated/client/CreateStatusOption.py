"""
Auto-generated class for CreateStatusOption
"""
from six import string_types

from . import client_support


class CreateStatusOption(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type context: str
        :type description: str
        :type state: str
        :type target_url: str
        :rtype: CreateStatusOption
        """

        return CreateStatusOption(**kwargs)

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'CreateStatusOption'
        data = json or kwargs

        # set attributes
        data_types = [string_types]
        self.context = client_support.set_property('context', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.description = client_support.set_property(
            'description', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.state = client_support.set_property('state', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.target_url = client_support.set_property(
            'target_url', data, data_types, False, [], False, False, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)

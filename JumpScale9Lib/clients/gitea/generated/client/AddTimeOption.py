"""
Auto-generated class for AddTimeOption
"""

from . import client_support


class AddTimeOption(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type time: int
        :rtype: AddTimeOption
        """

        return AddTimeOption(**kwargs)

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'AddTimeOption'
        data = json or kwargs

        # set attributes
        data_types = [int]
        self.time = client_support.set_property('time', data, data_types, False, [], False, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)

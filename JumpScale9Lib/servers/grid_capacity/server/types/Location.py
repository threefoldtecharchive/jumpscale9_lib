"""
Auto-generated class for Location
"""
from six import string_types

from . import client_support


class Location(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type city: str
        :type continent: str
        :type country: str
        :type latitude: float
        :type longitude: float
        :rtype: Location
        """

        return Location(**kwargs)

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Location'
        data = json or kwargs

        # set attributes
        data_types = [string_types]
        self.city = client_support.set_property('city', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.continent = client_support.set_property('continent', data, data_types, False, [], False, True, class_name)
        data_types = [string_types]
        self.country = client_support.set_property('country', data, data_types, False, [], False, True, class_name)
        data_types = [float]
        self.latitude = client_support.set_property('latitude', data, data_types, False, [], False, True, class_name)
        data_types = [float]
        self.longitude = client_support.set_property('longitude', data, data_types, False, [], False, True, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)

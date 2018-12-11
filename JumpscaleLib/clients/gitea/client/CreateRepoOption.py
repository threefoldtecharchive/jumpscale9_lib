# DO NOT EDIT THIS FILE. This file will be overwritten when re-running go-raml.

"""
Auto-generated class for CreateRepoOption
"""
from six import string_types

from . import client_support


class CreateRepoOption(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type auto_init: bool
        :type description: string_types
        :type gitignores: string_types
        :type license: string_types
        :type name: string_types
        :type private: bool
        :type readme: string_types
        :rtype: CreateRepoOption
        """

        return CreateRepoOption(**kwargs)

    def __init__(self, json=None, **kwargs):
        pass
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'CreateRepoOption'
        data = json or kwargs

        # set attributes
        data_types = [bool]
        self.auto_init = client_support.set_property('auto_init', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.description = client_support.set_property(
            'description', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.gitignores = client_support.set_property(
            'gitignores', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.license = client_support.set_property('license', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.name = client_support.set_property('name', data, data_types, False, [], False, True, class_name)
        data_types = [bool]
        self.private = client_support.set_property('private', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.readme = client_support.set_property('readme', data, data_types, False, [], False, False, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)

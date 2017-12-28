"""
Auto-generated class for Release
"""
from .User import User
from datetime import datetime
from six import string_types

from . import client_support


class Release(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type author: User
        :type body: str
        :type created_at: datetime
        :type draft: bool
        :type id: int
        :type name: str
        :type prerelease: bool
        :type published_at: datetime
        :type tag_name: str
        :type tarball_url: str
        :type target_commitish: str
        :type url: str
        :type zipball_url: str
        :rtype: Release
        """

        return Release(**kwargs)

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Release'
        data = json or kwargs

        # set attributes
        data_types = [User]
        self.author = client_support.set_property('author', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.body = client_support.set_property('body', data, data_types, False, [], False, False, class_name)
        data_types = [datetime]
        self.created_at = client_support.set_property(
            'created_at', data, data_types, False, [], False, False, class_name)
        data_types = [bool]
        self.draft = client_support.set_property('draft', data, data_types, False, [], False, False, class_name)
        data_types = [int]
        self.id = client_support.set_property('id', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.name = client_support.set_property('name', data, data_types, False, [], False, False, class_name)
        data_types = [bool]
        self.prerelease = client_support.set_property(
            'prerelease', data, data_types, False, [], False, False, class_name)
        data_types = [datetime]
        self.published_at = client_support.set_property(
            'published_at', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.tag_name = client_support.set_property('tag_name', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.tarball_url = client_support.set_property(
            'tarball_url', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.target_commitish = client_support.set_property(
            'target_commitish', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.url = client_support.set_property('url', data, data_types, False, [], False, False, class_name)
        data_types = [string_types]
        self.zipball_url = client_support.set_property(
            'zipball_url', data, data_types, False, [], False, False, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)

"""
Auto-generated class for IssueLabelsOption
"""

from . import client_support


class IssueLabelsOption(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type labels: list[int]
        :rtype: IssueLabelsOption
        """

        return IssueLabelsOption(**kwargs)

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'IssueLabelsOption'
        data = json or kwargs

        # set attributes
        data_types = [int]
        self.labels = client_support.set_property('labels', data, data_types, False, [], True, False, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)

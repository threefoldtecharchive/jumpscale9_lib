# DO NOT EDIT THIS FILE. This file will be overwritten when re-running go-raml.

import base64


class BasicAuthClientBasicauth:
    def __init__(self, http_client):
        pass
        self._http_client = http_client

    def set_authorization_header(self, username, password):
        """"Hash username:password and set header Authorization to 'Basic <hash>'"""
        val = base64.b64encode('%s:%s' % (username, password))
        self._http_client.set_header('Authorization', 'Basic %s' % val)

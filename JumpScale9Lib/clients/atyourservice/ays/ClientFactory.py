from .client import Client

DEFAULT_URL = "https://localhost:5000"

class ClientFactory:

    def __init__(self):
        self.__jslocation__ = 'j.clients.ays'

    def get(self, client_id, client_secret, url=DEFAULT_URL, validity=3600):
        """
        Get an AYS client to interact with a local or remote AYS server.

        Args:
            client_id: client ID of the API access key of the ItsYou.online organization protecting the AYS RESTful API; defaults to None
            client_secret: secret of the API access key of the ItsYou.online organization protecting the AYS RESTful API; defaults to None
            url: url of the AYS RESTful API, e.g. `http://172.25.0.238:5000`; defaults to https://localhost:5000
            validity: validity of the JWT that will be created based on the given client ID and secret, defaults to 3600 (seconds)
        """
        return Client(url=url, jwt=None, clientID=client_id, secret=client_secret, validity=validity)

    def get_with_jwt(self, url=DEFAULT_URL, jwt=None):
        """
        Get an AYS client to interact with a local or remote AYS server.

        Args:
            url: url of the AYS RESTful API, e.g. `http://172.25.0.238:5000`; defaults to https://localhost:5000
            jwt: JSON Web Token for the ItsYou.online organization protecting the AYS RESTful API; defaults to None
        """
        return Client(url=url, jwt=jwt, clientID=None, secret=None, validity=None)

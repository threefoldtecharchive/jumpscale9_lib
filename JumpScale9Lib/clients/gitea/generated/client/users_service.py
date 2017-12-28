
from .User import User
from .api_response import APIResponse
from .unhandled_api_error import UnhandledAPIError
from .unmarshall_error import UnmarshallError


class UsersService:
    def __init__(self, client):
        self.client = client

    def userSearch(self, headers=None, query_params=None, content_type="application/json"):
        """
        Search for users
        It is method for GET /users/search
        """
        uri = self.client.base_url + "/users/search"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append((elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def userCheckFollowing(self, follower, followee, headers=None, query_params=None, content_type="application/json"):
        """
        Check if one user is following another user
        It is method for GET /users/{follower}/following/{followee}
        """
        uri = self.client.base_url + "/users/" + follower + "/following/" + followee
        return self.client.get(uri, None, headers, query_params, content_type)

    def userListFollowers(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        List the given user's followers
        It is method for GET /users/{username}/followers
        """
        uri = self.client.base_url + "/users/" + username + "/followers"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append((elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def userListFollowing(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        List the users that the given user is following
        It is method for GET /users/{username}/following
        """
        uri = self.client.base_url + "/users/" + username + "/following"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append((elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def userListGPGKeys(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        List the given user's GPG keys
        It is method for GET /users/{username}/gpg_keys
        """
        uri = self.client.base_url + "/users/" + username + "/gpg_keys"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append((elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def userListKeys(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        List the given user's public keys
        It is method for GET /users/{username}/keys
        """
        uri = self.client.base_url + "/users/" + username + "/keys"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append((elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def userListRepos(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        List the repos owned by the given user
        It is method for GET /users/{username}/repos
        """
        uri = self.client.base_url + "/users/" + username + "/repos"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append((elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def userListStarred(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        The repos that the given user has starred
        It is method for GET /users/{username}/starred
        """
        uri = self.client.base_url + "/users/" + username + "/starred"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append((elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def userListSubscriptions(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        List the repositories watched by a user
        It is method for GET /users/{username}/subscriptions
        """
        uri = self.client.base_url + "/users/" + username + "/subscriptions"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append((elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def userGetTokens(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        List the authenticated user's access tokens
        It is method for GET /users/{username}/tokens
        """
        uri = self.client.base_url + "/users/" + username + "/tokens"
        return self.client.get(uri, None, headers, query_params, content_type)

    def userCreateToken(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Create an access token
        It is method for POST /users/{username}/tokens
        """
        uri = self.client.base_url + "/users/" + username + "/tokens"
        return self.client.post(uri, data, headers, query_params, content_type)

    def userGet(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Get a user
        It is method for GET /users/{username}
        """
        uri = self.client.base_url + "/users/" + username
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=User(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

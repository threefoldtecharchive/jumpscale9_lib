from js9 import j

import zerotier
import requests
import json


class ZerotierClient:

    def __init__(self, token):
        self.client = zerotier.client.Client()
        self.client.set_auth_header("Bearer " + token)

    def getNetworks(self):
        """
        returns [(id,name,onlinecount)]
        """
        res0 = self.client.network.listNetworks().json()
        return [(item["id"], item["name"], item["onlineMemberCount"]) for item in res0]

    def getNetworkMembers(self, networkId, online=True):

        res = self.client.network.listMembers(id=networkId).json()
        result = []
        for item in res:
            res2 = {}
            res2["authorized"] = item["config"]["authorized"]
            # item["creationTime"]
            res2["name"] = item["name"]
            res2["id"] = item["id"]
            if online and item["online"] is False:
                continue
            res2["online"] = item["online"]
            res2["lastOnlineHR"] = j.data.time.epoch2HRDateTime(
                item["lastOnline"] / 1000)
            res2["lastOnline"] = item["lastOnline"]
            res2["ipaddr_priv"] = item["config"]["ipAssignments"]
            res2["ipaddr_pub"] = item["physicalAddress"].split(
                "/")[0] if item["physicalAddress"] else None
            result.append(res2)
        return result

    def getNetworkMemberFromIPPub(self, ip_pub, networkId, online=True):
        res = self.getNetworkMembers(networkId, online)

        res = [item for item in res if item['ipaddr_pub'] == ip_pub]

        if len(res) is 0:
            raise RuntimeError(
                "Did not find network member with ipaddr:%s" % ip_pub)

        return res[0]

        # class ZerotierClient:
        #     def __init__(self, apikey):
        #         self.apikey = apikey
        #         self.apibase = "https://my.zerotier.com/api"
        #
        #     def request(self, path, data=None):
        #         if data == None:
        #             return requests.get(self.apibase + path, headers={'Authorization': 'Bearer ' + self.apikey})
        #
        #         else:
        #             return requests.post(self.apibase + path, headers={'Authorization': 'Bearer ' + self.apikey}, json=data)
        #
        #     def delete(self, path):
        #         return requests.delete(self.apibase + path, headers={'Authorization': 'Bearer ' + self.apikey})
        #
        #     def status(self):
        #         return self.request("/status").json()
        #
        #     def user(self, id):
        #         return self.request("/user/%s" % id).json()
        #
        #     def networks(self):
        #         return self.request("/network").json()
        #
        #     def network_create(self, name):
        #         data = {
        #             "config": {
        #                 "name": name,
        #                 "rules": [{"ruleNo": 1, "action": "accept"}],
        #                 "v4AssignMode": "zt",
        #                 "routes": [{"target": "10.147.17.0/24", "via": None, "flags": 0, "metric": 0}],
        #                 "ipAssignmentPools": [{"ipRangeStart": "10.147.17.1", "ipRangeEnd": "10.147.17.254"}]
        #             }
        #         }
        #
        #         return self.request("/network", data).json()
        #
        #     def network_delete(self, id):
        #         return self.delete("/network/%s" % id)


class ZerotierFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.zerotier"
        self.__imports__ = "zerotier"
        self.logger = j.logger.get('j.clients.zerotier')
        self.connections = {}

    def get(self, token=""):
        """
        """
        if token is "":
            token = j.core.state.config["zerotier"]["apitoken"]
        return ZerotierClient(token)

from .CoreDns import Coredns
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class CorednsFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal_zos.coredns"
        JSBASE.__init__(self)

    def get(self, name, node, etcd_endpoint, etcd_password, zt_identity=None, nics=None, backplane='backplane'):
        """
        Get sal for coredns
        Returns:
            the sal layer 
        """
        return Coredns(name, node, etcd_endpoint, etcd_password, zt_identity, nics, backplane)

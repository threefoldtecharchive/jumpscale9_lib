from .TfChain import TfChain
from jumpscale import j

JSBASE = j.application.jsbase_get_class()


class TfChainFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal_zos.tfchain"
        JSBASE.__init__(self)

    @staticmethod
    def get():
        """
        Get sal for tfchain
        Returns:
            the sal layer 
        """
        return TfChain()
from jumpscale import j

from .CoreDnsClient import CoreDnsClient

JSConfigFactory = j.tools.configmanager.base_class_configs


class CoreDnsFactory(JSConfigFactory):
    def __init__(self):
        self.__jslocation__ = "j.clients.coredns"
        JSConfigFactory.__init__(self, CoreDnsClient)

    def configure(self, instance_name, host, port="2379", user="root", password="root"):
        """
        gets an instance of coredns client with etcd configurations directly
        """
        j.clients.etcd.get(instance_name, data={"host": host, "port": port, "user": user, "password_": password})
        return self.get(instance_name, data={"etcd_instance": instance_name})

    def test(self):
        #create etcd client
        cl = j.clients.coredns.configure(instance_name="main",host="10.144.72.95",password="njufdmrq3k")
        #create zones
        zone1 = cl.zone_create('test.example.com','10.144.13.199',record_type='A')
        zone2 = cl.zone_create('example.com','2003::8:1',record_type='AAAA')
        #add records in etcd
        cl.deploy() 
        #get records from etcd
        cl.zones
        #remove records from etcd
        cl.remove([zone1,zone2])

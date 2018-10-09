import json
from enum import Enum

import requests

from JumpscaleLib.sal_zos.disks.Disks import StorageType

from .units import GB, GiB

class CapacityParser:
    def get_report(self, cpu_info, mem_info, disk_info, indent=None):
        """
        Takes in hardware info and parses it into a report

        @param total_mem: total memory of the system in bytes
        @param hw_info: hardware information
        @param disk_info: disk information

        @return Report of the capacity
        """
        return Report(cpu_info, mem_info, disk_info, indent=indent)


class Report():
    """
    Report takes in hardware information and parses it into a report.
    """

    def __init__(self, cpu_info, mem_info, disk_info, indent=None):
        """
        @param total_mem: total system memory in bytes
        @param hw_info: hardware information
        @param disk_info: disk information
        """
        self._total_mem = mem_info['total']
        self._total_cpus = len(cpu_info)
        self._disks = disk_info

        # json indent for pretty printing
        self.indent = indent

    @property
    def CRU(self):
        """
        return the number of core units
        """
        return self._total_cpus

    @property
    def location(self):
        resp = requests.get('https://geoip-db.com/json')
        location = None
        if resp.status_code == 200:
            data = resp.json()
            location = dict(
                continent=data.get('continent', {}).get('names', {}).get('en', 'Unknown'),
                country=data.get('country_name', 'Unknown'),
                city=data.get('city', 'Unknown'),
                longitude=data.get('longitude', 0),
                latitude=data.get('latitude', 0)
            )
        return location

    @property
    def MRU(self):
        """
        return the number of memory units in GiB
        """
        size = (self._total_mem / GiB)
        return round(size, 2)

    @property
    def HRU(self):
        """
        return the number of hd units in GiB
        size field of disks is expected to be in bytes
        """
        unit = 0
        for disk in self._disks:
            if disk.type in [StorageType.HDD, StorageType.ARCHIVE]:
                unit += int(disk.size) / GiB

        return round(unit, 2)

    @property
    def SRU(self):
        """
        return the number of ssd units in GiB
        size field of disks is expected to be in bytes
        """
        unit = 0
        for disk in self._disks:
            if disk.type in [StorageType.SSD, StorageType.NVME]:
                unit += int(disk.size) / GiB

        return round(unit, 2)

    def __repr__(self):
        return json.dumps({
            "processors": self._total_cpus,
            "memory": self._total_mem,
            "disks": self._disks,
        }, indent=self.indent)

    def __str__(self):
        return repr(self)

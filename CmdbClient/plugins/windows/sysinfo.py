#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "xh"
# Date: 2019/11/13
import platform
import wmi
import os
import win32com
from win32com.client import Dispatch, constants


def collect_data():
    data = {
        "os_type": platform.system(),
        "os_release": "%s %s %s" % (platform.release(), platform.architecture(), platform.version()),
        'os_distribution': 'Microsoft',
        "asset_type": "server",
    }
    win32obj = Win32Infro()
    data.update(win32obj.get_cpu_info())
    data.update(win32obj.get_ram_info())
    data.update(win32obj.get_server_info())
    data.update(win32obj.get_disk_info())
    data.update(win32obj.get_nic_info())
    return data


class Win32Infro(object):
    """window通过pywin32采集服务器硬件信息"""

    def __init__(self):
        self.wmi_obj = wmi.WMI()
        self.wmi_service_obj = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        self.wmi_service_connector = self.wmi_service_obj.ConnectServer(".", "root\cimv2")

    def get_cpu_info(self):
        """采集cpu信息"""
        data = {}
        cpu_list = self.wmi_obj.Win32_Processor()
        # print(cpu_list)
        cpu_core_count = 0
        for cpu in cpu_list:
            # print(cpu.name)
            cpu_core_count += cpu.NumberOfCores
            cpu_model = cpu.name
        data["cpu_count"] = len(cpu_list)
        data["cpu_core_count"] = cpu_core_count
        data["cpu_model"] = cpu_model
        return data

    def get_ram_info(self):
        data = []
        ram_collection = self.wmi_service_connector.ExecQuery("Select * from Win32_PhysicalMemory")
        # print(ram_collection)
        for item in ram_collection:
            # print(item.SerialNumber)
            mb = int(1024 * 1024 * 1024)
            ram_size = int(item.Capacity) / mb
            item_data = {
                "slot": item.DeviceLocator.strip(),
                "capacity": ram_size,
                "model": item.Caption,
                "manufactory": item.Manufacturer,
                "sn": item.SerialNumber,
            }
            data.append(item_data)
        # [print(i) for i in data]
        return {"ram": data}

    def get_server_info(self):
        """获取主机信息"""
        computer_info = self.wmi_obj.Win32_ComputerSystem()[0]
        system_info = self.wmi_obj.Win32_OperatingSystem()[0]
        data = {}
        data["manufactory"] = computer_info.Manufacturer
        data["model"] = computer_info.Model
        data["wake_up_type"] = computer_info.WakeUpType
        data["sn"] = system_info.SerialNumber
        # print(data)
        return data

    def get_disk_info(self):
        """获取磁盘信息"""
        data = []
        disk_info = self.wmi_obj.Win32_DiskDrive()
        for disk in disk_info:
            # print(disk.Model,disk.Size,disk.DeviceID,disk.Name,disk.Index,disk.SerialNumber,disk.SystemName,disk.Description)
            item_data = {}
            iface_choices = ["SAS", "SCST", "SATA"]
            for iface_type in iface_choices:
                if iface_type in disk.Model:
                    item_data["iface"] = iface_type
                else:
                    item_data["iface_type"] = "unkown"
                item_data["slot"] = disk.Index
                item_data["sn"] = disk.SerialNumber
                item_data["model"] = disk.Model
                item_data["manufactory"] = disk.Manufacturer
                item_data["capacity"] = int(disk.Size) / (1024 * 1024 * 1024)
                data.append(item_data)
            # [print(i) for i in data]
            return {"physical_disk": data}

    def get_nic_info(self):
        """获取网卡数据信息"""
        data = []
        nic_info = self.wmi_obj.Win32_NetworkAdapterConfiguration()
        for nic in nic_info:
            if nic.MACAddress is not None:
                item_data = {}
                item_data["macaddress"] = nic.MACAddress
                item_data["model"] = nic.Caption
                item_data["name"] = nic.Index
                if nic.IPAddress is not None:
                    item_data["ipaddress"] = nic.IPAddress[0]
                    item_data["netmask"] = nic.IPSubnet
                else:
                    item_data["ipaddress"] = ""
                    item_data["netmask"] = ""
                bonding = 0
                data.append(item_data)
        # [print(i) for i in data]
        return {"nic": data}

if __name__ == "__main__":
    collect_data()
    # print(collect_data())
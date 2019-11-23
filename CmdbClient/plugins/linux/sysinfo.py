#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "xh"
# Date: 2019/11/14
import subprocess
import os
import re


def collect_data():
    """采集linux服务器信息"""
    filter_keys = ['Manufacturer', 'Serial Number', 'Product Name', 'UUID', 'Wake-up Type']
    raw_data = {}
    for key in filter_keys:
        try:
            # linux下通过dmidecode命令取基本的硬件信息,数据是这种Product Name: Baidu Cloud BCC格式
            cmd_res = (subprocess.check_output("dmidecode -t system|grep '%s'" % key, shell=True))
            cmd_res = cmd_res.strip()
            res_list = cmd_res.split(":")
            if len(res_list) > 1:
                raw_data[key] = res_list[1].strip()
            else:
                raw_data[key] = -1
        except Exception as e:
            print(e)
            raw_data[key] = -2
    data = {
        "asset_type": "server",
        "manufactory": raw_data["Manufacturer"],
        "sn": raw_data["Serial Number"],
        "model": raw_data["Product Name"],
        "uuid": raw_data["UUID"],
        "Wake-up Type": raw_data["Wake-up Type"]
    }
    data.update(osinfo())
    data.update(get_disk_info())
    data.update(nicinfo())
    data.update(raminfo())
    return data


def get_disk_info():
    obj = DiskInfo()
    return obj.linux()


def nicinfo():
    raw_data = (subprocess.check_output("ifconfig -a", shell=True)).split("\n")
    nic_dict = {}
    next_ip_line = False
    last_mac_addr = None
    for line in raw_data:
        if next_ip_line:
            next_ip_line = False
            nic_name = last_mac_addr.split()[0]
            mac_addr = last_mac_addr.split("HWaddr")[1]
            row_ip_addr = last_mac_addr.split("inet addr:")
            row_bcast = last_mac_addr.split("Bcast:")
            row_netmask = last_mac_addr.split("Mask:")
            if len(row_ip_addr) > 1:
                ip_addr = row_ip_addr[1].split()[0]
                bcast = row_bcast[1].split()[0]
                netmask = row_netmask[1].split()[0]
            else:
                ip_addr = None
                bcast = None
                netmask = None
            if mac_addr not in nic_dict:
                nic_dict[mac_addr] = {
                    "nic_name": nic_name,
                    "mac_addr": mac_addr,
                    "ip_addr": ip_addr,
                    "bcast": bcast,
                    "netmask": netmask,
                    "bonding": 0,
                    "model": "unkown"
                }
            else:
                # MAC已经存在，就需要绑定地址
                if "%s_bonding_addr" % (mac_addr) not in nic_dict:
                    random_mac_addr = "%s_bonding_addr" % mac_addr
                else:
                    random_mac_addr = "%s_bonding_addr2" % mac_addr
                nic_dict[random_mac_addr] = {
                    "nic_name": nic_name,
                    "mac_addr": random_mac_addr,
                    "ip_addr": ip_addr,
                    "bcast": bcast,
                    "netmask": netmask,
                    "bonding": 1,
                    "model": "unkown"
                }
        if "HWaddr" in line:
            next_ip_line = True
            last_mac_addr = line
    nic_list = []
    for k, v in nic_dict.items():
        nic_list.append(v)
    return {"nic": nic_list}


def raminfo():
    '''获取内存信息'''
    raw_data = subprocess.check_output("sudo dmidecode -t 17", shell=True)
    raw_list = raw_data.split("\n")
    raw_ram_list = []
    item_list = []
    for line in raw_list:
        if line.startswith("Memory Device"):
            raw_ram_list.append(item_list)
            item_list = []
        else:
            item_list.append(line.strip())
    ram_list = []
    for item in raw_ram_list:
        item_ram_size = 0
        ram_item_to_dict = {}
        for i in item:
            data = i.split(":")
            if len(data) == 2:
                key, v = data
                if key == "Size":
                    if v.strip != "No Module Installed":
                        ram_item_to_dict["capacity"] = v.split()[0].strip  # 例如 1024 MB
                        item_ram_size = v.split()[0]
                    else:
                        ram_item_to_dict["capacity"] = 0
                if key == "Type":
                    ram_item_to_dict["model"] = v.strip()
                if key == "Manufacturer":
                    ram_item_to_dict["manufactory"] = v.strip()
                if key == "Serial Number":
                    ram_item_to_dict["sn"] = v.strip()
                if key == "Asset Tag":
                    ram_item_to_dict["asset_tag"] = v.strip()
                if key == "Locator":
                    ram_item_to_dict["solt"] = v.strip()
        if item_ram_size == 0:
            pass
        else:
            ram_list.append(ram_item_to_dict)
    row_total_size = subprocess.check_output("cat /proc/meminfo|grep MemTotal", shell=True).split(":")  # 获取总内存大小
    ram_data = {"ram": ram_list}
    if len(row_total_size) == 2:
        total_size_mb = int(row_total_size.strip()[0]) / 1024
        ram_data["ram_size"] = total_size_mb
    return ram_data


def osinfo():
    distributor = subprocess.check_output("lsb_release -a|grep 'Distributor ID'", shell=True).split(":")
    release = subprocess.check_output("lsb_release -a|grep Description", shell=True).split(":")
    data_dict = {
        "os_release": release[1].strip() if len(release) > 1 else None,
        "os_distributor": distributor[1].strip if len(distributor) > 1 else None,
    }
    return data_dict


class DiskInfo(object):
    '''采集磁盘信息'''

    def linux(self):
        res = {"physical_disk_driver": []}
        try:
            plugin_path = os.path.defpath(__file__)
            cmd = "sudo %s/MegaCli -PDList -aALL" % plugin_path
            cmd_res = subprocess.check_output(cmd, shell=True)
            res["physical_disk_driver"] = self.parse(cmd_res[1])
        except Exception as e:
            print(e)
        return res

    def parse(self, content):
        respone = []
        result = []
        for row_line in content.split("\n\n\n\n"):
            result.append(row_line)
        for item in result:
            temp_dict = {}
            for row in item.split("\n"):
                if not row.strip():
                    continue
                if len(row.split(":")) != 2: continue
                key, value = row.split(":")
                name = self.mega_patter_match(key)
                if name:
                    if key == "Raw Size":
                        raw_size = re.search('(\d+\.\d+)', value.strip())
                        if raw_size:
                            temp_dict[name] = raw_size.group()
                        else:
                            raw_size = "0"
                    else:
                        temp_dict[name] = value.strip()
            if temp_dict:
                respone.append(temp_dict)
            return respone

    def mega_patter_match(self, needle):
        grep_pattern = {'Slot': 'slot', 'Raw Size': 'capacity', 'Inquiry': 'model', 'PD Type': 'iface_type'}
        for key, value in grep_pattern.items():
            if needle.startswith(key):
                return value

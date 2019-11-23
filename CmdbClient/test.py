#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "xh"
# Date: 2019/11/15

ip_a = '''
eth0      Link encap:Ethernet  HWaddr 00:0C:29:20:5D:1A  
          inet addr:10.0.0.200  Bcast:10.0.0.255  Mask:255.255.255.0
          inet6 addr: fe80::20c:29ff:fe20:5d1a/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:1678 errors:0 dropped:0 overruns:0 frame:0
          TX packets:918 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:150792 (147.2 KiB)  TX bytes:72371 (70.6 KiB)

eth1      Link encap:Ethernet  HWaddr 00:0C:29:20:5D:24  
          inet addr:172.16.1.200  Bcast:172.16.1.255  Mask:255.255.255.0
          inet6 addr: fe80::20c:29ff:fe20:5d24/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:24 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:0 (0.0 b)  TX bytes:1656 (1.6 KiB)

lo        Link encap:Local Loopback  
          inet addr:127.0.0.1  Mask:255.0.0.0
          inet6 addr: ::1/128 Scope:Host
          UP LOOPBACK RUNNING  MTU:65536  Metric:1
          RX packets:245 errors:0 dropped:0 overruns:0 frame:0
          TX packets:245 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0 
          RX bytes:22839 (22.3 KiB)  TX bytes:22839 (22.3 KiB)
'''

def nicinfo():
    raw_data = ip_a.strip().split("\n")
    # print("raw_data", raw_data)
    nic_dict = {}
    next_ip_line = False
    last_mac_addr = None
    for line in raw_data:
        if next_ip_line:
            next_ip_line = False
            nic_name = last_mac_addr.split()[0]
            mac_addr = last_mac_addr.split("HWaddr")[1].strip()
            row_ip_addr = line.split("inet addr:")
            # print("row_ip", row_ip_addr)
            row_bcast = line.split("Bcast:")
            row_netmask = line.split("Mask:")
            # print(len(row_ip_addr))
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
                # print("nic_dict", nic_dict)
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
         print(k, v)
         nic_list.append(v)
    return {"nic": nic_list}
print("nicinfo", nicinfo())

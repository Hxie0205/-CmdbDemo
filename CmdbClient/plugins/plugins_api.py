#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "xh"
# Date: 2019/11/13

from .windows import sysinfo as win_sysinfo
from .linux import sysinfo as linux_sysinfo

def WindowsSysinfo():

    return win_sysinfo.collect_data()

def LinuxSysinfo():
    return linux_sysinfo.collect_data()
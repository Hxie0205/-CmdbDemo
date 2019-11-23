#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "xh"
# Date: 2019/11/13
import platform
import sys
from plugins import plugins_api


class InfoCollection(object):
    '''采集硬件信息'''

    def os_platform(self):
        os_type = platform.system()
        return os_type

    def collect(self):
        os_platform = self.os_platform()
        try:
            func = getattr(self, os_platform)
            info_data = func()
            return info_data
        except AttributeError as e:
            sys.exit("error: CmdbClient not support os [%s]!" % os_platform)

    def Windows(self):

        return plugins_api.WindowsSysinfo()

    def Linux(self):
        return plugins_api.LinuxSysinfo

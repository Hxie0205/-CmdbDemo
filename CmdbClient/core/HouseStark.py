#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "xh"
# Date: 2019/11/13
from core import info_collection
from conf import settings
import urllib.request
import urllib.parse, urllib.error
import os, sys
import json
import datetime


class ArgvHandler(object):
    def __init__(self, argv_list):
        self.argvs = argv_list
        self.pase_argvs()

    def pase_argvs(self):
        if len(self.argvs) > 1:
            if hasattr(self, self.argvs[1]):
                func = getattr(self, self.argvs[1])
                func()
            else:
                self.help_msg()
        else:
            self.help_msg()

    def help_msg(self):
        msg = '''
        collect_data    收集资产数据
        run_forever ...
        get_asset_id    获取资产id
        report_asset    汇报资产数据到服务器
        '''
        print(msg)

    def collect_data(self):
        obj = info_collection.InfoCollection()
        asset_data = obj.collect()
        print("asset", asset_data)
        return asset_data

    def get_asset_id(self):
        pass

    def load_asset_id(self, sn=None):
        asset_id_file = settings.Params["asset_id"]
        has_asset_id = False
        if os.path.isfile(asset_id_file):
            asset_id = open(asset_id_file).read().strip()
            if asset_id.isdigit():
                return asset_id
            else:
                has_asset_id = False
        else:
            has_asset_id = False

    def __updata_asset_id(self, new_asset_id):
        '''将服务端返回的资产id更新到本地'''
        asset_id_file = settings.Params["asset_id"]
        with open(asset_id_file, "w", encoding="utf-8") as f:
            f.write(str(new_asset_id))

    def log_record(self, log, action_type=None):
        '''记录日志'''
        f = open(settings.Params["log_file"], "ab")
        if type(log) is str:
            pass
        if type(log) is dict:
            if "info" in log:
                for msg in log["info"]:
                    log_format = "%s\tINFO\t%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"), msg)
                    f.write(log_format)
            if "error" in log:
                for msg in log:
                    log_format = "%s\tERROR\t%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"), msg)
                    f.write(log_format)
            if "warning" in log:
                for msg in log:
                    log_format = "%s\tWARNING\t%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"), msg)
                    f.write(log_format)
        f.close()

    def report_asset(self):
        obj = info_collection.InfoCollection()
        asset_data = obj.collect()
        asset_id = self.load_asset_id(asset_data["sn"])
        if asset_id:  # 资产之前汇报过，只需把存在客户端的asset_id放进asset_data中，直接汇报到正式资产库中
            asset_data["asset_id"] = asset_id
            post_url = "asset_report"
        else:  # 否则资产为第一次汇报，需要先汇报到待批准区
            asset_data["asset_id"] = None
            post_url = "asset_report_with_no_id"
        data = {"asset_data": json.dumps(asset_data)}
        respones = self.__submit_data(post_url, data, method="post")
        print("返回的respones", respones)
        if "asset_id" in str(respones):
            self.__updata_asset_id(respones["asset_id"])

    def __submit_data(self, action_type, data, method):
        '''
        发达数据到目标主机
        :param action_type: url
        :param data: 数据
        :param method: 请求方式
        :return:
        '''
        if action_type in settings.Params["urls"]:
            if type(settings.Params["port"]) is int:
                url = "http://%s:%s%s" % (
                    settings.Params["server"], settings.Params["port"], settings.Params["urls"][action_type])
            else:
                url = "http://%s%s" % (settings.Params["server"], settings.Params["urls"][action_type])
            if method == "get":
                args = ""
                for k, v in data.item:
                    args += "&%s=%s" % (k, v)
                args = args[1:]
                url_with_args = "%s?%s" % (url, args)
                try:
                    req = urllib.request.urlopen(url_with_args, timeout=settings.Params["request_timeout"])
                    callback = req.read()
                    return callback
                except urllib.error as e:
                    sys.exit("\033[31;1m%s\033[0m" % e)
            elif method == "post":
                try:
                    data_encode = urllib.parse.urlencode(data).encode()
                    req = urllib.request.urlopen(url=url, data=data_encode, timeout=settings.Params['request_timeout'])
                    callback = req.read()
                    print("\033[31;1m[%s]:[%s]\033[0m response:\n%s" % (method, url, callback))
                    return callback
                except Exception as e:
                    sys.exit("\033[31;1m%s\033[0m" % e)
        else:
            raise KeyError

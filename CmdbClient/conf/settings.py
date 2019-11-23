#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "xh"
# Date: 2019/11/18

import os

BaseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Params = {
    "server": "127.0.0.1",
    "port": 8000,
    "request_timeout": 30,
    "urls": {
        "asset_report_with_no_id": "/asset/report/asset_with_no_asset_id/",  # 新资产待批准区
        "asset_report": "/asset/report/",  # 正式资产表接口
    },
    "asset_id": '%s/var/.asset_id' % BaseDir,
    "log_file": '%s/logs/run_log' % BaseDir,
    "auth": {
        "user": "xiehong",
        "token": "xh123321",
    },
}
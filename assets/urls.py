#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "xh"
# Date: 2019/11/19

from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"report/asset_with_no_asset_id/$", views.asset_with_no_asset_id, name="acquire_asset_id"),
    url(r'new_assets/approval/$', views.new_assets_approval, name="new_assets_approval"),


]
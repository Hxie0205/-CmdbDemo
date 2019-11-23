#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "xh"
# Date: 2019/11/13
import os
import sys
import platform

if platform.system() == "Windows":
    Base_dir = "\\".join(os.path.abspath(os.path.dirname(__file__)).split("\\")[:-1])
    print(Base_dir)
else:
    Base_dir = "/".join(os.path.abspath(os.path.dirname(__file__)).split("/")[:-1])
sys.path.append(Base_dir)
print("环境变量", sys.path)

from core import HouseStark
if __name__ == "__main__":
    HouseStark.ArgvHandler(sys.argv)
#!/usr/bin/env python
# coding:utf-8
# This script is aimed to grep logs by application
# (User should input a packageName and then we look up for the process ids then separate logs by process ids).

import sys

import adb
from adb import print_package_log

if len(sys.argv) < 2:
    exit("Please input package name as first argument")

packageName = str(sys.argv[1])

devices = adb.get_device_id_list()
devicesNum = len(devices)

if devicesNum < 1:
    print("Device not found.")
elif devicesNum == 1:
    device = devices[0]
    print_package_log(device, packageName)
else:
    print("Please chose a device, input the index of the device:")
    for i in range(0, devicesNum):
        print(str(i) + "\t" + devices[i])
    index = input("")
    print_package_log(devices[int(index)], packageName)

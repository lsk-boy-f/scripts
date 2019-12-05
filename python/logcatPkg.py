#!/usr/bin/env python
# coding:utf-8
# This script is aimed to grep logs by application
# (User should input a packageName and then we look up for the process ids then separate logs by process ids).

import os
import sys

if len(sys.argv) < 2:
    exit("Please input package name as first argument")

packageName = str(sys.argv[1])


def get_device_id():
    device_list = []
    command = "adb devices -l | sed '1d'| awk '{print $1}'"
    result = os.popen(command)
    device_id = result.readline().strip()
    if device_id != "":
        device_list.append(device_id)

    while device_id != "":
        device_id = result.readline().strip()
        if device_id != "":
            device_list.append(device_id)
    return device_list


def print_package_log(device_to_print, package_name):
    # print device, packageName
    print("Got device: " + device_to_print)
    command = "adb -s %s shell ps | grep %s | awk '{print $2}'" % (device_to_print, package_name)
    # print command
    p = os.popen(command)
    # for some applications,there are multiple processes,so we should get all the process id
    pid = p.readline().strip()
    filters = pid
    while pid != "":
        pid = p.readline().strip()
        if pid != '':
            filters = filters + "|" + pid
            # print 'command = %s;filters=%s'%(command, filters)
    if filters != '':
        cmd = 'adb -s %s logcat -v time | grep --color=always -E "%s" ' % (device_to_print, filters)
        os.system(cmd)


devices = get_device_id()
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

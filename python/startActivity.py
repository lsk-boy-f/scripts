#!/usr/bin/env python
# coding:utf-8
import os
import sys
import adb

if len(sys.argv) < 3:
    exit("Please input package name and activity name")

packageName = str(sys.argv[1])
activityName = str(sys.argv[2])


def start_activity(device_id, package_name, activity_name):
    # print device, packageName
    print("Got device: " + device_id)
    command = "adb -s %s shell am start %s/%s" % (device_id, package_name, activity_name)
    os.system(command)


devices = adb.get_device_id_list()
devicesNum = len(devices)

if devicesNum < 1:
    print("Device not found.")
elif devicesNum == 1:
    device = devices[0]
    start_activity(device, packageName, activityName)
else:
    print("Please chose a device, input the index of the device:")
    for i in range(0, devicesNum):
        print(str(i) + "\t" + devices[i])
    index = input("")
    start_activity(devices[int(index)], packageName, activityName)

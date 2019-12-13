#!/usr/bin/env python
# coding:utf-8
import os
import sys

if len(sys.argv) < 3:
    exit("Please input package name and activity name")

packageName = str(sys.argv[1])
activityName = str(sys.argv[2])


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


def start_activity(device, package_name, activity_name):
    # print device, packageName
    print("Got device: " + device)
    command = "adb -s %s shell am start %s/%s" % (device, package_name, activity_name)
    os.system(command)


devices = get_device_id()
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

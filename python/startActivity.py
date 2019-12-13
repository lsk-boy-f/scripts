#!/usr/bin/env python
#coding:utf-8
import os
import sys

packageName=str(sys.argv[1])
activityName=str(sys.argv[2])

def getDeviceId():
    devices = []
    command = "adb devices -l | sed '1d'| awk '{print $1}'"
    result = os.popen(command)
    deviceId = result.readline().strip()
    if deviceId != "":
        devices.append(deviceId)

    while (deviceId != ""):
        deviceId = result.readline().strip()
        if deviceId != "":
            devices.append(deviceId)
    return devices;

def startActivity(device, packageName, activityName):
    # print device, packageName
    print "Got device: " + device
    command = "adb -s %s shell am start %s/%s"%(device, packageName, activityName)
    os.system(command)

devices = getDeviceId();
devicesNum = len(devices);

if devicesNum < 1:
    print "Device not found."
elif devicesNum == 1:
    device = devices[0]
    startActivity(device, packageName, activityName)
else:
    print "Please chose a dvice, input the index of the device:"
    for i in xrange(0, devicesNum):
        print str(i) + "\t" + devices[i]
    index = raw_input("")
    startActivity(devices[int(index)], packageName, activityName)
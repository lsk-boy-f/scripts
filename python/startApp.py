#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from lib import command_with_multi_device
from lib import adb_utils
from adb import start_activity


def start_app(device):
    print("Device:", device)
    print("Package:", package_name)
    if activity_name:
        print("Target activity:", activity_name)

    if activity_name:
        start_activity(device, package_name, activity_name)
    else:
        adb_utils.start_app(device, package_name)


def main(package, activity=None):
    global package_name, activity_name
    package_name = package
    activity_name = activity
    command_with_multi_device.execute(start_app)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Start Android app on device")
    parser.add_argument("-p", "--package", required=True,
                        help="Target package name")
    parser.add_argument("-n", "--activity", help="Target Activity")
    args = parser.parse_args()
    main(args.package, args.activity)

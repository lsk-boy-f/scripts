#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

from lib import command_with_multi_device


def kill_app(device):
    print("Current package: ", package_name)
    # 杀死应用
    kill_app_by_pkg(device, package_name)


def kill_app_by_pkg(device, package_name):
    # 杀死应用
    print(f"Killed app on device: {device}")
    os.system(f"adb -s {device} shell am force-stop {package_name}")


def main():
    command_with_multi_device.execute(kill_app)


if __name__ == "__main__":
    if sys.argv and len(sys.argv) > 1:
        package_name = str(sys.argv[1])
        main()
    else:
        print("Please input package name.")
        sys.exit(1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import time
from lib import command_with_multi_device
from lib import adb_utils
import killApp


def restart_app(device):
    print("Device:", device)
    print("Current package:", package_name)

    killApp.kill_app_by_pkg(device, package_name)
    time.sleep(1)
    adb_utils.start_app(device, package_name)


def main(package):
    global package_name
    package_name = package
    command_with_multi_device.execute(restart_app)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Restart Android app on device")
    parser.add_argument("-p", "--package", required=True,
                        help="Target package name")
    args = parser.parse_args()
    main(args.package)

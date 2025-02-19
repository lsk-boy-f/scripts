#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from lib import command_with_multi_device
from lib import adb_utils
import killApp


def restart_app(device):
    print("Device:", device)
    package_name = adb_utils.get_current_package_name(device)
    print("Current package:", package_name)

    killApp.kill_app_by_pkg(device, package_name)
    time.sleep(1)
    adb_utils.start_app(device, package_name)


def main():
    command_with_multi_device.execute(restart_app)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from lib import command_with_multi_device
from lib import adb_utils
import killApp

def kill_app(device):
    package_name = adb_utils.get_current_package_name(device)
    print("Current package: ", package_name)
    # 杀死应用
    killApp.kill_app_by_pkg(device, package_name)

def main():
    command_with_multi_device.execute(kill_app)

if __name__ == "__main__":
    main()

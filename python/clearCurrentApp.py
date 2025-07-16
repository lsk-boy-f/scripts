#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from lib import command_with_multi_device
from lib import adb_utils

def clear_app(device):
    package_name = adb_utils.get_current_package_name(device=device)
    print("Current package: ", package_name)

    print(f"Clear app on device: {device}")
    os.system(f"adb -s {device} shell pm clear {package_name}")

def main():
    command_with_multi_device.execute(clear_app)

if __name__ == "__main__":
    main()

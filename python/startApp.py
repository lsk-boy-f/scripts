#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import sys
from lib import command_with_multi_device
from lib import adb_utils

def start_app(device):
    print("Device:", device)
    print("Package:", package_name)

    adb_utils.start_app(device, package_name)

def main():
    command_with_multi_device.execute(start_app)

if __name__ == "__main__":
    package_name = str(sys.argv[1])
    main()

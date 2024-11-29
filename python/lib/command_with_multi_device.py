#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os


from . import adb_utils

def execute(func):
    devices = adb_utils.get_connected_devices()
    
    if not devices:
        print("No devices connected.")
        return

    if len(devices) == 1:
        # 如果只有一个设备连接，直接杀死该设备的应用
        func(devices[0])
    else:
        # 如果有多个设备连接，让用户选择设备
        print("Connected devices:")
        for i, device in enumerate(devices, 1):
            print(f"{i}. {device}")
        
        user_choice = input("Choose a device to execute: ")
        
        if 1 <= int(user_choice) <= len(devices):
            selected_device = devices[int(user_choice) - 1]
            func(selected_device)
        else:
            print("Invalid choice.")

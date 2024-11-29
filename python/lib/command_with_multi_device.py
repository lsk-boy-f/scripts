#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os


from . import adb_utils


def execute(func):
    try:
        devices = adb_utils.get_connected_devices()

        if not devices:
            print("No devices connected.")
            sys.exit(1)

        if len(devices) == 1:
            func(devices[0])
        else:
            print("Connected devices:")
            for i, device in enumerate(devices, 1):
                print(f"{i}. {device}")

            while True:
                try:
                    user_choice = int(
                        input("Choose a device (1-{}): ".format(len(devices))))
                    if 1 <= user_choice <= len(devices):
                        selected_device = devices[user_choice - 1]
                        func(selected_device)
                        break
                    else:
                        print(
                            f"Please enter a number between 1 and {len(devices)}")
                except ValueError:
                    print("Please enter a valid number")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        sys.exit(1)

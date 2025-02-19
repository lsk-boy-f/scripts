#!/usr/bin/env python
# coding:utf-8
from adb import start_activity

import os
import argparse

from device import get_connected_devices, select_device


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="监控特定包名的日志")
    parser.add_argument("-d", "--device", help="设备序列号 (使用 adb devices 获取)")
    parser.add_argument("-p", "--package", help="目标应用包名")
    parser.add_argument("-n", "--activity", help="目标Activity")
    args = parser.parse_args()

    devices = get_connected_devices()
    device = args.device
    if not devices:
        print("未检测到连接的设备，请检查 adb 连接。")
        exit(1)

    # 如果没有指定设备，交互选择
    if not device:
        if len(devices) > 1:
            device = select_device(devices)
        else:
            device = devices[0]
    else:
        if args.device in devices:
            device = args.device
        else:
            print(f"设备 {args.device} 未连接，请检查 adb 连接。")
            exit(1)

    if not args.activity:
        print(f"请指定Activity")
        exit(1)

    start_activity(device, args.package, args.activity)

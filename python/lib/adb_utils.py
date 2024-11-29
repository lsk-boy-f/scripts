#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess


def get_connected_devices():
    # 获取已连接设备列表
    result = os.popen("adb devices -l").read()
    lines = result.strip().split('\n')

    devices = []
    for line in lines[1:]:
        device_info = line.split()
        if len(device_info) >= 2 and device_info[1] == 'device':
            devices.append(device_info[0])

    return devices


def get_current_package_name(device):
    # print("Device: ", device)
    # 获取当前在最前台的应用包名
    current_app = os.popen(
        f"adb -s {device} shell dumpsys activity | ag ResumedActivity").read().strip()
    package_name = current_app.split('/')[0].split(" ")[-1]
    # print("Current package: ", package_name)
    return package_name


def start_app(device, package_name):
    start_component = find_start_component(device, package_name)
    if start_component:
        print(f"Start component: {start_component}")
        # start app
        print(f"Start app on device: {device}")
        os.system(
            f"""adb -s {device} shell am start -n "{start_component}" -a android.intent.action.MAIN -c android.intent.category.LAUNCHER""")

# 查找启动组件


def find_start_component(device, package_name):
    command = f"""adb -s {device} shell pm dump {package_name} |  grep -B 1 "android.intent.action.MAIN\\"" | grep {package_name}"""
    # print(command)
    out = os.popen(command).read().strip()
    component_list = []
    for line in out.splitlines():
        # print("line", line)
        for item in line.split(" "):
            if package_name in item:
                component_list.append(item)
    if not component_list:
        print("未找到启动组件")
        return None
    if len(component_list) == 1:
        return component_list[0]
    else:
        print("找到多个启动组件:")
        for i, component in enumerate(component_list, 1):
            print(f"{i}. {component}")

        user_choice = input("Choose a component to start: ")

        if 1 <= int(user_choice) <= len(component_list):
            component = component_list[int(user_choice) - 1]
            return component
        else:
            print("Invalid choice.")

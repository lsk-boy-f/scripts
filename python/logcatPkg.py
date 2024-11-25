#!/usr/bin/env python3

import argparse
import subprocess
import threading
import time

from device import get_connected_devices, select_device


def get_user_and_pids(package_name, device):
    """
    获取目标包名的用户和所有子进程的 PID
    """
    try:
        ps_result = subprocess.run(
            ["adb", "-s", device, "shell", "ps"],
            capture_output=True,
            text=True,
        )
        lines = ps_result.stdout.strip().split("\n")
        user = None
        pids = []

        # 查找目标包名的用户
        for line in lines:
            parts = line.split()
            if len(parts) >= 9 and package_name == parts[-1]:
                user = parts[0]  # 第一个字段是 USER
                break

        if not user:
            return None, []

        # 查找该用户的所有进程
        for line in lines:
            parts = line.split()
            if len(parts) >= 9 and parts[0] == user:
                pids.append(parts[1])  # 第二个字段是 PID

        return user, pids
    except Exception as e:
        print(f"获取用户和 PID 时出错: {e}")
        return None, []


def refresh_pids(package_name, device, pid_list):
    """
    定时刷新 PID 列表
    """
    while True:
        _, new_pids = get_user_and_pids(package_name, device)
        print(f"新的进程id：{new_pids}")
        pid_list.clear()
        pid_list.extend(new_pids)
        time.sleep(2)  # 每隔 2 秒刷新一次


def monitor_logs(package_name, device):
    """
    监控目标包名的所有进程日志
    """
    pid_list = []

    # 启动一个线程定时刷新 PID 列表
    refresh_thread = threading.Thread(target=refresh_pids, args=(
        package_name, device, pid_list), daemon=True)
    refresh_thread.start()

    try:
        print(f"开始监控设备 {device} 上包名为 '{package_name}' 的日志...")
        logcat_process = subprocess.Popen(
            ["adb", "-s", device, "logcat"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors='ignore',
            bufsize=1,
        )
        # # print(logcat_process.stdout)
        # for line in logcat_process.stdout:
        #     # print(f"process {pid_list}, line {line}")
        #     if any(f"{pid}" in line for pid in pid_list):
        #         print(line.strip())

        while True:
            for line in iter(logcat_process.stdout.readline, ''):
                if any(f"{pid}" in line for pid in pid_list):
                    print(line.strip())
    except KeyboardInterrupt:
        print("停止日志监控...")
        logcat_process.terminate()
    except Exception as e:
        print(f"日志监控时发生错误: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="监控特定包名的日志")
    parser.add_argument("-d", "--device", help="设备序列号 (使用 adb devices 获取)")
    parser.add_argument("-p", "--package", help="目标应用包名")
    args = parser.parse_args()

    devices = get_connected_devices()
    if not devices:
        print("未检测到连接的设备，请检查 adb 连接。")
        exit(1)

    # 如果没有指定设备，交互选择
    if not args.device:
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

    # 如果没有指定包名，提示用户输入
    if not args.package:
        target_package = input("请输入要监控的应用包名: ")
    else:
        target_package = args.package

    monitor_logs(target_package, device)

#!/usr/bin/env python3

import argparse
import subprocess
import threading
import time

from device import get_connected_devices, select_device


def get_user_and_pid(process_name, device):
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
        pid = None
        # print(f"lines: {lines}", process_name)

        # 查找目标包名的用户
        for line in lines:
            # print(process_name)
            # print(line)
            if process_name in line:
                parts = line.split()
                # print(parts)
                if len(parts) >= 9 and process_name == parts[-1]:
                    user = parts[0]  # 第一个字段是 USER
                    pid = parts[1]  # 第二个字段是 PID
                break

        return user, pid

    except Exception as e:
        print(f"获取用户和 PID 时出错: {e}")
        return None, None


def refresh_pids(process_name, device, pid_list):
    """
    定时刷新 PID 列表
    """
    while True:
        _, new_pid = get_user_and_pid(process_name, device)
        if not pid_list:
            print("========================================================")
            print(f"进程发生变化，当前进程id：{new_pid}")
            print("========================================================")
            pid_list.append(new_pid)
        else:
            if pid_list[-1] != new_pid:
                print("========================================================")
                print(f"进程发生变化，当前进程id：{new_pid}")
                print("========================================================")
                pid_list.clear()
                pid_list.append(new_pid)

        time.sleep(0.2)  # 每隔 0.2 秒刷新一次


def monitor_logs(process_name, device):
    """
    监控目标包名的所有进程日志
    """
    pid_list = []

    # 启动一个线程定时刷新 PID 列表
    refresh_thread = threading.Thread(target=refresh_pids, args=(
        process_name, device, pid_list), daemon=True)
    refresh_thread.start()

    try:
        print(f"开始监控设备 {device} 上包名为 '{process_name}' 的日志...")
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
    parser.add_argument("-p", "--process",
                        help="过滤的进程名字，如：com.android.systemui")
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
    if not args.process:
        target_process = input("请输入要监控的应用包名: ")
    else:
        target_process = args.process

    if target_process:
        monitor_logs(target_process, device)
    else:
        print("请指定要监控的进程名字")
        exit(1)

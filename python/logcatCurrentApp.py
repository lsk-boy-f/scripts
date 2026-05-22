#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import threading
import time

from lib import adb_utils
from lib import command_with_multi_device


def get_processes(package_name, device):
    """
    获取目标包名的所有进程（主进程和子进程）
    返回 [(pid, process_name), ...]
    """
    try:
        ps_result = subprocess.run(
            ["adb", "-s", device, "shell", "ps"],
            capture_output=True,
            text=True,
        )
        lines = ps_result.stdout.strip().split("\n")
        user = None
        processes = []

        for line in lines:
            parts = line.split()
            if len(parts) >= 9 and package_name == parts[-1]:
                user = parts[0]
                break

        if not user:
            return []

        for line in lines:
            parts = line.split()
            if len(parts) >= 9 and parts[0] == user:
                processes.append((parts[1], parts[-1]))

        return processes
    except Exception as e:
        print(f"获取进程列表时出错: {e}")
        return []


def select_processes(processes):
    """
    让用户选择要监控的进程，返回选中的进程名列表；None 表示全部
    """
    print("检测到以下进程：")
    for i, (pid, name) in enumerate(processes, 1):
        print(f"  {i}. {name} (pid: {pid})")
    print("  a. 全部")

    while True:
        choice = input("请选择要监控的进程 (输入数字，多个用逗号分隔，或输入 a 表示全部): ").strip()
        if choice.lower() == "a":
            return None

        try:
            indices = [int(x.strip()) for x in choice.split(",")]
            if all(1 <= i <= len(processes) for i in indices):
                return [processes[i - 1][1] for i in indices]
            print(f"请输入 1 到 {len(processes)} 之间的数字")
        except ValueError:
            print("输入无效，请重新选择")


def refresh_pids(package_name, device, pid_list, selected_names=None):
    """
    定时刷新 PID 列表
    """
    old_pids = set()
    while True:
        processes = get_processes(package_name, device)
        if selected_names is not None:
            new_pids = [pid for pid, name in processes if name in selected_names]
        else:
            new_pids = [pid for pid, _ in processes]

        new_pids_set = set(new_pids)
        if new_pids_set != old_pids:
            print(f"进程发生变化，当前进程 id：{new_pids}")
            old_pids = new_pids_set
            pid_list.clear()
            pid_list.extend(new_pids)

        time.sleep(0.2)


def monitor_logs(package_name, device, selected_names=None):
    """
    监控目标包名选定进程的日志
    """
    pid_list = []
    refresh_thread = threading.Thread(
        target=refresh_pids,
        args=(package_name, device, pid_list, selected_names),
        daemon=True,
    )
    refresh_thread.start()

    logcat_process = None
    try:
        label = "全部进程" if selected_names is None else ", ".join(selected_names)
        print(f"开始监控设备 {device} 上 '{package_name}' 的日志 ({label})...")
        logcat_process = subprocess.Popen(
            ["adb", "-s", device, "logcat"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="ignore",
            bufsize=1,
        )

        while True:
            if logcat_process.stdout is None:
                print("无法读取 logcat 输出")
                break
            for line in iter(logcat_process.stdout.readline, ""):
                if any(f"{pid}" in line for pid in pid_list):
                    print(line.strip())
    except KeyboardInterrupt:
        print("停止日志监控...")
        if logcat_process is not None:
            logcat_process.terminate()
    except Exception as e:
        print(f"日志监控时发生错误: {e}")


def logcat_current_app(device):
    package_name = adb_utils.get_current_package_name(device)
    print(f"当前前台应用: {package_name}")

    processes = get_processes(package_name, device)
    if not processes:
        print(f"未找到包名 '{package_name}' 的运行进程，请确认应用正在运行。")
        return

    if len(processes) == 1:
        pid, name = processes[0]
        print(f"仅有一个进程: {name} (pid: {pid})")
        monitor_logs(package_name, device)
    else:
        selected_names = select_processes(processes)
        monitor_logs(package_name, device, selected_names)


def main():
    command_with_multi_device.execute(logcat_current_app)


if __name__ == "__main__":
    main()

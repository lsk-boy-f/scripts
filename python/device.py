
import subprocess


def get_connected_devices():
    """
    获取当前连接的设备列表
    """
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
        )
        lines = result.stdout.strip().split("\n")[1:]  # 第一行是标题
        devices = [line.split("\t")[0] for line in lines if "device" in line]
        return devices
    except Exception as e:
        print(f"获取设备列表时出错: {e}")
        return []


def select_device(devices):
    """
    让用户选择目标设备
    """
    print("检测到以下设备：")
    for i, device in enumerate(devices):
        print(f"{i + 1}: {device}")
    choice = int(input("请选择设备 (输入数字): ")) - 1
    return devices[choice]

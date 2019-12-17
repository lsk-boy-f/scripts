import os


def get_device_id_list():
    """
    get android device serial list current connected to the pc
    """
    device_id_list = []
    command = "adb devices -l | sed '1d'| awk '{print $1}'"
    result = os.popen(command)
    device_id = result.readline().strip()
    if device_id != "":
        device_id_list.append(device_id)

    while device_id != "":
        device_id = result.readline().strip()
        if device_id != "":
            device_id_list.append(device_id)
    return device_id_list

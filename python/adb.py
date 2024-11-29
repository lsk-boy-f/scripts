import os


def start_activity(device_id, package_name, activity_name):
    """
    start activity in app
    """
    # print device, packageName
    print(f"Got device: {device_id}")
    command = "adb -s %s shell am start %s/%s" % (
        device_id, package_name, activity_name)
    os.system(command)

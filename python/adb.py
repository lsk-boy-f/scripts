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


def start_activity(device_id, package_name, activity_name):
    """
    start activity in app
    """
    # print device, packageName
    print("Got device: " + device_id)
    command = "adb -s %s shell am start %s/%s" % (device_id, package_name, activity_name)
    os.system(command)


def print_package_log(device_id, package_name):
    """
    print package's logcat
    """
    # print device, packageName
    print("Got device: " + device_id)
    command = "adb -s %s shell ps | grep %s | awk '{print $2}'" % (device_id, package_name)
    # print command
    p = os.popen(command)
    # for some applications,there are multiple processes,so we should get all the process id
    pid = p.readline().strip()
    filters = pid
    while pid != "":
        pid = p.readline().strip()
        if pid != '':
            filters = filters + "|" + pid
            # print 'command = %s;filters=%s'%(command, filters)
    if filters != '':
        cmd = 'adb -s %s logcat -v color | grep --color=always -E "%s" ' % (device_id, filters)
        os.system(cmd)
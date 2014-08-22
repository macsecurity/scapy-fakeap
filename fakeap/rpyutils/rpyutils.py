import subprocess
import re
import os
import struct


class Level:
    CRITICAL = 0
    INFO = 1
    DEBUG = 2


class Color:
    GREY = '\x1b[1;37m'
    GREEN = '\x1b[1;32m'
    BLUE = '\x1b[1;34m'
    YELLOW = '\x1b[1;33m'
    RED = '\x1b[1;31m'
    MAGENTA = '\x1b[1;35m'
    CYAN = '\x1b[1;36m'


def clr(color, text):
    return color + str(text) + '\x1b[0m'


def check_root():
    if not os.geteuid() == 0:
        printd(clr(Color.RED, "Run as root."), Level.CRITICAL)
        exit(1)


def check_root_shadow():
    dev_null = open(os.devnull, 'w')

    try:
        subprocess.check_output(['cat', '/etc/shadow'], stderr=dev_null)
    except subprocess.CalledProcessError:
        printd(clr(Color.RED, "Run as root."), Level.CRITICAL)
        exit(1)


def set_monitor_mode(wlan_dev, enable=True):
    monitor_dev = None
    if enable:
        result = subprocess.check_output(['airmon-ng', 'start', wlan_dev])
        if not "monitor mode enabled on" in result:
            printd(clr(Color.RED, "ERROR: Airmon could not enable monitor mode on device %s. Make sure you are root, and that" \
                                       "your wlan card supports monitor mode." % wlan_dev), Level.CRITICAL)
            exit(1)
        monitor_dev = re.search(r"monitor mode enabled on (\w+)", result).group(1)

        printd("Airmon set %s to monitor mode on %s" % (wlan_dev, monitor_dev), Level.INFO)
    else:
        subprocess.check_output(['airmon-ng', 'stop', wlan_dev])

    return monitor_dev


def printd(string, level):
    if VERBOSITY >= level:
        print(string)


def hex_offset_to_string(byte_array):
    temp = byte_array.replace("\n", "")
    temp = temp.replace(" ", "")
    return temp.decode("hex")


def get_frequency(channel):
    if channel == 14:
        freq = 2484
    else:
        freq = 2407 + (channel * 5)

    freq_string = struct.pack("<h", freq)

    return freq_string


def mac_to_bytes(mac):
    return ''.join(chr(int(x, 16)) for x in mac.split(':'))


def bytes_to_mac(byte_array):
    return ':'.join("{:02x}".format(ord(byte)) for byte in byte_array)


VERBOSITY = Level.CRITICAL
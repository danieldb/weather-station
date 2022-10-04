import json
from operator import contains
from pprint import pprint
import sys
import glob
import serial
from datetime import datetime


def serial_ports():
    """Lists serial port names

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of the serial ports available on the system
    """
    if sys.platform.startswith("win"):
        ports = ["COM%s" % (i + 1) for i in range(256)]
    elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob("/dev/tty[A-Za-z]*")
    elif sys.platform.startswith("darwin"):
        ports = glob.glob("/dev/tty.*")
    else:
        raise EnvironmentError("Unsupported platform")

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def auto_select_serial_port():
    ports = serial_ports()
    for i in ports:
        if not i.__contains__("Bluetooth"):
            return i


print()
port = auto_select_serial_port()
dht_bmp = serial.Serial(port, 9600)
data = {}
while True:
    try:
        line = dht_bmp.read_until(b"\n")
        print(line)
        vars = line.decode("utf8").split(",")
        for i in vars:
            var = i.split(":")
            data[var[0]] = var[1]
        data["time"] = datetime.now().isoformat()
        pprint(data)
    except KeyboardInterrupt:
        dht_bmp.close()
        break


dht_bmp.close()

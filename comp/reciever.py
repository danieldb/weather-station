import json
from operator import contains
from pprint import pprint
import sys
import glob
import serial
from datetime import datetime
import psycopg


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


def log_to_db(
    data,
    schema_name="public",
    table_name="data",
):
    with psycopg.connect(
        "host=localhost port=5432 dbname=postgres connect_timeout=10"
    ) as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            cur.execute(
                f"""INSERT INTO {schema_name}.{table_name}("PER", 
                                            "WSPD", 
                                            "PRES", 
                                            "TEMP", 
                                            "ALT", 
                                            "HUM", 
                                            "RNFL", 
                                            "WNDR", 
                                            "TSTMP") VALUES (
                                                {data.get("PER")},
                                                {data.get("WSA")},
                                                {data.get("PBMP")},
                                                {data.get("TDHT")},
                                                {data.get("ABMP")},
                                                {data.get("HDHT")},
                                                {data.get("WLRG")},
                                                null,
                                                '{data.get("TIME")}'::TIMESTAMP)"""
            )
            conn.commit()


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
            data[var[0]] = var[1].replace("\n", "").replace("\r", "")
        data["TIME"] = datetime.now()
        pprint(data)

    except KeyboardInterrupt:
        dht_bmp.close()
        break

dht_bmp.close()

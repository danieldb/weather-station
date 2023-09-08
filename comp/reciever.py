import sys
import glob
import serial
from datetime import datetime
import psycopg
import csv
from os.path import exists
import os
import boto3
from dotenv import load_dotenv, dotenv_values


PERSISTER = "LIVE"  # DDB, CSV, or LOCAL

if PERSISTER == "DDB":
    load_dotenv("../.env", override=True)
    env = dotenv_values()
    os.environ["AWS_ACCESS_KEY_ID"] = env.get("WRITER_ACCESS_KEY_ID")
    os.environ["AWS_SECRET_ACCESS_KEY"] = env.get("WRITER_SECRET_ACCESS_KEY")
    os.environ["AWS_DEFAULT_REGION"] = env.get("AWS_DEFAULT_REGION")


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


def log_to_local_db(
    data: dict[str:float],
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


session = boto3.Session()
ddb = session.client("dynamodb")


def log_to_ddb(data: dict[str:float]):
    ddb.put_item(
        TableName="weather-station",
        Item={
            "PER": {"N": str(data.get("PER"))},  # sampling period (ms)
            "WSA": {
                "N": str(data.get("WSA"))
            },  # wind speed average (encoder ticks / period)
            "PBMP": {"N": str(data.get("PBMP"))},  # pressure bmp180 (hPa)
            "TDHT": {"N": str(data.get("TDHT"))},  # temperature dht22 (deg C)
            "ABMP": {"N": str(data.get("ABMP"))},  # altitude bmp180 (m)
            "HDHT": {"N": str(data.get("HDHT"))},  # humidity dht22 (%)
            "WLRG": {"N": str(data.get("WLRG"))},  # rain gague water level (idk yet)
            "WDIR": {"N": str(data.get("WDIR"))},  # wind direction (idk yet)
            "TIMESTAMP": {"N": str(data.get("TIME"))},  # timestamp (sec)
        },
    )


def log_to_csv(data: dict[str:float], filename="data.csv"):
    if not exists("data.csv"):
        with open("data.csv", "w") as csvfile:
            csvfile.write("ABMP,HDHT,PBMP,PER,TBMP,TDHT,WLRG,WSA,WDIR,TIME\n")
    print("loggin")
    with open("data.csv", "a") as csvfile:
        writer = csv.writer(csvfile, delimiter=",", quotechar="'")
        writer.writerow(
            [
                data.get("ABMP"),
                data.get("HDHT"),
                data.get("PBMP"),
                data.get("PER"),
                data.get("TBMP"),
                data.get("TDHT"),
                data.get("WLRG"),
                data.get("WSA"),
                data.get("WDIR"),
                data.get("TIME"),
            ]
        )

def log_to_temp_storage(data: dict[str:float], filename="data.csv"):
    print("temp loggin")
    with open("new_data.csv", "w") as csvfile:
        csvfile.write("ABMP,HDHT,PBMP,PER,TBMP,TDHT,WLRG,WSA,WDIR,TIME\n")
        writer = csv.writer(csvfile, delimiter=",", quotechar="'")
        writer.writerow(
            [
                data.get("ABMP"),
                data.get("HDHT"),
                data.get("PBMP"),
                data.get("PER"),
                data.get("TBMP"),
                data.get("TDHT"),
                data.get("WLRG"),
                data.get("WSA"),
                data.get("WDIR"),
                data.get("TIME"),
            ]
        )

port = auto_select_serial_port()
arduino = serial.Serial(port, 9600)
data = {}
while True:
    try:
        # format line into data
        line = arduino.read_until(b"\n").replace(b"\r\n", b"")
        vars = line.decode("utf8").split(",")
        for i in vars:
            var = i.split(":")
            data[var[0]] = var[1]
        data["TIME"] = datetime.now().timestamp()

        print(data)

        # send data to specified destination
        if PERSISTER == "LOCAL":
            log_to_local_db(data)
        elif PERSISTER == "CSV":
            log_to_csv(data)
        elif PERSISTER == "LIVE":
            log_to_temp_storage(data)
        elif PERSISTER == "DDB":
            log_to_ddb(data)
        else:
            raise Exception(
                "Please select a valid destination for persisting the weather data"
            )

    except KeyboardInterrupt:
        arduino.close()
        break

arduino.close()

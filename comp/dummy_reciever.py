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
import random
from time import sleep


PERSISTER = "LIVE"  # DDB, CSV, or LOCAL


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


def log_to_temp_storage(data: dict[str:float], filename="new_data.csv"):
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


while True:
    data = {
        "ABMP": -58.53,
        "HDHT": 69.20,
        "PBMP": 1020.30,
        "PER": 5000,
        "TBMP": 20.50,
        "TDHT": 18.50,
        "WLRG": 0,
        "WSA": random.randint(0, 100),
        "WDIR": -1,  # None,
        "TIME": datetime.now().timestamp(),
    }
    try:
        sleep(0.1)
        # format line into data

        print(data)

        # send data to specified destination
        if PERSISTER == "CSV":
            log_to_csv(data)
        elif PERSISTER == "LIVE":
            log_to_temp_storage(data)
        else:
            raise Exception(
                "Please select a valid destination for persisting the weather data"
            )

    except KeyboardInterrupt:
        break

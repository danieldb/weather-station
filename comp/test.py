import psycopg
from datetime import datetime
import csv
from dotenv import load_dotenv, dotenv_values
import os
from google.cloud.sql.connector import Connector
import sqlalchemy
import boto3

load_dotenv("../.env", override=True)
env = dotenv_values()
os.environ["AWS_ACCESS_KEY_ID"] = env.get("WRITER_ACCESS_KEY_ID")
os.environ["AWS_SECRET_ACCESS_KEY"] = env.get("WRITER_SECRET_ACCESS_KEY")
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
sample = {
    "ABMP": -58.53,
    "HDHT": 69.20,
    "PBMP": 1020.30,
    "PER": 5000,
    "TBMP": 20.50,
    "TDHT": 18.50,
    "WLRG": 0,
    "WSA": 0.00,
    "WDIR": -1,  # None,
    "TIME": datetime.now().timestamp(),
}

session = boto3.Session()
ddb = session.client("dynamodb")


def log_to_ddb(data: dict[str:float]):
    ddb.put_item(
        TableName="weather-station",
        Item={
            "PER": {"N": str(data.get("PER"))},  # sampling period
            "WSA": {"N": str(data.get("WSA"))},  # wind speed average
            "PBMP": {"N": str(data.get("PBMP"))},  # pressure bmp180
            "TDHT": {"N": str(data.get("TDHT"))},  # temperature dht22
            "ABMP": {"N": str(data.get("ABMP"))},  # altitude bmp180
            "HDHT": {"N": str(data.get("HDHT"))},  # humidity dht22
            "WLRG": {"N": str(data.get("WLRG"))},  # rain gague water level
            "WDIR": {"N": str(data.get("WDIR"))},  # wind direction
            "TIMESTAMP": {"N": str(data.get("TIME"))},  # timestamp
        },
    )


log_to_ddb(sample)

exit(0)
# Connect to an existing database
with open("/Users/danieldb/Desktop/Weather Station/comp/data.csv", "a") as csvfile:
    writer = csv.writer(csvfile, delimiter=",", quotechar="|")
    writer.writerow([1, 2, 3, 4, 5, 6, 7, 8, 9])

INSTANCE_CONNECTION_NAME = env.get(
    "INSTANCE_CONNECTION"
)  # i.e demo-project:us-central1:demo-instance
print(f"Your instance connection name is: {INSTANCE_CONNECTION_NAME}")
DB_USER = env.get("USER")
DB_PASS = env.get("PASSWORD")
DB_NAME = env.get("DB")

connector = Connector()


def getconn():
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME, "pymysql", user=DB_USER, password=DB_PASS, db=DB_NAME
    )
    return conn


# create connection pool with 'creator' argument to our connection object function
pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

with pool.connect() as db_conn:
    # create ratings table in our movies database
    db_conn.execute(
        """CREATE TABLE IF NOT EXISTS test 
        ( 
        ABMP FLOAT, 
        HDHT FLOAT, 
        PBMP FLOAT, 
        PER FLOAT, 
        TBMP FLOAT, 
        TDHT FLOAT, 
        WLRG FLOAT, 
        WSA FLOAT, 
        TIME TIMESTAMP
        );"""
    )
    # insert data into our ratings table
    insert_stmt = sqlalchemy.text(
        """INSERT INTO test (ABMP,HDHT,PBMP,PER,TBMP,TDHT,WLRG,WSA,TIME) 
        VALUES 
        (:ABMP,:HDHT,:PBMP,:PER,:TBMP,:TDHT,:WLRG,:WSA,:TIME)""",
    )

    # insert entries into table
    db_conn.execute(
        insert_stmt,
        ABMP=sample.get("ABMP"),
        HDHT=sample.get("HDHT"),
        PBMP=sample.get("PBMP"),
        PER=sample.get("PER"),
        TBMP=sample.get("TBMP"),
        TDHT=sample.get("TDHT"),
        WLRG=sample.get("WLRG"),
        WSA=sample.get("WSA"),
        TIME=sample.get("TIME"),
    )

    # query and fetch ratings table
    results = db_conn.execute("SELECT * FROM ratings").fetchall()

    # show results
    for row in results:
        print(row)

connector.close()
exit(0)
with psycopg.connect(
    "host=localhost port=5432 dbname=postgres connect_timeout=10"
) as conn:
    # Open a cursor to perform database operations
    with conn.cursor() as cur:
        # Execute a command: this creates a new table

        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no SQL injections!)
        cur.execute(
            f"""INSERT INTO public.data("PER", 
                                          "WSPD", 
                                          "PRES", 
                                          "TEMP", 
                                          "ALT", 
                                          "HUM", 
                                          "RNFL", 
                                          "WNDR", 
                                          "TSTMP") VALUES (
                                            {sample.get("PER")},
                                            {sample.get("WSA")},
                                            {sample.get("PBMP")},
                                            {sample.get("TDHT")},
                                            {sample.get("ABMP")},
                                            {sample.get("HDHT")},
                                            {sample.get("WLRG")},
                                            null,
                                            '{sample.get("TIME")}'::TIMESTAMP)"""
        )

        # Query the database and obtain data as Python objects.
        cur.execute("SELECT * FROM public.data")
        cur.fetchone()
        # will return (1, 100, "abc'def")

        # You can use `cur.fetchmany()`, `cur.fetchall()` to return a list
        # of several records, or even iterate on the cursor
        for record in cur:
            print(record)

        # Make the changes to the database persistent
        conn.commit()

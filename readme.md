# How to set up your own weatherstation!

## Step 1, Hardware

I used many different sensors and built my own sensors in some cases. All the designs for these parts, including 3d models, other products, and pictures can either be found here or will be added once I finish the project.

#### Products

- Rotary Encoder ()
- BMP180 ()
- DHT22 ()
- Arduino **\_** ()
- Raspberry Pi 2B+ () any RPi will work

#### 3d models

- Anemometer
  - Hub (3mf: ) (stl: )
  - Cups (3mf: ) (stl: )

#### Pictures for other hardware

### Assemble The Hardware

The next step is to connect the hardware all together, whether that is with jumper wires, perf board, or pcbs, the schematics can be found there -> ().

Sidenote:
Thanks so much to the Brown Design Workshop for their community resource of tools and materials, this project was possible because of those resources.

## Step 2, Software

### Flash Arduino

The code found in `arduino_sensors.ino` lets the arduino read from the sensors and send their data (over UART serial) to a computer or other microcontroller. In this case, there is another reciever script which will pick up and persist this data.

First, clone this repository using
`git clone https://github.com/danieldb/weather-station`
and open the `arduino_sensors.ino` file in the arduino ide ()
Next, select `Tools > Port` and make sure your board is selected. If you ever open the serial monitor, make sure to close it before running the python script.
After that do the same with `Tools > Board`.

### Upload code to RPi

After flashing the arduino, you are ready to use the `reciever.py` script. This script takes the serial communication and saves it in the following 3 possible ways.

1. Save to CSV file

- this is the easiest method
- this is not a good long term storage option

2. Save in local Postgresql database with psycopg

- this is a local storage solution
- local Postgresql can be difficult to set up

3. Save to AWS DynamoDB with boto3

- very reliable
- able to be quried from a different application
- fairly easy to set up

I am not going to explain how to set up a DynamoDB table or a local Postgresql instance, but I will say how to set up your code environment so that the reciever can read your AWS credentials.

#### Where To Put AWS Credentials?

I am using the dotenv python package in order to store my access key id and secret access key. To make this dotenv file, create a file in the root of this repository called `.env` and populate it with the following:

    WRITER_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
    WRITER_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID"
    AWS_DEFAULT_REGION="your-region"

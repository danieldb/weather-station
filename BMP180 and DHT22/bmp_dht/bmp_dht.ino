#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#define seaLevelPressure_hPa 1013.25

#define DHTPIN 3
#define DHTTYPE DHT22

uint32_t delayMS;

DHT_Unified dht(DHTPIN, DHTTYPE);

Adafruit_BMP085 bmp;

void setup()
{

  Serial.begin(9600);
  // Initialize device.
  dht.begin();

  sensor_t sensor;
  // Set delay between sensor readings based on sensor details.
  delayMS = sensor.min_delay / 1000;

  if (!bmp.begin())
  {
    Serial.println("Could not find a valid BMP085 sensor, check wiring!");
    while (1)
    {
    }
  }
}

void loop()
{

  Serial.print("TBMP:");
  Serial.print(bmp.readTemperature());
  Serial.print(","); // deg C

  Serial.print("PBMP:");
  Serial.print(bmp.readPressure());
  Serial.print(","); // pascals Pa

  Serial.print("ABMP:");
  Serial.print(bmp.readAltitude());
  Serial.print(","); // meters

  Serial.print("PASBMP:");
  Serial.print(bmp.readSealevelPressure());
  Serial.print(","); // pascals Pa

  Serial.print("RABMP:");
  Serial.print(bmp.readAltitude(seaLevelPressure_hPa * 100));
  Serial.print(","); // meters

  sensors_event_t event;
  dht.temperature().getEvent(&event);

  Serial.print("TDHT:");
  Serial.print(event.temperature);
  Serial.print(","); // deg C

  dht.humidity().getEvent(&event);

  Serial.print("HDHT:");
  Serial.print(event.relative_humidity);
  Serial.println(); // percent %

  delay(delayMS);
}

#include <Wire.h>
#include <Adafruit_BMP085_U.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#define seaLevelPressure_hPa 1013.25

#define DHTPIN 9
#define DHTTYPE DHT22

const byte encoderPinA = 10; // outputA digital pin2
const byte encoderPinB = 11; // outoutB digital pin3
volatile double ticks = 0;
double protectedTicks = 0;
double previousTicks = 0;
uint32_t curMillis = 0;
uint32_t lastMillis = 0;

#define readA bitRead(PIND, encoderPinA) // faster than digitalRead()
#define readB bitRead(PIND, encoderPinB) // faster than digitalRead()

uint32_t delayMS;

DHT_Unified dht(DHTPIN, DHTTYPE);

Adafruit_BMP085_Unified bmp;

void setup()
{

  Serial.begin(9600);
  Serial.println("Serial: GOOD");
  // Initialize device.
  pinMode(encoderPinA, INPUT_PULLUP);
  pinMode(encoderPinB, INPUT_PULLUP);
  Serial.println("Encoder: INITIALIZED");
  dht.begin();
  Serial.println("DHT: GOOD");

  if(!bmp.begin())
  {
    /* There was a problem detecting the BMP085 ... check your connections */
    Serial.println("BMP: BAD");
  }else{
    Serial.println("BMP: GOOD");
  }
  
  attachInterrupt(digitalPinToInterrupt(encoderPinA), isrA, CHANGE);
  attachInterrupt(digitalPinToInterrupt(encoderPinB), isrB, CHANGE);
  Serial.println("Encoder: GOOD");
}

long secs = 100;

void loop()
{
    curMillis = millis();
    if (curMillis - lastMillis >= secs)
    {
        noInterrupts();
        protectedTicks = ticks;
        ticks = 0;
        Serial.print("WSA:"); // wind speed anemometer
        Serial.print(protectedTicks);
        Serial.print(","); // ticks / period (see period below, also, there should be 600 t/r)
        
        //Serial.print("WLRG:"); // water level rain gague
        //Serial.print(analogRead(0));
        //Serial.print(","); // idk units rn

        sensors_event_t dht_event;
        dht.temperature().getEvent(&dht_event);
      
        Serial.print("TDHT:"); // temp dht
        Serial.print(dht_event.temperature);
        Serial.print(","); // deg (F)
      
        dht.humidity().getEvent(&dht_event);
      
        Serial.print("HDHT:"); // humidity dht
        Serial.print(dht_event.relative_humidity);
        Serial.print(","); // percent (%)
        
        sensors_event_t bmp_event;
        bmp.getEvent(&bmp_event);
        Serial.print("PBMP:"); // pressure bmp
        Serial.print(bmp_event.pressure);
        Serial.print(","); // Hectopascal or mllibar (hPa or mb)
        
        float bmp_temperature;
        bmp.getTemperature(&bmp_temperature);
        Serial.print("TBMP:"); // temp bmp
        Serial.print(bmp_temperature);
        Serial.print(","); // degs (C)
        
        float seaLevelPressure = SENSORS_PRESSURE_SEALEVELHPA;
        Serial.print("ABMP:"); // altitude bmp
        Serial.print(bmp.pressureToAltitude(seaLevelPressure, bmp_event.pressure, bmp_temperature)); 
        Serial.print(","); // meters (m)
        
        Serial.print("PER:"); // Period
        Serial.print(curMillis-lastMillis);
        Serial.println(); // percent %
        lastMillis = curMillis;
        
        
        
        interrupts();
    }

}

void isrA()
{
    if (readB == readA)
    {
        ticks++;
    }
    else
    {
        ticks--;
    }
}
void isrB()
{
    if (readA == readB)
    {
        ticks--;
    }
    else
    {
        ticks++;
    }
}

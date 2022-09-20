const byte encoderPinA = 2; // outputA digital pin2
const byte encoderPinB = 3; // outoutB digital pin3
volatile double ticks = 0;
double protectedTicks = 0;
double previousTicks = 0;
int curMillis = 0;
int lastMillis = 0;

#define readA bitRead(PIND, 2) // faster than digitalRead()
#define readB bitRead(PIND, 3) // faster than digitalRead()

void setup()
{
    Serial.begin(250000);

    pinMode(encoderPinA, INPUT_PULLUP);
    pinMode(encoderPinB, INPUT_PULLUP);

    attachInterrupt(digitalPinToInterrupt(encoderPinA), isrA, CHANGE);
    attachInterrupt(digitalPinToInterrupt(encoderPinB), isrB, CHANGE);
}

void loop()
{
    curMillis = millis();
    if (curMillis - lastMillis >= 1000)
    {
        noInterrupts();
        lastMillis = curMillis;
        protectedTicks = ticks;
        ticks = 0;
        interrupts();
        Serial.print("ticks:");
        Serial.println(protectedTicks);
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

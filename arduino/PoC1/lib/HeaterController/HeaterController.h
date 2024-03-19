#ifndef HEATERCONTROLLER_H
#define HEATERCONTROLLER_H

#include <OneWire.h>
#include <DallasTemperature.h>

class HeaterController {
public:
    HeaterController(uint8_t oneWireBus, uint8_t heaterPin);
    void setTarget(float degreesC);
    float read();
    void update();

private:
    OneWire oneWire;
    DallasTemperature sensors;
    float targetTemperature;
    unsigned long lastRequestTime;
    float currentTemperature;
    int resolution;
    uint8_t heaterPin;
    unsigned long millisToWait; // Stores the calculated wait time for conversion
    void controlHeater();
    void calculateWaitForConversion(); // Function to calculate wait time
};

#endif // HEATERCONTROLLER_H
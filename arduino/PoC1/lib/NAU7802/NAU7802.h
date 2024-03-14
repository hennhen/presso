#ifndef NAU7802_H
#define NAU7802_H

#include <Adafruit_NAU7802.h>
#include <Wire.h>

class NAU7802 {
private:
    Adafruit_NAU7802 _scale;
    float _calibrationFactor;
    float _weight;

public:
    NAU7802(float calibrationFactor);
    bool init();
    bool available();
    bool tare();
    float read();
};

#endif // NAU7802_H
#ifndef NAU7802_H
#define NAU7802_H

#include <Adafruit_NAU7802.h>
#include <Wire.h>

class NAU7802 {
private:
    Adafruit_NAU7802 _scale;
    float _calibrationFactor;
    float _weight;
    float _lastWeight;
    short _averagingCountTimes = 5;
    short _currentAverageCount = 0;
    float _cumulative4Average = 0;

public:
    NAU7802(float calibrationFactor);
    bool init();
    bool available();
    bool tare();
    float read();
};

#endif // NAU7802_H
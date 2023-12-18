#ifndef HX711_SCALE_H
#define HX711_SCALE_H

#include <Arduino.h>
#include "HX711.h"

class HX711_Scale {
public:
    HX711_Scale(int dout, int sck, float calibration_factor);
    float weight;
    void tare();
    void updateWeight();
    void reset();

private:
    HX711 scale;
    float calibration_factor;
    float sum_readings;  // Buffer to store sum last 5 readings
    uint8_t count = 0;
};

#endif // HX711_SCALE_H

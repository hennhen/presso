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

private:
    HX711 scale;
    float calibration_factor;
};

#endif // HX711_SCALE_H

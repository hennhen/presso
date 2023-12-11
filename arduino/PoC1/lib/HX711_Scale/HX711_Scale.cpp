#include "HX711_Scale.h"
#include <Arduino.h>

HX711_Scale::HX711_Scale(int dout, int sck, float calibration_factor) {
    scale.begin(dout, sck);
    this->calibration_factor = calibration_factor;
    scale.set_scale(calibration_factor);
    scale.tare();
}

void HX711_Scale::tare() {
    scale.tare();
}

void HX711_Scale::updateWeight() {
    weight = scale.get_units();
    if (weight < 0) {
        weight = 0;
    }
}

#include "HX711_Scale.h"
#include <Arduino.h>

HX711_Scale::HX711_Scale(int dout, int sck, float calibration_factor) 
: scale(dout, sck), _calibration_factor(calibration_factor) {
    scale.set_scale(calibration_factor);
    scale.tare(10);
    count = 0;
}

bool HX711_Scale::init() {
  // scale = new HX711(_dout, _sck);
  scale.set_scale(_calibration_factor);
  scale.tare(10);
  count = 0;
  return true;
}

void HX711_Scale::tare() { scale.tare(10); }

void HX711_Scale::reset() {
  scale.tare(10);
  weight = 0.0;
  count = 0;
  sum_readings = 0;
}

// Uses the non-blocking function
// Will return the weight if the scale is ready
// Also takes average of 5 readings
// Scale is 80 hz, so 5 readings is 62.5 ms
// Wont use get units, will increment one everytime this fuction is called
// if not 5 times yet, return last average reading
void HX711_Scale::updateWeight() {
  if (scale.is_ready()) {
    sum_readings += scale.get_units_direct();
    count++;

    if (count % 8 == 0) {
      weight = sum_readings / 8; // Calculate average
      if (weight < 0.0) {
        weight = 0.0;
      }
      // Serial1.println(weight);
      sum_readings = 0; // Reset sum for the next set of 5 readings
      count = 0;        // Reset count for the next set of 5 readings
    }
  }
}

#ifndef HX711_SCALE_H
#define HX711_SCALE_H

#include "HX711.h"
#include <Arduino.h>

class HX711_Scale {
public:
  HX711_Scale(int dout, int sck, float calibration_factor);
//   bool init();
  float weight;
  void tare();
  void updateWeight();
  void reset();

private:
  HX711 scale;
  byte _dout, _sck;
  float _calibration_factor;
  float sum_readings; // Buffer to store sum last 5 readings
  uint8_t count = 0;
};

#endif // HX711_SCALE_H

#ifndef PressureSensor_H
#define PressureSensor_H

#include <Arduino.h>

class PressureSensor {
public:
  explicit PressureSensor(int sensorPin);
  float pressure_filtered;
  float readPressure();  // Reads and returns the filtered pressure value

private:
  int _sensorPin;
  float _pressurePrev;
  const float _minRaw;
  const float _maxRaw;
  const float _minScaled;
  const float _maxScaled;
  const float _beta;  // Beta value for the filter

  static float mapfloat(float x, float in_min, float in_max, float out_min, float out_max);
  static float calculateBeta();
};


#endif
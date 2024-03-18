#ifndef ADSPressureSensor_H
#define ADSPressureSensor_H

#include <Arduino.h>
#include <ADS1X15.h>

class ADSPressureSensor {
public:
  ADSPressureSensor(uint8_t address = 0x48, uint8_t gain = 0, uint8_t dataRate = 6);
  float readPressure();  // Reads and returns the pressure value in bars

private:
  ADS1115 _ads;  // ADS1115 instance
  uint8_t _gain;
  uint8_t _dataRate;
  float _pressure;
  
  // Pressure sensor voltage to pressure conversion constants
  const float _minVoltage = 0.5;   // Minimum voltage output at 0 bars
  const float _maxVoltage = 4.5;   // Maximum voltage output at 17.24 bars
  const float _minPressure = 0.0;  // Minimum pressure in bars
  const float _maxPressure = 17.24; // Maximum pressure in bars

  float voltageToBars(float voltage);
};

#endif // ADSPressureSensor_H
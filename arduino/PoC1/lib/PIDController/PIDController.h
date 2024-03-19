#ifndef PIDController_H
#define PIDController_H

#include "ADSPressureSensor.h"
#include "MotorController.h"
#include <Arduino.h>

class PIDController {
public:
  PIDController(MotorController &motor, ADSPressureSensor &sensor);
  short updateDynamic(float target);
  void setParameters(float kp, float ki, float kd); // Set PID parameters
  void setReady(bool ready); // Set the PID controller to ready
  bool isReady();            // Check if the PID controller is ready
  float _kp, _ki, _kd;

private:
  MotorController &_motor;
  ADSPressureSensor &_sensor;
  short _sampleTime = 20;
  unsigned long _lastUpdateTime;
  short _lastControlVariable;
  float _eIntegral, _ePrev, _eDerivative;
  unsigned long _prevT;
  bool _ready;

  float calculateControlVariable(float error, float deltaTime);
};

#endif

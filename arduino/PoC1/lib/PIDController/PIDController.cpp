#include "PIDController.h"
#include "ADSPressureSensor.h"
#include "MotorController.h"

PIDController::PIDController(MotorController &cytronMotor,
                             ADSPressureSensor &sensor)
    : _motor(cytronMotor), _sensor(sensor), _kp(0), _ki(0), _kd(0),
      _eIntegral(0), _ePrev(0), _eDerivative(0), _lastUpdateTime(0),
      _ready(false) {}

void PIDController::setReady(bool ready) { _ready = ready; }

bool PIDController::isReady() { return _ready; }

short PIDController::updateDynamic(float target) {
  unsigned long currT = millis();

  // Check Sample Time
  if (currT - _lastUpdateTime < _sampleTime) {
    // Sample time has not passed
    return _lastControlVariable;
  }

  float deltaTime = (currT - _lastUpdateTime) / 1000.0; 

  float currentPressure = _sensor.readPressure();
  float error = target - currentPressure; // Use target instead of _setpoint
  _eDerivative = (error - _ePrev) / deltaTime;
  _eIntegral += error * deltaTime;

  /** TODO: Add integral clamping **/ 

  // Calculate control variable
  short controlVariable =
      (short)round(_kp * error + _ki * _eIntegral + _kd * _eDerivative);
  _ePrev = error;

  if (controlVariable > 126) {
    controlVariable = 126;
  } else if (controlVariable < 0) {
    controlVariable = 0;
  }

  // Serial1.println(controlVariable);

  _motor.setDutyCycle(-controlVariable);
  _lastControlVariable = controlVariable;
  _lastUpdateTime = currT; // Update the last update time
  return (controlVariable);
}

void PIDController::setParameters(float kp, float ki, float kd, short sampleTime) {
  _kp = kp;
  _ki = ki;
  _kd = kd;
  _eIntegral = 0;   // Reset integral component when parameters change
  _ePrev = 0;       // Reset previous error
  _eDerivative = 0; // Reset derivative component
  _lastUpdateTime = 0; // Reset last update time
  _sampleTime = sampleTime;
}

void PIDController::reset(){
  _ready = false;
  _eIntegral = 0;
  _ePrev = 0;
  _eDerivative = 0;
  _lastUpdateTime = 0;
  _lastControlVariable = 0;
}
#include "PIDController.h"

PIDController::PIDController(CytronController& motor, PressureSensor& sensor)
: _motor(motor), _sensor(sensor), _setpoint(0), _kp(0), _ki(0), _kd(0), _eIntegral(0), _ePrev(0), _eDerivative(0), _prevT(millis()) {
}

float PIDController::update() {
    unsigned long currT = millis();
    float deltaTime = (currT - _prevT) / 1000.0; // Convert to seconds
    _prevT = currT;

    float pressure = _sensor.readPressure();
    float error = _setpoint - pressure;
    _eDerivative = (error - _ePrev) / deltaTime;
    _eIntegral += error * deltaTime;
    float controlVariable = _kp * error + _ki * _eIntegral + _kd * _eDerivative;
    _ePrev = error;

    if (controlVariable > 255) {
        controlVariable = 255;
    } else if (controlVariable < 0) {
        controlVariable = 0;
    }

    _motor.setSpeed(controlVariable);
    return(controlVariable);
}

void PIDController::setParameters(float setpoint, float kp, float ki, float kd) {
    _setpoint = setpoint;
    _kp = kp;
    _ki = ki;
    _kd = kd;
    _eIntegral = 0; // Reset integral component when parameters change
    _ePrev = 0; // Reset previous error
    _eDerivative = 0; // Reset derivative component
}


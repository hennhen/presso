#ifndef PIDController_H
#define PIDController_H

#include <Arduino.h>
#include "MotorController.h" 
#include "ADSPressureSensor.h"

class PIDController {
public:
    PIDController(MotorController& motor, ADSPressureSensor& sensor);
    float updateStatic(); // Update PID calculations and control the motor
    float updateDynamic(float target); // Update PID calculations and control the motor
    void setParameters(float setpoint, float kp, float ki, float kd); // Set PID parameters

private:
    MotorController& _motor;
    ADSPressureSensor& _sensor;
    float _setpoint;
    float _kp, _ki, _kd;
    float _eIntegral, _ePrev, _eDerivative;
    unsigned long _prevT;

    float calculateControlVariable(float error, float deltaTime);
};

#endif

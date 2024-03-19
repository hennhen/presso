#ifndef CytronController_H
#define CytronController_H

#include <Arduino.h>
#include "MotorController.h"

class CytronController : public MotorController {
  public:
    CytronController(uint8_t pwmPin, uint8_t dirPin); // Constructor
    void setDutyCycle(short value) override; // This now correctly overrides the base class method
    void stop() override; // Stop the motor

  private:
    uint8_t _pwmPin;
    uint8_t _dirPin;
};

#endif

#ifndef CytronController_H
#define CytronController_H

#include <Arduino.h>

class CytronController {
  public:
    CytronController(uint8_t pwmPin, uint8_t dirPin); // Constructor
    void setSpeed(short value); // Set the speed and direction of the motor
    void stop(); // Stop the motor

  private:
    uint8_t _pwmPin;
    uint8_t _dirPin;
};

#endif

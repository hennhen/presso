#ifndef CytronController_H
#define CytronController_H

#include <Arduino.h>

class CytronController {
  public:
    CytronController(int pwmPin, int dirPin); // Constructor
    void setSpeed(float value); // Set the speed and direction of the motor
    void stop(); // Stop the motor

  private:
    int _pwmPin;
    int _dirPin;
};

#endif

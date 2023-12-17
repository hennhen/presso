#ifndef RoboController_H
#define RoboController_H

#include <Arduino.h>
#include "RoboClaw.h"

class RoboController {
  public:
    RoboController(HardwareSerial *roboSerial, uint32_t baudrate); // Constructor
    void setSpeed(short value); // Set the speed and direction of the motor, -127 to 127
    void stop(); // Stop the motor

  private:
    HardwareSerial *_roboSerial;
    RoboClaw _roboClaw;
    int _baudrate;
    static const uint8_t _address = 0x80; // RoboClaw address
};

#endif

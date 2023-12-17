#ifndef RoboController_H
#define RoboController_H

#include <Arduino.h>
#include "RoboClaw.h"
#include "MotorController.h"

class RoboController : public MotorController {
  public:
    RoboController(HardwareSerial *roboSerial, uint32_t baudrate); // Constructor
    void setSpeed(short value) override; // Set the speed and direction of the motor, -127 to 127
    void stop() override; // Stop the motor

  private:
    HardwareSerial *_roboSerial;
    RoboClaw _roboClaw;
    int _baudrate;
    static const uint8_t _address = 0x80; // RoboClaw address
};

#endif

#include "RoboController.h"

RoboController::RoboController(HardwareSerial *roboSerial, uint32_t baudrate)
: _roboSerial(roboSerial), _baudrate(baudrate), _roboClaw(roboSerial, 10000) {
    _roboClaw.begin(_baudrate);
}

void RoboController::setSpeed(short value) {
  if (value < -127) {
    value = -127;
  } else if (value > 127) {
    value = 127;
  }

  if (value < 0) {
    _roboClaw.BackwardM1(_address, -value);
  } else if (value > 0) {
    _roboClaw.ForwardM1(_address, value);
  } else {
    _roboClaw.ForwardM1(_address, 0);
  }
}

void RoboController::stop() {
  _roboClaw.ForwardM1(_address, 0); // Stop the motor
}

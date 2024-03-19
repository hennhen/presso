#include "RoboController.h"

RoboController::RoboController(HardwareSerial *roboSerial, long baudrate)
    : _roboSerial(roboSerial), _baudrate(baudrate), _roboClaw(roboSerial, 1) {
  // Constructor now only stores parameters
}

void RoboController::init() { _roboClaw.begin(_baudrate); }

void RoboController::setDutyCycle(short value) {
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

/*** POSITIONAL FUNCTIONS ***/
void RoboController::setPosition(long position) {
  // Mostly used to home the motor
  _roboClaw.SetEncM1(_address, position);
};

void RoboController::moveToAbsEncoderPosition(unsigned long position,
                                              unsigned int speed) {
  _roboClaw.SpeedAccelDeccelPositionM1(_address, _defaultAccel, speed,
                                       _defaultDecel, position, 1);
}

void RoboController::moveToAbsMmPosition(float positionMm, unsigned int speed) {
  uint32_t encoderPosition = positionMm * _ticksPerMm;
  moveToAbsEncoderPosition(encoderPosition);
}

void RoboController::moveRelativeMm(float distance, unsigned int speed) {
  uint32_t targetPosition =
      _roboClaw.ReadEncM1(_address) + distance * _ticksPerMm;
  _roboClaw.SpeedAccelDeccelPositionM1(_address, _defaultAccel, speed,
                                       _defaultDecel, targetPosition, 1);
}

void RoboController::homeAndZero() {
  // Start by moving down
  setDutyCycle(-126);
  // Wait for motor to start moving
  delay(1000);
  // Wait for both current and speed = 0
  float current;
  int speed;

  for (int i = 0; i < 100; ++i) {
    do {
      current = getCurrent();
      speed = getSpeed();
      Serial1.printf("Current: %.2f, Speed: %d\n", current, speed);
    } while (current > 0.01);
  }

  delay(100);
  stop();
  Serial1.println("homed in function");
  // Set encoder to 0
  setPosition(0);
}

/* GETTER FUNCTIONS*/
float RoboController::getCurrent() {
  int16_t current1, current2;
  bool result = _roboClaw.ReadCurrents(_address, current1, current2);
  if (result) {
    float current = current1 / 100.0;
    _lastCurrent = current;
    return current;
  } else {
    // Serial1.printf("Read currents failed: %d\n", current1);
    return _lastCurrent;
  }
}

int RoboController::getSpeed() {
  int speed = _roboClaw.ReadSpeedM1(_address);
  return speed;
}

long RoboController::getPosition() { return _roboClaw.ReadEncM1(_address); }

void RoboController::stop() {
  _roboClaw.ForwardM1(_address, 0); // Stop the motor
}

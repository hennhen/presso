#include "RoboController.h"

RoboController::RoboController(HardwareSerial *roboSerial, long baudrate)
    : _roboSerial(roboSerial), _baudrate(baudrate),
      _roboClaw(roboSerial, 10000) {
  // Constructor now only stores parameters
}

void RoboController::init() { _roboClaw.begin(_baudrate); }

void RoboController::stop() {
  _roboClaw.ForwardM1(_address, 0); // Stop the motor
}

/*** Speed Controls ***/
void RoboController::setDutyCycle(short value) {
  if (value < -126) {
    value = -126;
  } else if (value > 126) {
    value = 126;
  }

  if (value < 0) {
    _roboClaw.BackwardM1(_address, -value);
  } else if (value > 0) {
    _roboClaw.ForwardM1(_address, value);
  } else {
    _roboClaw.ForwardM1(_address, 0);
  }
}

void RoboController::setSpeedAccel(uint32_t speed, uint32_t accel) {
  _roboClaw.SpeedAccelM1(_address, accel, speed);
}

/*** POSITIONAL FUNCTIONS ***/
void RoboController::setPosition(long position) {
  // Mostly used to home the motor
  _roboClaw.SetEncM1(_address, position);
}

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
  bool valid;
  int32_t signedPosition =
      static_cast<int32_t>(_roboClaw.ReadEncM1(_address, nullptr, &valid));
  if (!valid) {
    Serial1.println("Error: Invalid encoder reading");
    return;
  }
  int32_t targetPosition =
      signedPosition + static_cast<int32_t>(distance * _ticksPerMm);
  Serial1.println(signedPosition);
  Serial1.println(targetPosition);
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
  stop();
  Serial1.println("homed in function");
  // Set encoder to 0
  setPosition(0);
  delay(500);
  stop();
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
  bool valid;
  int speed = _roboClaw.ReadSpeedM1(_address, nullptr, &valid);
  if (valid) {
    _lastSpeed = speed;
    // Serial1.println(speed);
    return speed;
  } else {
    Serial1.print("ReadSpeedM1 failed");
    return _lastSpeed;
  }
}

// Should only be used in non-critical.
long RoboController::getPosition() {
  bool valid;
  long position = _roboClaw.ReadEncM1(_address, nullptr, &valid);
  if (valid) {
    _lastPosition = position;
    return position;
  } else {
    return _lastPosition;
  }
}

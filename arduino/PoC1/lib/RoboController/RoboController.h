#ifndef RoboController_H
#define RoboController_H

#include "MotorController.h"
#include "RoboClaw.h"
#include <Arduino.h>

class RoboController : public MotorController {
private:
  HardwareSerial *_roboSerial;
  RoboClaw _roboClaw;
  long _baudrate;
  float _lastCurrent = 0.0;
  int _lastSpeed = 0;
  long _lastPosition = 0;
  static const uint8_t _address = 0x80; // RoboClaw address
  static const unsigned int _maxSpeed = 15000;
  static const unsigned int _ticksPerMm = 3365;
  static const uint32_t _defaultAccel = 15000;
  static const uint32_t _defaultDecel = 15000;

public:
  RoboController(HardwareSerial *roboSerial, long baudrate); // Constructor
  void init();          // Initialize the motor controller
  void stop() override; // Stop the motor

  /* Speed Controls*/
  void setDutyCycle(short value) override; // -127 to 127
  void setSpeed(short speed);              // +- 15000
  void setSpeedAccel(unsigned int speed, uint32_t accel = _defaultAccel);

  /* Positional Controls*/
  void setPosition(long position); // 0 ~ 200000 (water trasport top)
  void moveToAbsEncoderPosition(unsigned long position,
                                unsigned int speed = 15000);
  void moveToAbsMmPosition(float positionMm, unsigned int speed = 15000);
  void moveRelativeMm(float distance, unsigned int speed = 15000);
  void homeAndZero();

  /* Readings */
  float getCurrent(); // Read the current of the motor
  int getSpeed();     // Read the speed of the motor
  long getPosition();
};

#endif

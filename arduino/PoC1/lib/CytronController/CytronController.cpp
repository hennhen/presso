#include "CytronController.h"
#include <Arduino.h>

CytronController::CytronController(uint8_t pwmPin, uint8_t dirPin)
    : _pwmPin(pwmPin), _dirPin(dirPin) {
  pinMode(_pwmPin, OUTPUT);
  pinMode(_dirPin, OUTPUT);
}

bool dir = HIGH;
short pwmValue = 0;

void CytronController::setSpeed(short value) {

  pwmValue = value;

  if (value < 0) {
    dir = LOW;
  } else {
    dir = HIGH;
  }

  if (pwmValue > 255) {
    pwmValue = 255;
  }

  digitalWrite(_dirPin, dir);
  analogWrite(_pwmPin, pwmValue);
}

void CytronController::stop() {
  digitalWrite(_dirPin, HIGH);
  analogWrite(_pwmPin, 0);
}

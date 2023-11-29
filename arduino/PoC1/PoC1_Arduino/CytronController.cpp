#include "CytronController.h"
#include <Arduino.h>

CytronController::CytronController(int pwmPin, int dirPin)
: _pwmPin(pwmPin), _dirPin(dirPin) {
  pinMode(_pwmPin, OUTPUT);
  pinMode(_dirPin, OUTPUT);
}

void CytronController::setSpeed(float value) {
  int dir = HIGH;
  int pwmValue = (int)fabs(value);

  if (value < 0) {
    dir = LOW;
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

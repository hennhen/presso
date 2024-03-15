#include <Arduino.h>
#include "RoboClaw.h"

// RoboClaw configuration
#define ADR 0x80  // Default RoboClaw address
#define SERIAL_SPEED 115200
#define MOTOR_SPEED 126  // Speed range is 0-127 for 7-bit mode

// Create RoboClaw instance
RoboClaw roboclaw(&Serial2, 115200);

void setup() {
  // Initialize Serial for debug messages
  Serial.begin(SERIAL_SPEED);
  Serial.println("Starting RoboClaw Test...");

  // Initialize Serial2 for RoboClaw communication
  roboclaw.begin(SERIAL_SPEED);
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read();
    if (command == '1') {
      // Move motor forward
      Serial.println("Moving motor forward");
      roboclaw.ForwardM1(ADR, MOTOR_SPEED);
      delay(1000); // Run motor for 1 second
      roboclaw.ForwardM1(ADR, 0); // Stop motor
    } else if (command == '2') {
      // Move motor in reverse
      Serial.println("Moving motor in reverse");
      roboclaw.BackwardM1(ADR, MOTOR_SPEED);
      delay(1000); // Run motor for 1 second
      roboclaw.BackwardM1(ADR, 0); // Stop motor
    }
  }
}
#include <PacketSerial.h>
#include "PressureSensor.h"
#include "CytronController.h"
#include "PIDController.h"

#define pressurePin A0  // Define the pin for the pressure sensor
#define pwmPin 6        // PWM Pin for Motor
#define dirPin 7        // Direction Pin for Motor

#define PRESSURE_SETPOINT 4.0
#define kP 500
#define kI 5
#define kD 1

PacketSerial serial;

PressureSensor pSensor(pressurePin);
CytronController motor(pwmPin, dirPin); 
PIDController pidController(motor, pSensor);


void setup() {
  Serial.begin(9600);  // Start the serial communication
  pidController.setParameters(PRESSURE_SETPOINT, kP, kI, kD);
}

void loop() {

  Serial.println(pidController.update());  // Update the PID controller
  delay(20);               // Adjust the delay as needed
}
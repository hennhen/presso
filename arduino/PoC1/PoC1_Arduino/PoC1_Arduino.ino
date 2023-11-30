#include <PacketSerial.h>
#include "PressureSensor.h"
#include "CytronController.h"
#include "PIDController.h"

#define pressurePin A0  // Define the pin for the pressure sensor
#define pwmPin 6        // PWM Pin for Motor
#define dirPin 7        // Direction Pin for Motor

#define PRESSURE_SETPOINT 4.0
#define kP 500
#define kI 3
#define kD 0

#define COBS_FLAG 0x00
#define COMMAND_START_BYTE 0x02

enum Commands {
  SET_MOTOR_SPEED = 1,
  SET_PID_VALUES = 2,
  SET_PRESSURE = 3,
  STOP = 4
};

PacketSerial pSerial;

PressureSensor pSensor(pressurePin);
CytronController motor(pwmPin, dirPin);
PIDController pidController(motor, pSensor);

float pressure;
uint8_t outBuffer[4];  // floats are 4-bytes each in Ardiuno
const float confirm_float = 999.999;

void setup() {
  pidController.setParameters(PRESSURE_SETPOINT, kP, kI, kD);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  pSerial.begin(115200);  // Start the serial communication
  // Serial.begin(9600);
  pSerial.setPacketHandler(&onPacketReceived);
}

void loop() {
  // pressure = pSensor.readPressure();
  pSerial.update();
  // pidController.update();

  // memcpy(outBuffer, &pressure, sizeof(pressure));
  // pSerial.send(outBuffer, sizeof(outBuffer));
  delay(1);
}

void onPacketReceived(const uint8_t* buffer, size_t size) {
  if (size == sizeof(short) + sizeof(float)) {
    // // Create variables to hold the extracted data
    short command;
    float value;

    // // Extract the integer (first 4 bytes)
    memcpy(&command, buffer, sizeof(short));
    memcpy(&value, buffer + sizeof(short), sizeof(float));

    pSerial.send(reinterpret_cast<uint8_t*>(&value), sizeof(float));

    if (value == 4.7) {
      for (size_t i = 0; i < 2; ++i) {
        digitalWrite(LED_BUILTIN, HIGH);  // Turn the LED on
        delay(200);                       // Wait for 500 milliseconds
        digitalWrite(LED_BUILTIN, LOW);   // Turn the LED off
        delay(200);                       // Wait for 500 milliseconds
      }
    }
  }
}
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

#define START_BYTE 0x02

PacketSerial pSerial;

PressureSensor pSensor(pressurePin);
CytronController motor(pwmPin, dirPin); 
PIDController pidController(motor, pSensor);

float pressure;
uint8_t outBuffer[4]; // floats are 4-bytes each in Ardiuno

void setup() {
  pidController.setParameters(PRESSURE_SETPOINT, kP, kI, kD);

  pSerial.begin(9600);  // Start the serial communication
  // Serial.begin(9600);
  // pSerial.setPacketHandler(&onPacketReceived);

}

void loop() {
  pressure = pSensor.readPressure();
  pidController.update();

  memcpy(outBuffer, &pressure, sizeof(pressure));
  pSerial.send(outBuffer, sizeof(outBuffer));
  delay(20);
}

void onPacketReceived(const uint8_t* buffer, size_t size)
{
  // Make a temporary buffer.
  uint8_t tempBuffer[size];

  // Send the reversed buffer back to the sender. The send() method will encode
  // the whole buffer as as single packet, set packet markers, etc.
  // The `tempBuffer` is a pointer to the `tempBuffer` array and `size` is the
  // number of bytes to send in the `tempBuffer`.

  // myPacketSerial.send(tempBuffer, size);
}
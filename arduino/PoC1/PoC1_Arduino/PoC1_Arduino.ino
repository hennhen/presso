#include <PacketSerial.h>
#include <SoftwareSerial.h>
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
  STOP = 4,

  EXTRACTION_STOPPED = 8,
  PRESSURE_READING = 9
};

SoftwareSerial debug(11, 10);  // RX, TX
PacketSerial pSerial;


PressureSensor pSensor(pressurePin);
CytronController motor(pwmPin, dirPin);
PIDController pidController(motor, pSensor);

// PID Extraction Loop Parameters
bool isPIDRunning = false;
unsigned long pidStartTime = 0;
const unsigned long pidRunDuration = 4000; // PID Loop timeout

//
float pressure;
uint8_t outBuffer[sizeof(short) + sizeof(float)];

void setup() {
  motor.stop();

  pSerial.begin(115200);

  debug.begin(4800);
  debug.println("debug print test...");

  pSerial.setPacketHandler(&onPacketReceived);
}

void loop() {
  pSerial.update();
  pressure = pSensor.readPressure();

  if (isPIDRunning) {
    // Check if 5 seconds have passed or a stop command was received
    if (millis() - pidStartTime > pidRunDuration) {
      isPIDRunning = false;
      motor.stop();  // Stop the motor after 5 seconds
      sendExtractionStopped();
      debug.println("Extraction duration reached");
    } else {
      // BUFFER SEEMS TO OVER FLOW IF I PRINT THIS AS WELL. IF delay 30 ms it works
      // Can't be doing this in actual. 
      // debug.println("extracting...");
      pidController.update();
      sendPressureReading();
    }
  }
  // debug.println(pressure);
  delay(30);
}

void onPacketReceived(const uint8_t* buffer, size_t size) {
  // Ensure the buffer has at least the size of a short (for the command)
  if (size < sizeof(short)) {
    debug.print("Not enough data to read a command. Size: ");
    debug.println(size);
    debug.print("Data: ");

    if (size > 0) {
          // Print the single byte in hexadecimal format
          debug.print("0x");
          debug.println(buffer[0], HEX);  // Print the first byte in HEX
      }
    return;
  }

  // Extract the command
  short command;
  memcpy(&command, buffer, sizeof(short));
  debug.print("Received Command: ");
  debug.println(command);

  // Switch on the command
  switch (command) {
    case STOP:
      {
        motor.stop();
        isPIDRunning = false; // Stop PID control
        sendExtractionStopped();
        debug.println("Stopped");
        break;
      }
    case SET_MOTOR_SPEED:
      {
        // Check if the size is correct (command + 1 float)
        if (size == sizeof(short) + sizeof(float)) {
          float speed;
          memcpy(&speed, buffer + sizeof(short), sizeof(float));
          motor.setSpeed(speed);  // Assuming a method to set motor speed
          debug.println("Motor speed set:");
          debug.print("Speed: ");
          debug.println(speed);
        } else {
          debug.println("Invalid Set Motor Speed Command");
        }
        break;
      }

    case SET_PID_VALUES:
      {
        // Check if the size is correct (command + 4 floats)
        if (size == sizeof(short) + 4 * sizeof(float)) {
          // Create variables to hold the PID values
          float p, i, d, setpoint;

          // Extract the PID values
          memcpy(&p, buffer + sizeof(short), sizeof(float));
          memcpy(&i, buffer + sizeof(short) + sizeof(float), sizeof(float));
          memcpy(&d, buffer + sizeof(short) + 2 * sizeof(float), sizeof(float));
          memcpy(&setpoint, buffer + sizeof(short) + 3 * sizeof(float), sizeof(float));


          pidController.setParameters(setpoint, p, i, d);
          {  // Debug Prints
            debug.println("PID values set:");
            debug.print("Setpoint: ");
            debug.println(setpoint);
            debug.print("P: ");
            debug.println(p);
            debug.print("I: ");
            debug.println(i);
            debug.print("D: ");
            debug.println(d);
          }
          
          // Start PID control
          debug.println("extracting & sending pressure...");
          isPIDRunning = true;
          pidStartTime = millis();  // Record the start time
          break;

        } else {
          debug.println("Invalid PID Command");
        }
        break;
      }
      // Handle other cases here
      // ...
  }
  debug.println();
}

void sendExtractionStopped() {
    short command = EXTRACTION_STOPPED;
    uint8_t buffer[sizeof(short)];
    memcpy(buffer, &command, sizeof(command));
    pSerial.send(buffer, sizeof(buffer));
    debug.print("Sending Extraction Stopped. Sent bytes: ");
    debug.println(sizeof(buffer));
}

void sendPressureReading() {
    short command = PRESSURE_READING;
    uint8_t buffer[sizeof(short) + sizeof(float)];
    memcpy(buffer, &command, sizeof(command));
    memcpy(buffer + sizeof(command), &pressure, sizeof(pressure));
    pSerial.send(buffer, sizeof(buffer));
    // debug.print("Sending Pressure. Sent bytes: ");
    // debug.println(sizeof(buffer));
}

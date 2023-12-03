#include <PacketSerial.h>
#include <SoftwareSerial.h>
#include "PressureSensor.h"
#include "CytronController.h"
#include "PIDController.h"
#include "HX711_Scale.h"

#define DEBUG  // Comment out this line if you don't want debug prints

#ifdef DEBUG
  #define DEBUG_PRINT(x)  Serial1.println(x)
#else
  #define DEBUG_PRINT(x)
#endif

#define pressurePin A0  // Define the pin for the pressure sensor
#define pwmPin 6        // PWM Pin for Motor
#define dirPin 7        // Direction Pin for Motor
#define LOADCELL_DOUT_PIN 30
#define LOADCELL_SCK_PIN 31

#define LOADCELL_CALIBRATION_FACTOR 1036.1112060547

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

  WEIGHT_READING = 7,
  EXTRACTION_STOPPED = 8,
  PRESSURE_READING = 9
};

PacketSerial pSerial;

PressureSensor pSensor(pressurePin);
CytronController motor(pwmPin, dirPin);
PIDController pidController(motor, pSensor);
HX711_Scale scale(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN, LOADCELL_CALIBRATION_FACTOR);

// PID Extraction Loop Parameters
bool isPIDRunning = false;
unsigned long pidStartTime = 0;
const unsigned long pidRunDuration = 3000; // PID Loop timeout

//
float pressure;
float weight;
bool includeWeight = false; 

float targetWeight = 0.0; // Target weight for termination condition
uint8_t outBuffer[sizeof(short) + sizeof(float)];

void setup() {
  motor.stop();

  pSerial.begin(115200);

  
  #ifdef DEBUG
    Serial1.begin(115200);
    DEBUG_PRINT("debug print test...");
  #endif

  pSerial.setPacketHandler(&onPacketReceived);
}

void loop() {

  pSerial.update();
  pressure = pSensor.readPressure();
  DEBUG_PRINT("pressure: " + String(pressure));

  // loopStartTime = millis();
  if (includeWeight) {
    scale.updateWeight();
  }
  // duration = millis() - loopStartTime;

  // DEBUG_PRINT("update weight time: " + String(duration) + " ms");

  if (isPIDRunning) {
    // Check if 5 seconds have passed or target weight reached
    // If target weight is 0, then it is not used as a termination condition

    if ((targetWeight != 0 && scale.weight >= targetWeight) || (targetWeight == 0 && millis() - pidStartTime > pidRunDuration)) {
      isPIDRunning = false;
      motor.stop();  // Stop the motor after 5 seconds or target weight reached
      sendExtractionStopped();
      DEBUG_PRINT("Extraction duration reached or target weight reached");
    } else {

      pidController.update();

      sendPressureReading();

      if (includeWeight) {
        sendWeightReading();  // Only send weight reading if includeWeight is true
      }
    }
  }
  if(!includeWeight) {
    delay(30);
  }
}

void onPacketReceived(const uint8_t* buffer, size_t size) {
  // Ensure the buffer has at least the size of a short (for the command)
  if (size < sizeof(short)) {
    DEBUG_PRINT("Not enough data to read a command. Size: ");
    DEBUG_PRINT(size);
    DEBUG_PRINT("Data: ");

    if (size > 0) {
          // Print the single byte in hexadecimal format
          DEBUG_PRINT("0x");
          DEBUG_PRINT(buffer[0]);  // Print the first byte in HEX
      }
    return;
  }

  // Extract the command
  short command;
  memcpy(&command, buffer, sizeof(short));
  DEBUG_PRINT("Received Command: ");
  DEBUG_PRINT(command);

  // Switch on the command
  switch (command) {
    case STOP:
      {
        motor.stop();
        isPIDRunning = false; // Stop PID control
        sendExtractionStopped();
        DEBUG_PRINT("Stopped");
        break;
      }
    case SET_MOTOR_SPEED:
      {
        // Check if the size is correct (command + 1 float)
        if (size == sizeof(short) + sizeof(float)) {
          float speed;
          memcpy(&speed, buffer + sizeof(short), sizeof(float));
          motor.setSpeed(speed);  // Assuming a method to set motor speed
          DEBUG_PRINT("Motor speed set:");
          DEBUG_PRINT("Speed: ");
          DEBUG_PRINT(speed);
        } else {
          DEBUG_PRINT("Invalid Set Motor Speed Command");
        }
        break;
      }

    case SET_PID_VALUES:
      {
        // Check if the size is correct (command + 5 floats)
        if (size == sizeof(short) + 5 * sizeof(float)) {
          // Create variables to hold the PID values
          float p, i, d, setpoint, weight;

          // Extract the PID values
          memcpy(&p, buffer + sizeof(short), sizeof(float));
          memcpy(&i, buffer + sizeof(short) + sizeof(float), sizeof(float));
          memcpy(&d, buffer + sizeof(short) + 2 * sizeof(float), sizeof(float));
          memcpy(&setpoint, buffer + sizeof(short) + 3 * sizeof(float), sizeof(float));
          memcpy(&weight, buffer + sizeof(short) + 4 * sizeof(float), sizeof(float));

          pidController.setParameters(setpoint, p, i, d);
          targetWeight = weight; // Set the target weight for termination condition

          if(targetWeight != 0) {
            includeWeight = true;
          }

          {  // Debug Prints
            DEBUG_PRINT("PID values set:");
            DEBUG_PRINT("Setpoint: ");
            DEBUG_PRINT(setpoint);
            DEBUG_PRINT("P: ");
            DEBUG_PRINT(p);
            DEBUG_PRINT("I: ");
            DEBUG_PRINT(i);
            DEBUG_PRINT("D: ");
            DEBUG_PRINT(d);
            DEBUG_PRINT("Target Weight: ");
            DEBUG_PRINT(weight);
          }
          
          // Start PID control
          DEBUG_PRINT("extracting & sending pressure...");
          isPIDRunning = true;
          pidStartTime = millis();  // Record the start time
          break;

        } else {
          DEBUG_PRINT("Invalid PID Command");
        }
        break;
      }
      // Handle other cases here
      // ...
  }
  // DEBUG_PRINT();
}

void sendExtractionStopped() {
    short command = EXTRACTION_STOPPED;
    uint8_t buffer[sizeof(short)];
    memcpy(buffer, &command, sizeof(command));
    pSerial.send(buffer, sizeof(buffer));
    DEBUG_PRINT("Sending Extraction Stopped. Sent bytes: ");
    DEBUG_PRINT(sizeof(buffer));
}

void sendPressureReading() {
    short command = PRESSURE_READING;
    uint8_t buffer[sizeof(short) + sizeof(float)];
    memcpy(buffer, &command, sizeof(command));
    memcpy(buffer + sizeof(command), &pressure, sizeof(pressure));
    pSerial.send(buffer, sizeof(buffer));
    // DEBUG_PRINT("Sending Pressure. Sent bytes: ");
    // DEBUG_PRINT(sizeof(buffer));
}

void sendWeightReading() {
  short command = WEIGHT_READING;
  uint8_t buffer[sizeof(short) + sizeof(float)];
  memcpy(buffer, &command, sizeof(command));
  memcpy(buffer + sizeof(command), &scale.weight, sizeof(weight));
  pSerial.send(buffer, sizeof(buffer));
}
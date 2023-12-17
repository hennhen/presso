#include "CytronController.h"
#include "ExtractionProfile.h"
#include "HX711_Scale.h"
#include "PIDController.h"
#include "PressureSensor.h"
#include <PacketSerial.h>
#include <SoftwareSerial.h>
#include "RoboController.h"

#define DEBUG // Comment out this line if you don't want debug prints

#ifdef DEBUG
#define DEBUG_PRINT(x) Serial1.println(x)
#else
#define DEBUG_PRINT(x)
#endif

#define pressurePin A0 // Define the pin for the pressure sensor
#define pwmPin 6       // PWM Pin for Motor
#define dirPin 7       // Direction Pin for Motor
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

  DUTY_CYCLE = 5,
  TARGET_PRESSURE = 6,
  WEIGHT_READING = 7,
  EXTRACTION_STOPPED = 8,
  PRESSURE_READING = 9
};

PacketSerial pSerial;

PressureSensor pSensor(pressurePin);
// CytronController motor(pwmPin, dirPin);
RoboController motor(&Serial2, 115200);
PIDController pidController(motor, pSensor);
HX711_Scale scale(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN,
                  LOADCELL_CALIBRATION_FACTOR);

// PID Extraction Loop Parameters
bool isExtracting = false;
unsigned long extractionStartTime = 0;
const unsigned long extractionDuration = 4000; // PID Loop timeout

// Function to send a command with a floating point value
void sendFloat(short command, float value = 0.0) {
  uint8_t buffer[sizeof(short) + sizeof(float)];
  memcpy(buffer, &command, sizeof(short));
  memcpy(buffer + sizeof(short), &value, sizeof(float));
  pSerial.send(buffer, sizeof(buffer));
  // DEBUG_PRINT("Sent Command: ");
  // DEBUG_PRINT(command);
  // DEBUG_PRINT("Value: ");
  // DEBUG_PRINT(value);
}

//


ExtractionProfile extractionProfile = ExtractionProfile(SINE_WAVE, extractionDuration); 
// ExtractionProfile extractionProfile = ExtractionProfile(RAMPING, extractionDuration);
// ExtractionProfile extractionProfile = ExtractionProfile(STATIC, extractionDuration);

void setup() {
  motor.init();
  motor.stop();
  pSerial.begin(115200);
  pSerial.setPacketHandler(&onPacketReceived);

#ifdef DEBUG
  Serial1.begin(115200);
  DEBUG_PRINT("debug print test...");
#endif

  extractionProfile.setSineParameters(1.0, 0.4, 8.0);
  // extractionProfile.setRampingParameters(9.0, 2000, 2000);
  // extractionProfile.setStaticPressure(8.0);
}

unsigned long lastSendTime = 0;
const unsigned long sendInterval = 5; // Send data every 15 ms

float currPressure;
float currDutyCycle;
float weight;
bool includeWeight = false;

float targetWeight = 0.0; // Target weight for termination condition
uint8_t outBuffer[sizeof(short) + sizeof(float)];

void loop() {
  pSerial.update();
  currPressure = pSensor.readPressure();

  // If extracting, update the PID controller
  if (isExtracting) {
    if (includeWeight) {
      scale.updateWeight();
    }

    // Check if the extraction duration has been reached in the target profile
    if (!extractionProfile.isFinished()) {
      // Extracting. Get the target pressure from the profile
      float currTarget = extractionProfile.getTarget(millis());

      // Update the PID controller with current target pressure
      currDutyCycle = pidController.updateDynamic(currTarget);

      // Serial1.println(targetPressure);

      // Send the current target pressure and current pressure
      if (millis() - lastSendTime >= sendInterval) {
        lastSendTime = millis();
        sendFloat(DUTY_CYCLE, currDutyCycle);
        sendFloat(TARGET_PRESSURE, currTarget);
        sendFloat(PRESSURE_READING, currPressure);
        // DEBUG_PRINT(currDutyCycle);
        // if (includeWeight) {
        //   sendFloat(WEIGHT_READING, scale.getWeight());
        // }
      }
    } else {
      // Extraction finished. Stop the motor and PID control
      motor.stop();

      // Notify extraction stopped
      sendFloat(EXTRACTION_STOPPED);
      DEBUG_PRINT("Extraction duration reached or target weight reached");
      isExtracting = false;
    }
  }

  delay(20);
}

void onPacketReceived(const uint8_t *buffer, size_t size) {
  // Ensure the buffer has at least the size of a short (for the command)
  if (size < sizeof(short)) {
    DEBUG_PRINT("Not enough data to read a command. Size: ");
    DEBUG_PRINT(size);
    DEBUG_PRINT("Data: ");

    if (size > 0) {
      // Print the single byte in hexadecimal format
      DEBUG_PRINT("0x");
      DEBUG_PRINT(buffer[0]); // Print the first byte in HEX
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
  case STOP: {
    motor.stop();
    isExtracting = false; // Stop PID control
    sendFloat(EXTRACTION_STOPPED);
    DEBUG_PRINT("Stopped");
    break;
  }
  case SET_MOTOR_SPEED: {
    // Check if the size is correct (command + 1 float)
    if (size == sizeof(short) + sizeof(float)) {
      float speed;
      memcpy(&speed, buffer + sizeof(short), sizeof(float));
      short shortSpeed = (short)round(speed);
      DEBUG_PRINT("Speed Short:");
      DEBUG_PRINT(shortSpeed);
      motor.setSpeed(speed);

      DEBUG_PRINT("Motor speed set:");
      DEBUG_PRINT("Speed: ");
      DEBUG_PRINT(speed);
    } else {
      DEBUG_PRINT("Invalid Set Motor Speed Command");
    }
    break;
  }

  case SET_PID_VALUES: {
    // Check if the size is correct (command + 5 floats)
    if (size == sizeof(short) + 5 * sizeof(float)) {
      // Create variables to hold the PID values
      float p, i, d, setpoint, weight;

      // Extract the PID values
      memcpy(&p, buffer + sizeof(short), sizeof(float));
      memcpy(&i, buffer + sizeof(short) + sizeof(float), sizeof(float));
      memcpy(&d, buffer + sizeof(short) + 2 * sizeof(float), sizeof(float));
      memcpy(&setpoint, buffer + sizeof(short) + 3 * sizeof(float),
             sizeof(float));
      memcpy(&weight, buffer + sizeof(short) + 4 * sizeof(float),
             sizeof(float));

      if (targetWeight != 0) {
        includeWeight = true;
      }

      { // Debug Prints
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
      DEBUG_PRINT("Starting extraction...");
      pidController.setParameters(setpoint, p, i, d);
      extractionProfile.start(millis());
      isExtracting = true;

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
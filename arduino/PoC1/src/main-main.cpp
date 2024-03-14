#include "CytronController.h"
#include "ExtractionProfile.h"
#include "HX711_Scale.h"
#include "NAU7802.h"
#include "PIDController.h"
#include "PressureSensor.h"
#include "RoboController.h"
#include <PacketSerial.h>
#include <SoftwareSerial.h>
#include <StandardCplusplus.h>
#include <vector>

#define DEBUG // Comment out this line if you don't want debug prints

#ifdef DEBUG
#define DEBUG_PRINT(x) Serial1.println(x)
#else
#define DEBUG_PRINT(x)
#endif

#define pressurePin A15 // Define the pin for the pressure sensor
#define pwmPin 6        // PWM Pin for Motor
#define dirPin 7        // Direction Pin for Motor
#define LOADCELL_DOUT_PIN 20
#define LOADCELL_SCK_PIN 21

#define LOADCELL_CALIBRATION_FACTOR -1036.1112060547
#define NAU7802_CALIBRATION_FACTOR 1030.71337

#define PRESSURE_SETPOINT 4.0
#define kP 500
#define kI 3
#define kD 0

#define COBS_FLAG 0x00
#define COMMAND_START_BYTE 0x02

PacketSerial pSerial;

PressureSensor pSensor(pressurePin);
// CytronController motor(pwmPin, dirPin);
RoboController motor(&Serial2, 115200);
PIDController pidController(motor, pSensor);

// HX711_Scale scale(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN,
// LOADCELL_CALIBRATION_FACTOR);
NAU7802 scale(NAU7802_CALIBRATION_FACTOR);

// PID Extraction Loop Parameters
bool isExtracting = false;
unsigned long extractionStartTime = 0;
const unsigned long extractionDuration = 3000; // PID Loop timeout

/* Placeholder profile. Will be replaced later */
ExtractionProfile extractionProfile =
    ExtractionProfile(SINE_WAVE, extractionDuration);
// ExtractionProfile extractionProfile = ExtractionProfile(RAMPING,
// extractionDuration); ExtractionProfile extractionProfile =
// ExtractionProfile(STATIC, extractionDuration);

bool includeWeight = true;

unsigned long lastSendTime = 0;
const unsigned long sendInterval = 20; // Send data every XXX ms

float currPressure;
float currDutyCycle;
float targetWeight = 0.0; // Target weight for termination condition

void sendFloat(short command, float value = 0.0) {
  /*
  All communications to the host computer starts with
  - a short (2 bytes number) command
  - followed by a float (4 bytes) value
*/
  uint8_t buffer[sizeof(short) + sizeof(float)];
  memcpy(buffer, &command, sizeof(short));
  memcpy(buffer + sizeof(short), &value, sizeof(float));
  pSerial.send(buffer, sizeof(buffer));
  // DEBUG_PRINT("Sent Command: ");
  // DEBUG_PRINT(command);
  // DEBUG_PRINT("Value: ");
  // DEBUG_PRINT(value);
}

enum Commands {
  /*
  Commands enumumeration
  Used to identify the command sent from the host computer
  Must match the commands in the host computer code
 */
  /* Incoming */
  SET_MOTOR_SPEED = 1,
  SET_PID_VALUES = 2,
  SET_PRESSURE = 3,
  STOP = 4,

  /* Outgoing */
  DUTY_CYCLE = 5,
  TARGET_PRESSURE = 6,
  WEIGHT_READING = 7,
  EXTRACTION_STOPPED = 8,
  PRESSURE_READING = 9,
  PROFILE_SELECTION = 10,
  SINE_PROFILE = 11,
  STATIC_PROFILE = 12,
};

void onPacketReceived(const uint8_t *buffer, size_t size) {
  /*
  Receives commands from host computer
  Always starts with a (short) command.
  Switch on the command and receive case dependent values
*/

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
        DEBUG_PRINT("P: ");
        DEBUG_PRINT(p);
        DEBUG_PRINT("I: ");
        DEBUG_PRINT(i);
        DEBUG_PRINT("D: ");
        DEBUG_PRINT(d);
      }

      // Start PID control
      DEBUG_PRINT("Starting extraction...");
      scale.tare();
      pidController.setParameters(setpoint, p, i, d);
      extractionProfile.start(millis());
      isExtracting = true;

      break;
    } else {
      DEBUG_PRINT("Invalid PID Command");
    }
    break;
  }

  case PROFILE_SELECTION: {
    // Check if the size is correct (command + 1 short)
    if (size >= sizeof(short)) {
      short profileType;
      memcpy(&profileType, buffer + sizeof(short), sizeof(short));
      DEBUG_PRINT(profileType);
      // Determine the profile type and set the global profile object
      // accordingly
      switch (profileType) {
      case SINE_PROFILE: {
        // Create and set a Sine Wave profile
        // Extract the profile parameters
        float amplitude, frequency, offset;
        short duration;

        // buffer starts with command short, type short, 3 floats, 1 short
        memcpy(&amplitude, buffer + 2 * sizeof(short), sizeof(float));
        memcpy(&frequency, buffer + 2 * sizeof(short) + sizeof(float),
               sizeof(float));
        memcpy(&offset, buffer + 2 * sizeof(short) + 2 * sizeof(float),
               sizeof(float));
        memcpy(&duration, buffer + 2 * sizeof(short) + 3 * sizeof(float),
               sizeof(short));

        DEBUG_PRINT("Sine parameters set:");
        DEBUG_PRINT("Amplitude: ");
        DEBUG_PRINT(amplitude);
        DEBUG_PRINT("Frequency: ");
        DEBUG_PRINT(frequency);
        DEBUG_PRINT("Offset: ");
        DEBUG_PRINT(offset);
        DEBUG_PRINT("Duration: ");
        DEBUG_PRINT(duration);

        extractionProfile = ExtractionProfile(
            SINE_WAVE, duration); // Replace with your profile class
        extractionProfile.setSineParameters(amplitude, frequency,
                                            offset); // Set profile parameters
        break;
      }
        // case RAMPING:
        //   // Create and set a Ramping profile
        //   extractionProfile = MyProfile(); // Replace with your profile class
        //   extractionProfile.setRampingParameters(9.0, 2000, 2000); // Set
        //   profile parameters break;

      case STATIC_PROFILE: {
        // Create and set a Static profile
        float pressure;
        short duration;

        // buffer starts with command short, type short, 1 float, 1 short
        memcpy(&pressure, buffer + 2 * sizeof(short), sizeof(float));
        memcpy(&duration, buffer + 2 * sizeof(short) + sizeof(float),
               sizeof(short));
        DEBUG_PRINT("Static parameters set:");
        DEBUG_PRINT("Pressure: ");
        DEBUG_PRINT(pressure);
        DEBUG_PRINT("Duration: ");
        DEBUG_PRINT(duration);

        extractionProfile = ExtractionProfile(
            STATIC, duration); // Replace with your profile class
        extractionProfile.setStaticPressure(pressure); // Set profile parameters
        break;
      }

        // Add cases for other profile types as needed

      default:
        DEBUG_PRINT("Invalid Profile Type");
        break;
      }
    }
  }
  }
}

void setup() {
#ifdef DEBUG
  Serial1.begin(250000);
  DEBUG_PRINT("debug print test...");
#endif
  motor.init();
  motor.stop();
  pSerial.begin(250000);
  pSerial.setPacketHandler(&onPacketReceived);

  if (includeWeight) {
    scale.init();
  }

  /*
    Manual Extraction Profiles Setup
    Only inlude the profile that you want to run
  */
  // extractionProfile.setSineParameters(1.0, 0.4, 8.0);
  // extractionProfile.setRampingParameters(9.0, 2000, 2000);
  // extractionProfile.setStaticPressure(8.0);
}

long main_loop_start_time = 0;

void loop() {
  // main_loop_start_time = millis();
  pSerial.update();
  currPressure = pSensor.readPressure();
  // DEBUG_PRINT("hi");
  // DEBUG_PRINT(scale.read());

  /*  If we're extracting, do the necessary checks
     This is to prevent spamming the serial port with data when not extracting
   */
  if (isExtracting) {
    /* Check if the extraction duration has been reached in the target profile
     */
    if (!extractionProfile.isFinished()) {
      /* Extracting. Get the target pressure from the profile */
      float currTarget = extractionProfile.getTarget(millis());

      /* Update the PID controller with current target pressure */
      currDutyCycle = pidController.updateDynamic(currTarget);

      /* Retarded send time */
      if (millis() - lastSendTime >= sendInterval) {
        lastSendTime = millis();
        sendFloat(DUTY_CYCLE, currDutyCycle);
        sendFloat(TARGET_PRESSURE, currTarget);
        sendFloat(PRESSURE_READING, currPressure);
        // sendFloat(WEIGHT_READING, scale.weight);

        // DEBUG_PRINT(currDutyCycle);
        if (includeWeight) {
          sendFloat(WEIGHT_READING, scale.read());
        }
      }

      /* Create and add the packets to queue */
      // Instead of sending directly, enqueue data
      // enqueueData(DUTY_CYCLE, currDutyCycle);
      // enqueueData(TARGET_PRESSURE, currTarget);
      // enqueueData(PRESSURE_READING, currPressure);
      // enqueueData(WEIGHT_READING, scale.weight);

    } else {
      /* Extraction finished. Stop the motor and PID control */
      motor.stop();

      // Notify extraction stopped
      DEBUG_PRINT("Extraction duration reached & queued send stopped");
      sendFloat(EXTRACTION_STOPPED);
      isExtracting = false;

      // queue stop command
      // enqueueData(EXTRACTION_STOPPED, 0.0);
    }
  }

  // Send data from buffer at intervals
  // if (millis() - lastSendTime >= sendInterval && !isBufferEmpty()) {
  //   dequeueData(); // This will send and remove data from buffer
  //   lastSendTime = millis();
  // }

  delay(10);
  // DEBUG_PRINT(millis() - main_loop_start_time);
}
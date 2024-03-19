#include <Arduino.h>
#include <PacketSerial.h>

#define DEBUG  // Comment out this line if you don't want debug prints

#ifdef DEBUG
#define DEBUG_PRINT(x) Serial1.println(x)
#else
#define DEBUG_PRINT(x)
#endif


// ***** COMMAND TEMPLATES *****
enum Commands {
  SET_MOTOR_SPEED = 1,
  SET_PID_VALUES = 2,
  SET_PRESSURE = 3,
  STOP = 4,

  TARGET_PRESSURE = 6,
  WEIGHT_READING = 7,
  EXTRACTION_STOPPED = 8,
  PRESSURE_READING = 9
};

// ***** GLOBAL VARIABLES *****
float curr_pressure;
float curr_weight;
float curr_target_pressure;
bool includeWeight = false;
float targetWeight = 0.0;  // Target weight for termination condition

// ***** TIMING STUFF *****
unsigned long extractionStartTime = 0;
const unsigned long extraction_timeout = 6000;  // PID Loop timeout in ms

// ***** FLAGS *****
bool extracting = false;

// ***** FUNCTIONS *****
// ** Constructor **
SerialController::SerialController(PacketSerial& packetSerial)
  : perial(packetSerial), _motor(motor), _sensor(sensor), _scale(scale), _pidController(pidController) {
  _serial.setPacketHandler(&onPacketReceived);
#ifdef DEBUG
  Serial1.begin(115200);
  DEBUG_PRINT("debug print test...");
#endif
}

void SerialController::onPacketReceived(const uint8_t* buffer, size_t size) {
  // Ensure the buffer has at least the size of a short (for the command)
  if (size < sizeof(short)) {
    // Not enough data to read a command
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
        // Stop the motor & everything
        _motor.stop();
        isPIDRunning = false;  // Stop PID control
        sendExtractionStopped();

        DEBUG_PRINT("Stopped");
        break;
      }
    case SET_MOTOR_SPEED:
      {
        if (size == sizeof(short) + sizeof(float)) {
          // Check if the size is correct (command + 1 float)
          float speed;
          memcpy(&speed, buffer + sizeof(short), sizeof(float));
          motor.setDutyCycle(speed);  // Assuming a method to set motor speed

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
        if (size == sizeof(short) + 5 * sizeof(float)) {
          // Create variables to hold the PID values
          float p, i, d, pressure_setpoint, weight

                                              // Extract the PID values
                                              memcpy(&p, buffer + sizeof(short), sizeof(float));
          memcpy(&i, buffer + sizeof(short) + sizeof(float), sizeof(float));
          memcpy(&d, buffer + sizeof(short) + 2 * sizeof(float), sizeof(float));
          memcpy(&pressure_setpoint, buffer + sizeof(short) + 3 * sizeof(float), sizeof(float));
          memcpy(&weight, buffer + sizeof(short) + 4 * sizeof(float), sizeof(float));

          pidController.setParameters(setpoint, p, i, d);
          targetWeight = weight;  // Set the target weight for termination condition
          targetPressure = pressure_setpoint;

          if (targetWeight != 0) {
            includeWeight = true;
          }

          // Start PID control
          DEBUG_PRINT("extracting & sending pressure...");
          isPIDRunning = true;
          extractionStartTime = millis();  // Record the start time
          rampStartTime = millis();        // Initialize the start time

          DEBUG_PRINT("PID values set:");
          DEBUG_PRINT("Setpoint: ");
          DEBUG_PRINT(pressure_setpoint);
          DEBUG_PRINT("P: ");
          DEBUG_PRINT(p);
          DEBUG_PRINT("I: ");
          DEBUG_PRINT(i);
          DEBUG_PRINT("D: ");
          DEBUG_PRINT(d);
          DEBUG_PRINT("Target Weight: ");
          DEBUG_PRINT(weight);

          break;
        } else {
          DEBUG_PRINT("Invalid PID Command");
        }
        break;
      }
  }
}

void SerialController::sendExtractionStopped() {
  short command = EXTRACTION_STOPPED;
  uint8_t buffer[sizeof(short)];
  memcpy(buffer, &command, sizeof(command));
  pSerial.send(buffer, sizeof(buffer));
  DEBUG_PRINT("Sending Extraction Stopped...");
}

void SerialController::sendPressureReading() {
  short command = PRESSURE_READING;
  uint8_t buffer[sizeof(short) + sizeof(float)];
  memcpy(buffer, &command, sizeof(command));
  memcpy(buffer + sizeof(command), &pressure, sizeof(pressure));
  pSerial.send(buffer, sizeof(buffer));
}

void sSerialController::sendTargetPressure(float tpressure) {
  short command = TARGET_PRESSURE;
  uint8_t buffer[sizeof(short) + sizeof(float)];
  memcpy(buffer, &command, sizeof(command));
  memcpy(buffer + sizeof(command), &tpressure, sizeof(tpressure));
  pSerial.send(buffer, sizeof(buffer));
}

void SerialController::sendWeightReading() {
  short command = WEIGHT_READING;
  uint8_t buffer[sizeof(short) + sizeof(float)];
  memcpy(buffer, &command, sizeof(command));
  memcpy(buffer + sizeof(command), &scale.weight, sizeof(weight));
  pSerial.send(buffer, sizeof(buffer));
}


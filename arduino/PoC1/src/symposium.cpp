#include "StructsEnums.h"
#include <Arduino.h>
#include <NAU7802.h>
#include <PacketSerial.h>
#include <SerialCommunicator.h>

#include <ExtractionProfile.h>
#include <HeaterController.h>
#include <PIDController.h>
#include <RoboController.h>

#pragma region "DECLARATIONS"
/***** Hardware Objects *****/
// Scale
#define NAU7802_CALIBRATION_FACTOR 1030.71337
NAU7802 scale(NAU7802_CALIBRATION_FACTOR);
// Pressure Sensor
ADSPressureSensor pSensor;
RoboController motor(&Serial2, 230400);
// TC and Heater
const uint8_t ONE_WIRE_BUS = 4;
const uint8_t HEATER_PIN = 12;
HeaterController heaterController(ONE_WIRE_BUS, HEATER_PIN);

/***** Software Objects *****/
PIDController pidController(motor, pSensor);
ExtractionProfile extProfile(NO_PROFILE, 0);

PacketSerial pSerial;
SerialCommunicator serialComm(pSerial, pidController, extProfile, motor,
                              heaterController);

Datas datas;
Flags flags;

/*
struct Flags {
  bool inExtraction;
  bool partialExtraction; // Extraction without preheat or retraction
  bool inPID;
  bool isHeating;
  bool tareRequested;
};
*/

void onPacketReceived(const uint8_t *buffer, size_t size);
void pollData();
void streamData();
bool extractionShouldStop();
void executeStop();
void homeAndZero();

#pragma endregion

void setup() {
  Wire.begin();
  Serial1.begin(250000, SERIAL_8N1, 9, 10);
  Serial1.println("DEBUG TEST PRINT");
  pSerial.begin(250000);
  pSerial.setPacketHandler(&onPacketReceived);

  serialComm.setSendFrequency(50);

  /* Init hardware objects */
  if (!pSensor.init()) {
  };

  motor.init();
  motor.stop();

  scale.init();
  scale.tare();

  // flags.isHeating = true;
  heaterController.setTarget(50);

  /*** TEMP TESTING ***/
  // Serial1.println("homing...");
  // motor.homeAndZero();
  // Serial1.println("homed");
  // delay(1000);
  // motor.moveRelativeMm(60);
}

unsigned long loopStartTime;

void loop() {
  loopStartTime = millis();

  pSerial.update();
  pollData();

  /* Control Heater if Necessary */
  if (flags.isHeating) {
    heaterController.update();
    datas.temperature = heaterController.read();
  }

  /** Homing Sequence
   * BLOCKING!! But will still poll and receive data
   */
  if (flags.homing) {
    Serial1.println("Homing Requested...");
    homeAndZero();
  }

  if (flags.inExtraction) {
    /* Can have partial or full extraction */
    if (flags.partialExtraction) {
      /* Partial extraction logic. No heating/retraction. Directly Start PID */

      // Check for termination conditions
      loopStartTime = millis();
      bool shouldStop = extractionShouldStop();
      if (shouldStop) {
        executeStop();
      }
      if (flags.inPID) {
        // PID control logic
        datas.target = extProfile.getTarget(millis());
        datas.dutyCycle = pidController.updateDynamic(datas.target);
      }
    } else {
      // Full extraction logic. Retract and shit
    }
  }
  streamData();

  /* Debug Prints */
  //   Serial1.printf("Pressure: %f bars\n", datas.pressure);
  //   Serial1.printf("Weight: %f grams\n", datas.weight);

  /* Loop time printing */
  // unsigned long loopEndTime = millis();
  // Serial1.printf("%lu ms\n", loopEndTime - loopStartTime);
}

void onPacketReceived(const uint8_t *buffer, size_t size) {
  // Serial1.println("receiced");
  uint8_t result = serialComm.receiveCommands(buffer, size);
  switch (result) {
  case 0:
    // Fail
    Serial1.println("Something failed when receiving commands");
    break;
  case 1:
    // success, nothing to do
    break;
  case 2:
    // Partial Extraction. No heating.
    if (pidController.isReady() && extProfile.isReady()) {
      flags.inExtraction = true;
      flags.partialExtraction = true;
      flags.inPID = true;
      flags.isHeating = false;
      datas.extractionStartTime = millis();
      extProfile.start(datas.extractionStartTime);
      serialComm.notifyExtractionStarted();
      break;
    }
  case 3:
    // Generic Stop Command Received from computer
    executeStop();
    break;
  case 4: {
    // Tare
    scale.tare();
    delay(100);
    break;
  }
  case 5: {
    // Heater off
    heaterController.setTarget(0);
    digitalWrite(HEATER_PIN, LOW);
    flags.isHeating = false;
    break;
  }
  case 6: {
    // Heater on
    flags.isHeating = true;
    break;
  }
  case 7: {
    // Do Homing Sequence
    flags.homing = true;
    break;
  }
  }
}

bool extractionShouldStop() {
  if (extProfile.isFinished(loopStartTime)) {
    Serial1.println("Extraction Stopped: Finished");
    return true;
  } else if (datas.pressure > 12.5) {
    Serial1.println("Extraction Stopped: Pressure too high");
    return true;
  } else if (datas.motorCurrent > 2.5 && datas.pressure < 2.0) {
    Serial1.println(
        "Extraction Stopped: Motor current too high and pressure too low");
    Serial1.printf("Current: %.2f Pressure: %.2f\n", datas.motorCurrent,
                   datas.pressure);
    return true;
  } else if (datas.position < 5000) {
    Serial1.println("Extraction Stopped: Almost bottom out.");
    return true;
  }
  return false;
}

void executeStop() {
  // Common Extraction Stop Logic
  motor.stop();

  if (flags.inExtraction) {
    // Reset PID and Extraction Profile
    pidController.reset();
    extProfile.reset();
  }

  // Set all the flags.
  flags.inExtraction = false;
  flags.partialExtraction = false;
  flags.inPID = false;
  flags.homing = false;

  // Notify the serial
  serialComm.notifyExtractionStopped();
}

void homeAndZero() {
  motor.setSpeedAccel(-15000);
  // Wait for motor to start moving
  delay(500);
  // Wait for both current and speed = 0
  for (int i = 0; i < 100; ++i) {
    // Check 100 times if motor is stopped
    do {
      pSerial.update();
      pollData();
      Serial1.printf("Current: %.2f, Speed: %d\n", datas.motorCurrent,
                     datas.speed);
      streamData();
    } while (datas.motorCurrent > 0.01);
  }
  // Checked 100 times. Motor should be stopped now.
  motor.stop();
  motor.setPosition(0);
  flags.homing = false;
  delay(100);
}

void pollData() {
  /* First update data. Weight and pressure is always needed */
  datas.pressure = pSensor.readPressure();
  datas.weight = scale.read();
  datas.speed = motor.getSpeed();
  datas.motorCurrent = motor.getCurrent();
  datas.position = motor.getPosition();
}

void streamData() {
  /* Send and update serial */
  serialComm.sendData(datas, true, true, true, true, true, false, true, true,
                      true);
}
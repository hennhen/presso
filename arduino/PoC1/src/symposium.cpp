#include "StructsEnums.h"
#include <Arduino.h>
#include <NAU7802.h>
#include <PacketSerial.h>
#include <SerialCommunicator.h>

#include <ExtractionProfile.h>
#include <HeaterController.h>
#include <PIDController.h>
#include <RoboController.h>

/* Hardware Objects */
#define NAU7802_CALIBRATION_FACTOR 1030.71337
NAU7802 scale(NAU7802_CALIBRATION_FACTOR);

ADSPressureSensor pSensor;
RoboController motor(&Serial2, 115200);

const uint8_t ONE_WIRE_BUS = 4;
const uint8_t HEATER_PIN = 12;
HeaterController heaterController(ONE_WIRE_BUS, HEATER_PIN);

/* Software Objects*/
PIDController pidController(motor, pSensor);
ExtractionProfile extProfile = ExtractionProfile(SINE_WAVE, 500);

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

void onPacketReceived(const uint8_t *buffer, size_t size) {
  Serial1.println("receiced");
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
    // STOP
    flags.inExtraction = false;
    flags.partialExtraction = false;
    flags.inPID = false;
    motor.stop();
    serialComm.notifyExtractionStopped();
    break;
  }
}

void setup() {
  Wire.begin();
  Serial1.begin(250000, SERIAL_8N1, 9, 10);
  Serial1.println("DEBUG TEST PRINT");
  pSerial.begin(250000);
  pSerial.setPacketHandler(&onPacketReceived);

  serialComm.setSendFrequency(50);

  /* Init hardware objects */
  motor.init();
  motor.stop();

  scale.init();
  scale.tare();

  flags.isHeating = true;
  heaterController.setTarget(50);
}

void loop() {
  unsigned long loopStartTime = millis();

  /* First update data. Weight and pressure is always needed */
  datas.pressure = pSensor.readPressure();
  datas.weight = scale.read();

  /* Control Heater if Necessary */
  if (flags.isHeating) {
    heaterController.update();
    datas.temperature = heaterController.read();
  }

  if (flags.inExtraction) {
    unsigned long currentTime = millis();
    /* Can have partial or full extraction*/
    if (flags.partialExtraction) {
      /* Partial extraction logic. No heating/retraction. Directly Start PID */

      /* Check for termination conditions */
      if (extProfile.isFinished(currentTime)) {
        motor.stop();
        flags.inExtraction = false;
        flags.partialExtraction = false;
        flags.inPID = false;
        serialComm.notifyExtractionStopped();
      }
      if (flags.inPID) {
        datas.target = extProfile.getTarget(millis());
        pidController.updateDynamic(datas.target);
        // Serial1.println(datas.target);
      }
    } else {
      // Full extraction logic. Retract and shit
    }
  }

  /* Send and update serial */
  serialComm.sendData(datas, true, true, true, false, true);
  pSerial.update();

  /* Debug Prints */
  //   Serial1.printf("Pressure: %f bars\n", datas.pressure);
  //   Serial1.printf("Weight: %f grams\n", datas.weight);

  /* Loop time printing */
  //   unsigned long loopEndTime = millis();
  //   Serial1.printf("Loop took %lu ms\n", loopEndTime - loopStartTime);
}

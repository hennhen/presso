#ifndef SerialCommunicator_H
#define SerialCommunicator_H

#include "ExtractionProfile.h"
#include "HeaterController.h"
#include "PIDController.h"
#include "RoboController.h"
#include "StructsEnums.h"
#include <PacketSerial.h>
#include <vector>

class SerialCommunicator {
public:
  // Constructor
  SerialCommunicator(PacketSerial &packetSerial, PIDController &pid,
                     ExtractionProfile &profile, RoboController &motor,
                     HeaterController &heater);

  // Public methods
  void sendData(const Datas &datas, bool pressure = false, bool target = false,
                bool weight = false, bool dutyCycle = false,
                bool temperature = false, bool heaterStatus = false,
                bool speed = false, bool position = false,
                bool motorCurrent = false);
  void setSendFrequency(uint8_t frequency);
  void sendErrorMessage(String message);
  void notifyHeaterStatus(bool on);
  void notifyExtractionStarted();
  void notifyExtractionStopped();
  uint8_t receiveCommands(const uint8_t *buffer, size_t size);

private:
  // Private variables
  uint8_t _sendFrequency = 20; // Delay in ms
  unsigned long _lastSendTime = 0;

  PacketSerial &pSerial;
  PIDController &pidController;
  ExtractionProfile &extractionProfile;
  RoboController &motor;
  HeaterController &heater;

  // Private methods
  void sendFloat(short command, float value = 0.0);
  void sendShort(short command, short value);
  PIDController createPIDObject(const std::vector<Datas> &datas);
  ExtractionProfile createExtractionProfile(const std::vector<float> &data);

  // Add other private variables as needed
};

#endif // SERIAL_COMMS_H
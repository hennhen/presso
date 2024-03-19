#ifndef SerialController_H
#define SerialController_H

#include <Arduino.h>
#include <PacketSerial.h>
#include "PressureSensor.h"
#include "CytronController.h"
#include "PIDController.h"
#include "HX711_Scale.h"

class SerialController {
    public:
        bool debug_prints = false;
        SerialController(PacketSerial& packetSerial, CytronController& motor, PressureSensor& sensor, HX711_Scale& scale, PIDController& pidController);

    private:
        PacketSerial& perial;
        CytronController& _motor;
        PressureSensor& _sensor;
        HX711_Scale& _scale;
        PIDController& _pidController;

        uint8_t _sendFrequency = 20; // Delay in ms

        void onPacketReceived(const uint8_t* buffer, size_t size);
        void sendExtractionStopped();
        void sendPressureReading(float _pressure = 0);
        void sendWeightReading(float _weight = 0);
        void sendTargetPressure(float _target_pressure);
        void sendExtractionStopped();